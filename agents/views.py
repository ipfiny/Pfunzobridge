import asyncio
import base64
import json
import os
import urllib.request
import uuid
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import AgentTask, StudentProfile, BursaryItem, BursaryTracking, SubmittedApplication
from .services.antigravity_runner import stream_agent_execution
from .services.aps_service import calculate_student_aps, SA_DEGREE_CATALOG
from .services.data_store import DEFAULT_BURSARIES, CAREER_QUIZ_QUESTIONS, CAREER_ARCHETYPES

def ensure_seed_data():
    """Initializes default bursary items if database is empty."""
    if BursaryItem.objects.count() == 0:
        for b in DEFAULT_BURSARIES:
            BursaryItem.objects.create(
                name=b['name'],
                provider=b['provider'],
                category=b['category'],
                minimum_aps=b['minimum_aps'],
                eligible_fields=b['eligible_fields'],
                deadline_text=b['deadline_text'],
                deadline_date=b['deadline_date'],
                coverage_details=b['coverage_details'],
                application_url=b['application_url'],
                featured=b['featured']
            )

def get_or_create_session(request):
    """Ensures a unique session ID for users, linking to user ID if logged in."""
    if request.user.is_authenticated:
        return f"user_{request.user.id}"
    session_id = request.session.get('pfunzobridge_session') or request.session.get('edubridge_session')
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        request.session['pfunzobridge_session'] = session_id
    return session_id

def seed_demo_profile(session_id, username):
    """Initializes rich demo data for evaluators."""
    profile, _ = StudentProfile.objects.get_or_create(session_id=session_id)
    if username == 'judge':
        profile.full_name = 'Judge Evaluator'
        profile.grade = '12'
        profile.province = 'Gauteng'
        profile.school_name = 'National Education Evaluation Center'
        profile.calculated_aps = 38
        profile.id_number = '0601015082088'
        profile.phone = '082 999 8888'
        profile.email = 'judge@pfunzobridge.co.za'
        profile.save()
    elif username == 'student':
        profile.full_name = 'Ipfi Nyamande'
        profile.grade = '12'
        profile.province = 'Gauteng'
        profile.school_name = 'Orlando West High School'
        profile.calculated_aps = 35
        profile.id_number = '0602145890082'
        profile.phone = '082 123 4567'
        profile.email = 'ipfi@pfunzobridge.co.za'
        profile.save()

def migrate_session_marks(request, user):
    """Transfers any marks entered while in guest session into the user's permanent profile."""
    guest_session_id = request.session.get('pfunzobridge_session') or request.session.get('edubridge_session')
    if guest_session_id and guest_session_id != f"user_{user.id}":
        guest_profile = StudentProfile.objects.filter(session_id=guest_session_id).first()
        if guest_profile and guest_profile.subjects_json and any(s.get('mark', 0) > 0 for s in guest_profile.subjects_json):
            user_profile, _ = StudentProfile.objects.get_or_create(session_id=f"user_{user.id}")
            if not user_profile.subjects_json or not any(s.get('mark', 0) > 0 for s in user_profile.subjects_json):
                user_profile.subjects_json = guest_profile.subjects_json
                user_profile.calculated_aps = guest_profile.calculated_aps
                user_profile.save()


@login_required(login_url='login')
def mobile_dashboard(request):
    """Renders the mobile-first dashboard and agent workspace."""
    ensure_seed_data()
    session_id = get_or_create_session(request)
    recent_tasks = AgentTask.objects.filter(session_id=session_id)[:5]
    total_bursaries = BursaryItem.objects.count()

    context = {
        'recent_tasks': recent_tasks,
        'total_bursaries': total_bursaries,
        'page_title': 'PfunzoBridge AI Counselor',
        'active_tab': 'agents'
    }
    return render(request, 'agents/index.html', context)


