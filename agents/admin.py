from django.contrib import admin
from .models import AgentTask, StudentProfile, BursaryItem, BursaryTracking

@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'agent_type', 'status', 'created_at')
    list_filter = ('status', 'agent_type', 'created_at')
    search_fields = ('prompt', 'response', 'session_id')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'grade', 'province', 'calculated_aps', 'updated_at')
    list_filter = ('grade', 'province')
    search_fields = ('full_name', 'school_name', 'target_career')

@admin.register(BursaryItem)
class BursaryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'minimum_aps', 'deadline_text', 'featured')
    list_filter = ('featured', 'category')
    search_fields = ('name', 'provider', 'eligible_fields')

@admin.register(BursaryTracking)
class BursaryTrackingAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'bursary', 'status', 'updated_at')
    list_filter = ('status', 'has_certified_id', 'has_matric_results', 'has_proof_of_income')
