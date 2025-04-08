# submissions/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse # Keep this if you want simple text response on success
from .forms import SubmissionForm
from .tasks import process_submission
from .models import Submission # Import the model

def submit_assignment_view(request):
    success_message = None
    if request.method == 'POST':
        # Bind data from request.POST and request.FILES to the form
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Form is valid, save the model instance (this also saves the file)
            submission_instance = form.save(commit=False) # Don't commit yet if you need to modify
            submission_instance.status = 'PENDING' # Set initial status
            submission_instance.save() # Now save to DB, getting the ID
            print("Got file!")
            # Get necessary data for the task
            submission_id = submission_instance.id
            student_name = submission_instance.student_name
            # Get the full path to the saved file
            file_path = submission_instance.uploaded_file.path

            # Send the task to the Celery queue
            task = process_submission.delay(submission_id, student_name, file_path)

            # Optional: Store the Celery task ID on the submission model
            submission_instance.celery_task_id = task.id
            submission_instance.save(update_fields=['celery_task_id'])

            # Provide feedback to the user
            success_message = f"Assignment submitted successfully! Your submission ID is {submission_id}. Processing started (Task ID: {task.id})."
            # You could redirect instead: return redirect('some_success_page')
            # For now, re-render the form page with a success message
            form = SubmissionForm() # Show a blank form after successful submission
            return render(request, 'submissions/submit_form.html', {'form': form, 'success_message': success_message})

        # else: form is invalid, it will be re-rendered with errors below
    else: # GET request
        form = SubmissionForm() # Create a blank form

    return render(request, 'submissions/submit_form.html', {'form': form})