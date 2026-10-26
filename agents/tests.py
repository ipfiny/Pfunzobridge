import json
import asyncio
from datetime import timedelta
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from agents.models import AgentTask, BursaryItem, StudentProfile, BursaryTracking
from agents.services.aps_service import calculate_student_aps, percentage_to_aps_level
from agents.services.antigravity_runner import stream_agent_execution

class ApsServiceTests(TestCase):
    def test_aps_level_mapping(self):
        self.assertEqual(percentage_to_aps_level(85), 7)
        self.assertEqual(percentage_to_aps_level(72), 6)
        self.assertEqual(percentage_to_aps_level(65), 5)
        self.assertEqual(percentage_to_aps_level(55), 4)
        self.assertEqual(percentage_to_aps_level(45), 3)
        self.assertEqual(percentage_to_aps_level(35), 2)
        self.assertEqual(percentage_to_aps_level(20), 1)

    def test_calculate_student_aps(self):
        subjects = [
            {"name": "English HL", "mark": 80, "is_lo": False},       # 7
            {"name": "Mathematics", "mark": 75, "is_lo": False},      # 6
            {"name": "Life Orientation", "mark": 85, "is_lo": True},   # 7 (excluded from standard)
            {"name": "Physical Sciences", "mark": 70, "is_lo": False}, # 6
            {"name": "Life Sciences", "mark": 65, "is_lo": False},     # 5
            {"name": "Geography", "mark": 60, "is_lo": False},         # 5
            {"name": "IsiZulu", "mark": 70, "is_lo": False},           # 6
        ]
        # Standard APS: top 6 non-LO = 7 + 6 + 6 + 6 + 5 + 5 = 35
        # With LO: 35 + 7 = 42
        result = calculate_student_aps(subjects)
        self.assertEqual(result["total_aps_standard"], 35)
        self.assertEqual(result["total_aps_with_lo"], 42)
        self.assertGreater(len(result["eligible_courses"]), 0)


class AntigravityRunnerTests(TestCase):
    def test_streaming_generator(self):
        async def run_test():
            tokens = []
            async for token in stream_agent_execution("What is NSFAS funding?"):
                tokens.append(token)
            return "".join(tokens)

        full_output = asyncio.run(run_test())
        self.assertTrue(len(full_output) > 20)
        self.assertIn("NSFAS", full_output)


class MobileViewEndpointsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='teststudent', password='password123')
        self.client.force_login(self.user)

    def test_dashboard_requires_login(self):
        unauthed_client = Client()
        response = unauthed_client.get(reverse('mobile_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_login_view_renders_successfully(self):
        unauthed_client = Client()
        response = unauthed_client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PfunzoBridge Access")
        self.assertContains(response, "Sign in with Google")

    def test_dashboard_view(self):
        response = self.client.get(reverse('mobile_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PfunzoBridge")
        self.assertContains(response, "PfunzoAI")

    def test_aps_view(self):
        response = self.client.get(reverse('aps_calculator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "APS &amp; Marks Calculator")

    def test_aps_api_calculation(self):
        payload = {
            "subjects": [
                {"name": "English", "mark": 75, "is_lo": False},
                {"name": "Mathematics", "mark": 70, "is_lo": False},
                {"name": "Life Orientation", "mark": 80, "is_lo": True},
                {"name": "Physical Sciences", "mark": 65, "is_lo": False},
                {"name": "Life Sciences", "mark": 60, "is_lo": False},
                {"name": "Accounting", "mark": 55, "is_lo": False},
                {"name": "History", "mark": 50, "is_lo": False}
            ]
        }
        response = self.client.post(
            reverse('calculate_aps_api'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("total_aps_standard", data["result"])

    def test_quiz_view(self):
        response = self.client.get(reverse('career_quiz'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Career Guidance Quiz")

    def test_bursaries_view(self):
        response = self.client.get(reverse('bursaries_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bursary &amp; NSFAS Tracker")

    def test_run_agent_api(self):
        response = self.client.post(reverse('run_agent_api'), data={'prompt': 'Tell me about APS scores'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')
        # Check task was created
        self.assertTrue(AgentTask.objects.filter(prompt='Tell me about APS scores').exists())

    def test_profile_view(self):
        response = self.client.get(reverse('student_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Profile")

    def test_privacy_policy_view(self):
        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "POPIA Act 4 of 2013 Compliant")
        self.assertContains(response, "Ask for Permission First")
        self.assertContains(response, "Collect Only What We Need")
        self.assertContains(response, "Keep Data Safe &amp; Secure")
        self.assertContains(response, "Give You Complete Control")
        self.assertContains(response, "privacy@pfunzobridge.co.za")

    def test_apply_now_requires_login(self):
        unauthed_client = Client()
        response = unauthed_client.post(
            reverse('submit_application_api'),
            data=json.dumps({'bursary_id': 1}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()['success'])

    def test_google_auth_api_fallback(self):
        test_client = Client()
        payload = {
            'email': 'sipho.google@example.com',
            'name': 'Sipho Khumalo'
        }
        response = test_client.post(
            reverse('google_auth_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(User.objects.filter(email='sipho.google@example.com').exists())
        user = User.objects.get(email='sipho.google@example.com')
        self.assertEqual(user.first_name, 'Sipho')
        self.assertEqual(user.last_name, 'Khumalo')
        profile = StudentProfile.objects.get(session_id=f"user_{user.id}")
        self.assertFalse(profile.is_onboarded)
        self.assertIn(reverse('complete_profile'), data['redirect_url'])

    def test_google_auth_api_without_name(self):
        test_client = Client()
        payload = {
            'email': 'lerato.moloi@example.com'
        }
        response = test_client.post(
            reverse('google_auth_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        user = User.objects.get(email='lerato.moloi@example.com')
        self.assertEqual(user.first_name, 'Lerato')
        self.assertEqual(user.last_name, 'Moloi')

    def test_google_auth_api_empty_email(self):
        test_client = Client()
        response = test_client.post(
            reverse('google_auth_api'),
            data=json.dumps({'email': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_google_auth_api_second_login_redirects_to_root(self):
        # User already exists and is onboarded
        user = User.objects.create_user(username='returningstudent', email='returning@example.com')
        profile, _ = StudentProfile.objects.get_or_create(session_id=f"user_{user.id}")
        profile.is_onboarded = True
        profile.school_name = "Pretoria Boys High"
        profile.save()

        test_client = Client()
        payload = {
            'email': 'returning@example.com',
            'name': 'Returning Student',
            'next': 'mobile_dashboard'
        }
        response = test_client.post(
            reverse('google_auth_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        # Must land on profile screen
        self.assertEqual(data['redirect_url'], reverse('student_profile'))
        self.assertNotIn('login/mobile_dashboard', data['redirect_url'])

    def test_complete_profile_flow(self):
        user = User.objects.create_user(username='newgoogleuser', email='newgoogle@example.com')
        client = Client()
        client.force_login(user)

        # GET complete profile form
        get_res = client.get(reverse('complete_profile'))
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, "Complete Your Student Profile")
        self.assertContains(get_res, "newgoogle@example.com")

        # POST profile completion
        post_res = client.post(reverse('complete_profile'), data={
            'full_name': 'Sipho Dlamini',
            'grade': '12',
            'province': 'Limpopo',
            'school_name': 'Mbilwi Secondary School',
            'target_career': 'Mechatronics Engineering'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertEqual(post_res.url, reverse('student_profile'))
        profile = StudentProfile.objects.get(session_id=f"user_{user.id}")
        self.assertTrue(profile.is_onboarded)
        self.assertEqual(profile.school_name, 'Mbilwi Secondary School')
        self.assertEqual(profile.province, 'Limpopo')
        self.assertEqual(profile.target_career, 'Mechatronics Engineering')

    def test_direct_google_sign_in_action_without_email_does_not_default(self):
        test_client = Client()
        response = test_client.get(reverse('login') + '?action=google')
        self.assertEqual(response.status_code, 302)
        self.assertIn('show_google_modal=1', response.url)
        # Ensure NO personal default user is created
        self.assertFalse(User.objects.filter(email='nyamandeipfi@gmail.com').exists())

    def test_direct_google_sign_in_action_with_user_email(self):
        test_client = Client()
        response = test_client.get(reverse('login') + '?action=google&email=learner@example.com&name=Thabo+Mokoena')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='learner@example.com').exists())
        user = User.objects.get(email='learner@example.com')
        self.assertEqual(user.first_name, 'Thabo')
        self.assertEqual(user.last_name, 'Mokoena')
        self.assertIn(reverse('complete_profile'), response.url)

    def test_deadline_badge_colors(self):
        today = timezone.localdate()

        # 1. Past deadline -> Red badge
        past_bursary = BursaryItem.objects.create(
            name="Past Scheme",
            provider="Past Provider",
            deadline_date=today - timedelta(days=5),
            deadline_text="5 Days Ago"
        )
        status_past = past_bursary.deadline_status
        self.assertEqual(status_past['color'], 'red')
        self.assertIn('bg-red-950', status_past['badge_class'])
        self.assertIn('text-red-300', status_past['badge_class'])
        self.assertIn('border-red-800', status_past['badge_class'])

        # 2. Upcoming deadline (within 30 days) -> Amber badge
        upcoming_bursary = BursaryItem.objects.create(
            name="Upcoming Scheme",
            provider="Upcoming Provider",
            deadline_date=today + timedelta(days=12),
            deadline_text="In 12 Days"
        )
        status_upcoming = upcoming_bursary.deadline_status
        self.assertEqual(status_upcoming['color'], 'amber')
        self.assertIn('bg-amber-950', status_upcoming['badge_class'])
        self.assertIn('text-amber-300', status_upcoming['badge_class'])
        self.assertIn('border-amber-800', status_upcoming['badge_class'])

        # 3. Far future deadline (> 30 days away) -> Green badge
        future_bursary = BursaryItem.objects.create(
            name="Future Scheme",
            provider="Future Provider",
            deadline_date=today + timedelta(days=90),
            deadline_text="In 3 Months"
        )
        status_future = future_bursary.deadline_status
        self.assertEqual(status_future['color'], 'green')
        self.assertIn('bg-emerald-950', status_future['badge_class'])
        self.assertIn('text-emerald-300', status_future['badge_class'])
        self.assertIn('border-emerald-800', status_future['badge_class'])

        # 4. View renders the deadline badges
        response = self.client.get(reverse('bursaries_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Deadline: 5 Days Ago')
        self.assertContains(response, 'Deadline: In 12 Days')
        self.assertContains(response, 'Deadline: In 3 Months')
        self.assertContains(response, 'border-red-800')
        self.assertContains(response, 'border-amber-800')
        self.assertContains(response, 'border-emerald-800')

    def test_terms_of_use_view(self):
        """Tests the Terms of Use educational agreement view."""
        response = self.client.get(reverse('terms_of_use'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Terms of Use &amp; Learner Agreement")
        self.assertContains(response, "POPIA Act 4 of 2013")
        self.assertContains(response, "Educational Purpose &amp; Free Access")

    def test_guest_profile_hides_private_sections(self):
        """Ensures logged out/guest learners do not see grade, province, stats, checklist, or applications."""
        unauthed_client = Client()
        response = unauthed_client.get(reverse('student_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guest Learner")
        self.assertNotContains(response, "Computed APS")
        self.assertNotContains(response, "My Submitted Applications")
        self.assertNotContains(response, "Matriculant Readiness Checklist")
        self.assertNotContains(response, "Bookmarked Opportunities")
        # FAB should not be visible to logged out users
        self.assertNotContains(response, "title=\"Open PfunzoAI\"")

    def test_authenticated_profile_checklist_and_dynamic_verbs(self):
        """Tests checklist dynamic checkmarks and verbs for authenticated users."""
        profile, _ = StudentProfile.objects.get_or_create(session_id=f"user_{self.user.id}")
        profile.calculated_aps = 0
        profile.target_career = ""
        profile.save()

        # Check before completing steps: should show Calculate and Take Quiz
        response = self.client.get(reverse('student_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Computed APS")
        self.assertContains(response, "Matriculant Readiness Checklist")
        self.assertContains(response, "APS Calculated (Not yet)")
        self.assertContains(response, "Calculate</a>")
        self.assertContains(response, "Career Archetype Identified (Not yet)")
        self.assertContains(response, "Take Quiz</a>")
        self.assertContains(response, "Applications Submitted (0)")
        self.assertContains(response, "Apply Now</a>")

        # Now complete APS and Career Quiz
        profile.calculated_aps = 35
        profile.target_career = "Technologist & Builder"
        profile.save()

        response = self.client.get(reverse('student_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "APS Calculated (35 Points)")
        self.assertContains(response, "Recalculate</a>")
        self.assertContains(response, "Career Archetype Identified (Technologist &amp; Builder)")
        self.assertContains(response, "Retake Quiz</a>")

    def test_download_user_data_pdf(self):
        """Tests POPIA personal data subject access report PDF generation."""
        response = self.client.get(reverse('download_user_data_pdf'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="pfunzobridge_data_', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF-'))

    def test_delete_account_view(self):
        """Tests permanent account and personal data erasure under POPIA Section 24."""
        temp_user = User.objects.create_user(username='delstudent', password='password123')
        StudentProfile.objects.create(session_id=f"user_{temp_user.id}", full_name="Delete Me")
        temp_client = Client()
        temp_client.login(username='delstudent', password='password123')

        response = temp_client.post(reverse('delete_account'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='delstudent').exists())
        self.assertFalse(StudentProfile.objects.filter(session_id=f"user_{temp_user.id}").exists())

    def test_save_career_archetype_api(self):
        """Tests API endpoint to save career archetype from quiz."""
        payload = {"archetype_title": "Healthcare & Social Worker"}
        response = self.client.post(
            reverse('save_career_archetype_api'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        profile = StudentProfile.objects.get(session_id=f"user_{self.user.id}")
        self.assertEqual(profile.target_career, "Healthcare & Social Worker")
