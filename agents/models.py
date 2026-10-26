import uuid
import random
from django.db import models

class AgentTask(models.Model):
    """Logs autonomous agent prompts, thoughts, and outputs."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    task_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    session_id = models.CharField(max_length=128, default='guest-mobile-session')
    prompt = models.TextField()
    response = models.TextField(blank=True, default='')
    agent_type = models.CharField(max_length=64, default='Antigravity SA Counselor')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Task {self.task_id} ({self.status}) - {self.prompt[:40]}"


class StudentProfile(models.Model):
    """Stores high school learner profile & computed APS metrics."""
    GRADE_CHOICES = [
        ('10', 'Grade 10'),
        ('11', 'Grade 11'),
        ('12', 'Grade 12 / Matric'),
        ('matriculant', 'Matric Passed / Gap Year'),
        ('tvet', 'TVET Applicant'),
    ]

    session_id = models.CharField(max_length=128, unique=True)
    full_name = models.CharField(max_length=120, default='Student Learner')
    id_number = models.CharField(max_length=20, blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='12')
    province = models.CharField(max_length=60, default='Gauteng')
    school_name = models.CharField(max_length=180, blank=True, default='')
    calculated_aps = models.IntegerField(default=0)
    target_career = models.CharField(max_length=180, blank=True, default='')
    subjects_json = models.JSONField(default=list, blank=True)
    is_onboarded = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.grade}) - APS: {self.calculated_aps}"


class BursaryItem(models.Model):
    """Catalog of South African tertiary bursaries and funding schemes."""
    name = models.CharField(max_length=180)
    provider = models.CharField(max_length=180)
    category = models.CharField(max_length=60, default='General Tertiary')
    minimum_aps = models.IntegerField(default=25)
    eligible_fields = models.CharField(max_length=255, default='All Fields / STEM')
    deadline_date = models.DateField(null=True, blank=True)
    deadline_text = models.CharField(max_length=100, default='Annually 31 January')
    coverage_details = models.TextField(default='Tuition, Accommodation, Books, Monthly Stipend')
    application_url = models.URLField(max_length=300, blank=True)
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['deadline_date', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider})"

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.deadline_date:
            return self.deadline_date < timezone.localdate()
        return False

    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.deadline_date:
            delta = (self.deadline_date - timezone.localdate()).days
            return delta
        return None

    @property
    def deadline_status(self):
        """Returns structured deadline status: Green (far future >30d), Amber (upcoming <=30d), Red (passed <0d)."""
        from django.utils import timezone
        if not self.deadline_date:
            return {
                'code': 'future',
                'color': 'green',
                'label': f"Deadline: {self.deadline_text}",
                'badge_class': 'bg-emerald-950 text-emerald-300 border-emerald-800'
            }
        
        diff = (self.deadline_date - timezone.localdate()).days
        if diff < 0:
            return {
                'code': 'expired',
                'color': 'red',
                'label': f"Deadline: {self.deadline_text}",
                'badge_class': 'bg-red-950 text-red-300 border-red-800'
            }
        elif diff <= 30:
            return {
                'code': 'upcoming',
                'color': 'amber',
                'label': f"Deadline: {self.deadline_text}",
                'badge_class': 'bg-amber-950 text-amber-300 border-amber-800'
            }
        else:
            return {
                'code': 'future',
                'color': 'green',
                'label': f"Deadline: {self.deadline_text}",
                'badge_class': 'bg-emerald-950 text-emerald-300 border-emerald-800'
            }


class BursaryTracking(models.Model):
    """Tracks a learner's saved or applied bursaries and document checklist."""
    STATUS_CHOICES = [
        ('saved', 'Saved to Checklist'),
        ('docs_gathering', 'Gathering Documents'),
        ('submitted', 'Application Submitted'),
        ('accepted', 'Approved / Funded'),
    ]

    session_id = models.CharField(max_length=128)
    bursary = models.ForeignKey(BursaryItem, on_delete=models.CASCADE, related_name='trackers')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='saved')
    notes = models.TextField(blank=True, default='')
    has_certified_id = models.BooleanField(default=False)
    has_matric_results = models.BooleanField(default=False)
    has_proof_of_income = models.BooleanField(default=False)
    has_motivation_letter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('session_id', 'bursary')

    def __str__(self):
        return f"{self.session_id} -> {self.bursary.name} [{self.status}]"


class SubmittedApplication(models.Model):
    """Stores in-app completed applications for bursaries or university programmes."""
    STATUS_CHOICES = [
        ('submitted', 'Submitted - Verification in Progress'),
        ('documents_verified', 'Documents Verified'),
        ('shortlisted', 'Shortlisted by Selection Committee'),
        ('approved', 'Approved & Funded'),
    ]

    reference_number = models.CharField(max_length=64, unique=True)
    session_id = models.CharField(max_length=128)
    bursary = models.ForeignKey(BursaryItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    program_name = models.CharField(max_length=200, default='General Tertiary Funding')
    applicant_name = models.CharField(max_length=120)
    id_number = models.CharField(max_length=20)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, default='')
    province = models.CharField(max_length=60, default='Gauteng')
    school_name = models.CharField(max_length=180, blank=True, default='')
    aps_score = models.IntegerField(default=0)
    household_income = models.CharField(max_length=80, default='Under R350,000 / SASSA')
    is_sassa_recipient = models.BooleanField(default=False)
    motivation_text = models.TextField(blank=True, default='')
    has_certified_id = models.BooleanField(default=True)
    has_academic_results = models.BooleanField(default=True)
    has_proof_of_income = models.BooleanField(default=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.reference_number} - {self.applicant_name} ({self.program_name})"

    @classmethod
    def generate_reference(cls, prefix="EBSA"):
        """Generates an official South African student application reference."""
        num = random.randint(100000, 999999)
        return f"{prefix}-2026-{num}"
