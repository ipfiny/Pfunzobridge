import json
import asyncio
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

    def test_dashboard_view(self):
        response = self.client.get(reverse('mobile_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PfunzoBridge")
        self.assertContains(response, "Counselor")

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
        self.assertTrue(StudentProfile.objects.filter(session_id=f"user_{user.id}").exists())

    def test_google_auth_api_empty_email(self):
        test_client = Client()
        response = test_client.post(
            reverse('google_auth_api'),
            data=json.dumps({'email': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