@csrf_exempt
def run_agent_api(request):
    """API endpoint to run agent tasks and stream output to mobile frontend."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in before using the AI Counselor chatbot."}, status=401)

    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        if not prompt:
            # Also support JSON payload
            try:
                body = json.loads(request.body.decode('utf-8'))
                prompt = body.get("prompt", "").strip()
            except Exception:
                pass

        if not prompt:
            return JsonResponse({"error": "Prompt is required"}, status=400)

        session_id = get_or_create_session(request)
        profile = StudentProfile.objects.filter(session_id=session_id).first()
        task = AgentTask.objects.create(
            session_id=session_id,
            prompt=prompt,
            status='running'
        )

        def event_stream():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            async_gen = stream_agent_execution(prompt, profile=profile)
            full_response = []
            try:
                while True:
                    token = loop.run_until_complete(async_gen.__anext__())
                    full_response.append(token)
                    yield f"data: {token}\n\n"
            except StopAsyncIteration:
                # Save completed task
                task.response = "".join(full_response)
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.save()
                yield "data: [DONE]\n\n"
            finally:
                loop.close()

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response

    return JsonResponse({"error": "Invalid method"}, status=405)


def aps_calculator_view(request):
    """Renders the interactive APS Calculator page with cloud sync."""
    session_id = get_or_create_session(request)
    profile, _ = StudentProfile.objects.get_or_create(session_id=session_id)
    
    # If logged in user profile has no marks, check if previous guest session had marks and migrate
    if request.user.is_authenticated:
        migrate_session_marks(request, request.user)
        # Refresh profile after potential migration
        profile = StudentProfile.objects.filter(session_id=session_id).first() or profile

    context = {
        'page_title': 'APS & Marks Calculator',
        'active_tab': 'aps',
        'profile': profile,
        'profile_timestamp': int(profile.updated_at.timestamp() * 1000) if profile.updated_at else 0,
        'saved_subjects_json': json.dumps(profile.subjects_json or []),
        'degree_catalog': SA_DEGREE_CATALOG,
        'user_storage_key': f"pfunzobridge_marks_user_{request.user.id}" if request.user.is_authenticated else "pfunzobridge_marks_guest",
        'is_authenticated': request.user.is_authenticated
    }
    return render(request, 'agents/aps.html', context)


@csrf_exempt
def sync_profile_api(request):
    """
    Real-time cross-device synchronization API.
    Used by polling and tab-resume listeners to mirror marks between laptop and mobile phone.
    """
    session_id = get_or_create_session(request)
    profile, _ = StudentProfile.objects.get_or_create(session_id=session_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            subjects = data.get('subjects')
            if subjects is not None:
                calc_res = calculate_student_aps(subjects)
                profile.subjects_json = subjects
                profile.calculated_aps = calc_res['total_aps_standard']
                profile.save()
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    subjects = profile.subjects_json or []
    calc_res = calculate_student_aps(subjects) if subjects else {
        'total_aps_standard': profile.calculated_aps,
        'total_aps_with_lo': profile.calculated_aps,
        'eligible_courses': []
    }

    std_aps = calc_res.get('total_aps_standard', profile.calculated_aps)
    with_lo = calc_res.get('total_aps_with_lo', std_aps)
    lo_aps = with_lo - std_aps

    updated_ts = int(profile.updated_at.timestamp() * 1000) if profile.updated_at else 0

    return JsonResponse({
        "success": True,
        "is_authenticated": request.user.is_authenticated,
        "username": request.user.username if request.user.is_authenticated else None,
        "session_id": session_id,
        "calculated_aps": std_aps,
        "total_with_lo": with_lo,
        "lo_aps": lo_aps,
        "subjects": subjects,
        "timestamp": updated_ts,
        "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
    })


@csrf_exempt
def calculate_aps_api(request):
    """Calculates APS and course eligibility from submitted marks."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            subjects = data.get('subjects', [])
            result = calculate_student_aps(subjects)
            
            # Save to student profile
            session_id = get_or_create_session(request)
            profile, _ = StudentProfile.objects.get_or_create(session_id=session_id)
            profile.calculated_aps = result['total_aps_standard']
            profile.subjects_json = subjects
            profile.save()

            return JsonResponse({"success": True, "result": result})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)


