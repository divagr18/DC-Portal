# submissions/views.py
from django.http import HttpResponse
from .tasks import process_submission # Import the task function

def submit_assignment_view(request):
    # In a real view, you'd get these details from a form or database
    submission_id = 1234
    student_name = "Harshal Shah" # Using your username as an example
    file_path = "D:\portal\assignments" # Example path

    # Send the task to the Celery queue
    # .delay() is a shortcut for .apply_async()
    task = process_submission.delay(submission_id, student_name, file_path)

    # Return an immediate response to the user
    # task.id contains the unique ID of the task instance
    return HttpResponse(f"Assignment submitted! Processing started in the background. Task ID: {task.id}")