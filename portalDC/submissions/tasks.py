# submissions/tasks.py
import time
from celery import shared_task # Use shared_task to avoid importing the Celery app instance directly

@shared_task
def process_submission(submission_id, student_name, file_path):
    """
    Simulates processing an assignment submission.
    In a real scenario, this would involve database lookups,
    file operations, plagiarism checks, etc.
    """
    print(f"Starting processing for submission {submission_id} from {student_name}...")
    print(f"File located at: {file_path}")

    # Simulate some work (e.g., plagiarism check, grading script)
    try:
        # Simulate work taking 10 seconds
        time.sleep(10)
        result = f"Successfully processed submission {submission_id}."
        print(result)
        # Here you might update the submission status in the database
    except Exception as e:
        result = f"Failed to process submission {submission_id}. Error: {e}"
        print(result)
        # Handle error, maybe log it or mark submission as failed in DB

    return result # The return value is stored in the result backend (Redis db 1)