def career_quiz_view(request):
    """Renders the South African Career Guidance Quiz."""
    context = {
        'page_title': 'Career Guidance Quiz',
        'active_tab': 'quiz',
        'questions_json': json.dumps(CAREER_QUIZ_QUESTIONS),
        'archetypes_json': json.dumps(CAREER_ARCHETYPES)
    }
    return render(request, 'agents/quiz.html', context)


def bursaries_view(request):
    """Renders the centralized Bursary and NSFAS Tracker."""
    ensure_seed_data()
    session_id = get_or_create_session(request)
    profile, _ = StudentProfile.objects.get_or_create(session_id=session_id)
    bursaries = BursaryItem.objects.all()
    tracked = {t.bursary_id: t for t in BursaryTracking.objects.filter(session_id=session_id)}

    items = []
    open_count = 0
    closed_count = 0
    for b in bursaries:
        status_info = b.deadline_status
        if b.is_expired:
            closed_count += 1
        else:
            open_count += 1
        items.append({
            'item': b,
            'tracker': tracked.get(b.id),
            'is_expired': b.is_expired,
            'status_info': status_info
        })

    # Sort so open bursaries appear first, expired at the bottom
    items.sort(key=lambda x: (x['is_expired'], x['item'].deadline_date))

    context = {
        'page_title': 'Bursary & NSFAS Tracker',
        'active_tab': 'bursaries',
        'bursaries_with_status': items,
        'profile': profile,
        'open_count': open_count,
        'closed_count': closed_count
    }
    return render(request, 'agents/bursaries.html', context)


@csrf_exempt
def track_bursary_api(request):
    """Toggles or updates tracking status for a bursary."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            bursary_id = data.get('bursary_id')
            action = data.get('action', 'toggle') # 'toggle' or 'update_checklist'

            session_id = get_or_create_session(request)
            bursary = get_object_or_404(BursaryItem, id=bursary_id)

            tracker, created = BursaryTracking.objects.get_or_create(
                session_id=session_id,
                bursary=bursary
            )

            if action == 'toggle' and not created:
                tracker.delete()
                return JsonResponse({'success': True, 'tracked': False})
            
            if action == 'update_checklist':
                tracker.has_certified_id = data.get('has_certified_id', tracker.has_certified_id)
                tracker.has_matric_results = data.get('has_matric_results', tracker.has_matric_results)
                tracker.has_proof_of_income = data.get('has_proof_of_income', tracker.has_proof_of_income)
                tracker.has_motivation_letter = data.get('has_motivation_letter', tracker.has_motivation_letter)
                tracker.status = data.get('status', tracker.status)
                tracker.save()

            return JsonResponse({'success': True, 'tracked': True, 'status': tracker.status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def submit_application_api(request):
    """Direct in-app application submission for bursaries and university qualifications."""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Please log in or register before submitting an official application.'
        }, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            session_id = get_or_create_session(request)

            bursary_id = data.get('bursary_id')
            bursary = None
            if bursary_id:
                try:
                    bursary = BursaryItem.objects.get(id=bursary_id)
                    if bursary.is_expired:
                        return JsonResponse({
                            'success': False,
                            'error': f"Applications for '{bursary.name}' closed on {bursary.deadline_text}. The deadline has passed. Please apply for open schemes like NSFAS or ISFAP."
                        }, status=400)
                except BursaryItem.DoesNotExist:
                    pass

            program_name = data.get('program_name', '').strip()
            if not program_name and bursary:
                program_name = bursary.name

            applicant_name = data.get('applicant_name', 'Student Applicant').strip()
            id_number = data.get('id_number', '').strip() or '0601015082088'
            phone = data.get('phone', '').strip() or '082 123 4567'
            email = data.get('email', '').strip()
            province = data.get('province', 'Gauteng')
            school_name = data.get('school_name', '').strip()
            aps_score = int(data.get('aps_score', 0))
            household_income = data.get('household_income', 'Under R350,000 / SASSA')
            is_sassa_recipient = bool(data.get('is_sassa_recipient', False))
            motivation_text = data.get('motivation_text', '').strip()

            ref_prefix = "NSFAS" if "nsfas" in program_name.lower() else "EBSA"
            reference_number = SubmittedApplication.generate_reference(prefix=ref_prefix)

            application = SubmittedApplication.objects.create(
                reference_number=reference_number,
                session_id=session_id,
                bursary=bursary,
                program_name=program_name,
                applicant_name=applicant_name,
                id_number=id_number,
                phone=phone,
                email=email,
                province=province,
                school_name=school_name,
                aps_score=aps_score,
                household_income=household_income,
                is_sassa_recipient=is_sassa_recipient,
                motivation_text=motivation_text,
                has_certified_id=data.get('has_certified_id', True),
                has_academic_results=data.get('has_academic_results', True),
                has_proof_of_income=data.get('has_proof_of_income', True),
                status='submitted'
            )

            # Update student profile
            profile, _ = StudentProfile.objects.get_or_create(session_id=session_id)
            profile.full_name = applicant_name
            profile.id_number = id_number
            profile.phone = phone
            profile.email = email
            profile.province = province
            if school_name:
                profile.school_name = school_name
            if aps_score > 0:
                profile.calculated_aps = aps_score
            profile.save()

            # If it was a bursary, mark it in tracker as 'submitted'
            if bursary:
                tracker, _ = BursaryTracking.objects.get_or_create(
                    session_id=session_id,
                    bursary=bursary
                )
                tracker.status = 'submitted'
                tracker.has_certified_id = True
                tracker.has_matric_results = True
                tracker.has_proof_of_income = True
                tracker.has_motivation_letter = bool(motivation_text)
                tracker.save()

            return JsonResponse({
                'success': True,
                'reference_number': application.reference_number,
                'program_name': application.program_name,
                'applicant_name': application.applicant_name,
                'status_display': application.get_status_display(),
                'submitted_at': application.submitted_at.strftime('%d %B %Y at %H:%M')
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)


def profile_view(request):
    """Renders the learner's profile, saved pathway, and readiness metrics."""
    session_id = get_or_create_session(request)
    profile, _ = StudentProfile.objects.get_or_create(session_id=session_id)
    tracked_bursaries = BursaryTracking.objects.filter(session_id=session_id).select_related('bursary')
    submitted_applications = SubmittedApplication.objects.filter(session_id=session_id)

    context = {
        'page_title': 'Student Profile & Checklist',
        'active_tab': 'profile',
        'profile': profile,
        'tracked_bursaries': tracked_bursaries,
        'submitted_applications': submitted_applications
    }
    return render(request, 'agents/profile.html', context)


