# submissions/forms.py
import os
from django import forms
from .models import Submission
from django.core.exceptions import ValidationError

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['student_name', 'uploaded_file'] # Fields to include in the form

    def clean_uploaded_file(self):
        """
        Custom validation for the uploaded file field.
        Ensures the file is a PDF.
        """
        file = self.cleaned_data.get('uploaded_file', False)
        if file:
            # Check file size if needed (e.g., file.size > 10 * 1024 * 1024 for 10MB limit)
            # if file.size > 10 * 1024 * 1024:
            #     raise ValidationError("File size exceeds the 10MB limit.")

            # Check file extension
            ext = os.path.splitext(file.name)[1] # Get file extension
            valid_extensions = ['.pdf']
            if not ext.lower() in valid_extensions:
                raise ValidationError('Unsupported file type. Only PDF files are allowed.')
        # Always return the cleaned data, whether you have changed it or not.
        return file