from django.urls import path
from . import views

urlpatterns = [
    # Mobile Dashboard & Agent
    path('', views.mobile_dashboard, name='mobile_dashboard'),
    path('agents/', views.mobile_dashboard, name='agents_index'),
    path('run-agent-api/', views.run_agent_api, name='run_agent_api'),
    path('task/<uuid:task_id>/', views.detail_task_view, name='task_detail'),
    
    # APS Calculator
    path('aps/', views.aps_calculator_view, name='aps_calculator'),
    path('api/calculate-aps/', views.calculate_aps_api, name='calculate_aps_api'),
    path('api/sync-profile/', views.sync_profile_api, name='sync_profile_api'),

    # Career Guidance Quiz
    path('quiz/', views.career_quiz_view, name='career_quiz'),

    # Centralized Bursaries & NSFAS
    path('bursaries/', views.bursaries_view, name='bursaries_index'),
    path('api/track-bursary/', views.track_bursary_api, name='track_bursary_api'),
    path('api/submit-application/', views.submit_application_api, name='submit_application_api'),

    # Student Profile & Authentication
    path('profile/', views.profile_view, name='student_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/auth/google/', views.google_auth_api, name='google_auth_api'),
    path('api/forgot-password/', views.forgot_password_api, name='forgot_password_api'),
]