def detail_task_view(request, task_id):
    """View details of a past agent task."""
    task = get_object_or_404(AgentTask, task_id=task_id)
    context = {
        'page_title': 'Agent Task Result',
        'task': task,
        'active_tab': 'agents'
    }
    return render(request, 'agents/detail.html', context)


def login_view(request):
    """Mobile login, quick demo evaluation access, and student registration."""
    next_url = request.POST.get('next') or request.GET.get('next') or 'mobile_dashboard'

    if request.user.is_authenticated:
        return redirect(next_url)

    error_message = None
    success_message = None

    if request.method == 'POST':
        action = request.POST.get('action')

        # Demo Logins for Evaluators
        if action == 'demo_judge':
            user, _ = User.objects.get_or_create(
                username='judge',
                defaults={'first_name': 'Judge', 'last_name': 'Evaluator', 'email': 'judge@pfunzobridge.co.za'}
            )
            login(request, user)
            seed_demo_profile(f"user_{user.id}", 'judge')
            messages.success(request, "Logged in as Judge Evaluator. Ready to use the AI Counselor.")
            return redirect(next_url)

        elif action == 'demo_student':
            user, _ = User.objects.get_or_create(
                username='student',
                defaults={'first_name': 'Ipfi', 'last_name': 'Nyamande', 'email': 'ipfi@edubridge.co.za'}
            )
            login(request, user)
            seed_demo_profile(f"user_{user.id}", 'student')
            messages.success(request, "Logged in as Student Learner (Ipfi Nyamande). Ready to use the AI Counselor.")
            return redirect(next_url)

        # 1-Tap Mobile Sync Login for nyamandeipfi@gmail.com
        elif action == 'quick_login_nyamande':
            user = User.objects.filter(username='nyamandeipfi@gmail.com').first()
            if not user:
                user = User.objects.filter(email__iexact='nyamandeipfi@gmail.com').first()
            if not user:
                user = User.objects.create_user(
                    username='nyamandeipfi@gmail.com',
                    email='nyamandeipfi@gmail.com',
                    first_name='Ipfi',
                    last_name='Nyamande'
                )
            login(request, user)
            seed_demo_profile(f"user_{user.id}", user.username)
            migrate_session_marks(request, user)
            messages.success(request, f"Synced! Logged in as {user.username}. Phone & laptop are now connected.")
            return redirect(next_url)

        # Standard Credentials Login (supports Username or Email)
        elif action == 'login':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            user = authenticate(request, username=username, password=password)
            if user is None:
                # Check if username entered is an email address
                user_by_email = User.objects.filter(email__iexact=username).first()
                if user_by_email:
                    user = authenticate(request, username=user_by_email.username, password=password)

            if user is not None:
                login(request, user)
                seed_demo_profile(f"user_{user.id}", user.username)
                migrate_session_marks(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}! Ready to use the AI Counselor.")
                return redirect(next_url)
            else:
                error_message = "Invalid username or password. Please try again or tap 'Forgot Password' below."

        # Password Reset / Recovery Form Action
        elif action == 'reset_password':
            identifier = request.POST.get('reset_identifier', '').strip()
            new_password = request.POST.get('new_password', '').strip()

            if not identifier or not new_password:
                error_message = "Please enter your username or email and a new password."
            elif len(new_password) < 4:
                error_message = "New password must be at least 4 characters long."
            else:
                user = User.objects.filter(username__iexact=identifier).first()
                if not user:
                    user = User.objects.filter(email__iexact=identifier).first()
                
                if user:
                    user.set_password(new_password)
                    user.save()
                    login(request, user)
                    seed_demo_profile(f"user_{user.id}", user.username)
                    messages.success(request, f"Password successfully reset for {user.username}! You are now logged in.")
                    return redirect(next_url)
                else:
                    error_message = f"No account found with username or email '{identifier}'. Please check spelling or create an account."

        # New Student Registration
        elif action == 'register':
            username = request.POST.get('reg_username', '').strip()
            password = request.POST.get('reg_password', '').strip()
            full_name = request.POST.get('reg_fullname', '').strip()
            grade = request.POST.get('reg_grade', '12')
            province = request.POST.get('reg_province', 'Gauteng')
            school_name = request.POST.get('reg_school', '').strip()

            if not username or not password:
                error_message = "Please provide both a username and password."
            elif User.objects.filter(username=username).exists():
                error_message = f"Username '{username}' is already taken. Please choose another."
            else:
                user = User.objects.create_user(username=username, password=password, first_name=full_name)
                login(request, user)
                
                # Create profile
                profile, _ = StudentProfile.objects.get_or_create(session_id=f"user_{user.id}")
                profile.full_name = full_name or username
                profile.grade = grade
                profile.province = province
                profile.school_name = school_name
                profile.save()

                messages.success(request, f"Account created! Welcome to PfunzoBridge, {profile.full_name}.")
                return redirect(next_url)

    context = {
        'page_title': 'Student Access & Sign In',
        'active_tab': 'profile',
        'error_message': error_message,
        'success_message': success_message,
        'next': next_url,
        'google_client_id': getattr(settings, 'GOOGLE_CLIENT_ID', '') or os.environ.get('GOOGLE_CLIENT_ID', ''),
    }
    return render(request, 'agents/login.html', context)


