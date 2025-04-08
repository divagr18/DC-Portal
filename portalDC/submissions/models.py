# submissions/models.py
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import os
# Optional: Define a validator for file extensions if needed more broadly
# from django.core.exceptions import ValidationError
# def validate_pdf(value):
#     ext = os.path.splitext(value.name)[1] # [0] returns path+filename
#     valid_extensions = ['.pdf']
#     if not ext.lower() in valid_extensions:
#         raise ValidationError('Unsupported file extension. Only PDF files are allowed.')
def submission_upload_path(instance, filename):
    # Get student name from the model instance
    student_name = instance.student_name
    # Create a safe directory name from the student name
    # Replaces spaces with hyphens, removes unsafe chars, converts to lowercase
    safe_student_name = slugify(student_name) if student_name else 'unknown_student'
    # Construct the path: submissions/<safe_student_name>/<original_filename>
    # os.path.join handles path separators correctly
    return os.path.join('submissions', safe_student_name, filename)
class Submission(models.Model):
    # AutoField provides the automatic unique submission ID (pk)
    student_name = models.CharField(max_length=100)
    # FileField handles file uploads. `upload_to` specifies a subdirectory within MEDIA_ROOT.
    # 'submissions/%Y/%m/%d/' will organize files by date uploaded.
    # You can add validators=[validate_pdf] here too, but form validation is often preferred.
    uploaded_file = models.FileField(upload_to=submission_upload_path)
    submitted_at = models.DateTimeField(default=timezone.now)
    # Add status field for tracking Celery task progress
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETE', 'Complete'),
        ('FAILED', 'Failed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    celery_task_id = models.CharField(max_length=255, blank=True, null=True) # Store Celery task ID

    def __str__(self):
        # String representation for admin or debugging
        return f"Submission {self.id} by {self.student_name}"