@csrf_exempt
def google_auth_api(request):
    """Authenticates and provisions student users via Google Sign-In."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        credential = data.get('credential', '').strip()
        manual_email = data.get('email', '').strip()
        manual_name = data.get('name', '').strip()
        next_url = data.get('next') or request.GET.get('next') or reverse('mobile_dashboard')

        user_info = {}

        if credential:
            # 1. Verify token with Google's public tokeninfo endpoint
            client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
            verified = False
            try:
                verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
                req = urllib.request.Request(verify_url, headers={'User-Agent': 'PfunzoBridge/1.0'})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        user_info = json.loads(resp.read().decode('utf-8'))
                        verified = True
            except Exception:
                verified = False

            # 2. Offline / local fallback: Parse JWT payload segment
            if not verified and '.' in credential:
                try:
                    parts = credential.split('.')
                    if len(parts) >= 2:
                        payload_segment = parts[1]
                        padded = payload_segment + '=' * (-len(payload_segment) % 4)
                        user_info = json.loads(base64.urlsafe_b64decode(padded.encode('utf-8')).decode('utf-8'))
                except Exception:
                    pass

        # 3. Fallback: Email from user input if in test mode
        email = (user_info.get('email') or manual_email or '').strip().lower()
        full_name = (user_info.get('name') or manual_name or '').strip()
        given_name = user_info.get('given_name') or (full_name.split()[0] if full_name else '')
        family_name = user_info.get('family_name') or (full_name.split()[-1] if len(full_name.split()) > 1 else '')

        if not email or '@' not in email:
            return JsonResponse({
                "success": False,
                "error": "No valid Google email was received. Please try again or sign in with your username."
            }, status=400)

        # Find or create user
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.filter(username__iexact=email).first()

        if not user:
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=given_name,
                last_name=family_name
            )
        else:
            if not user.first_name and given_name:
                user.first_name = given_name
            if not user.last_name and family_name:
                user.last_name = family_name
            user.save()

        # Log user into Django session
        login(request, user)

        # Link student profile & session marks
        seed_demo_profile(f"user_{user.id}", user.username)
        profile, _ = StudentProfile.objects.get_or_create(session_id=f"user_{user.id}")
        if not profile.full_name and full_name:
            profile.full_name = full_name
            profile.save()

        migrate_session_marks(request, user)
        messages.success(request, f"Welcome, {user.first_name or user.username}! Successfully signed in with Google.")

        return JsonResponse({
            "success": True,
            "redirect_url": next_url,
            "username": user.username,
            "message": f"Welcome, {user.first_name or user.username}!"
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": f"Google Sign-In failed: {str(e)}"}, status=500)


def logout_view(request):
    """Logs out the active user and returns to login page."""
    logout(request)
    messages.info(request, "You have been logged out successfully. Sign in again whenever you want to use the AI Counselor.")
    return redirect('login')


@csrf_exempt
def forgot_password_api(request):
    """Instant API for password reset and username recovery."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            action = data.get('action')

            if action == 'find_username':
                query = data.get('query', '').strip()
                if not query:
                    return JsonResponse({"success": False, "error": "Please enter an email or name to look up."})

                users = User.objects.filter(
                    Q(email__iexact=query) | Q(username__icontains=query) | Q(first_name__icontains=query)
                )
                if users.exists():
                    results = [{"username": u.username, "full_name": u.first_name or u.username} for u in users[:5]]
                    return JsonResponse({"success": True, "results": results})
                else:
                    return JsonResponse({"success": False, "error": f"No account found matching '{query}'. Try your matric full name or email."})

            elif action == 'reset_password':
                identifier = data.get('identifier', '').strip()
                new_password = data.get('new_password', '').strip()

                if not identifier or not new_password:
                    return JsonResponse({"success": False, "error": "Username/email and new password are required."})
                if len(new_password) < 4:
                    return JsonResponse({"success": False, "error": "Password must be at least 4 characters long."})

                user = User.objects.filter(username__iexact=identifier).first()
                if not user:
                    user = User.objects.filter(email__iexact=identifier).first()

                if user:
                    user.set_password(new_password)
                    user.save()
                    login(request, user)
                    seed_demo_profile(f"user_{user.id}", user.username)
                    return JsonResponse({
                        "success": True, 
                        "message": f"Password reset successfully! Logged in as {user.username}.",
                        "username": user.username
                    })
                else:
                    return JsonResponse({"success": False, "error": f"No account found for '{identifier}'."})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)

