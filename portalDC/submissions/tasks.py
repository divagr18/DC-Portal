# submissions/tasks.py
import time
import os # Import os if needed for path manipulation
from celery import shared_task
from .models import Submission # Import the model

@shared_task(bind=True) # Use bind=True to access task instance (self) if needed
def process_submission(self, submission_id, student_name, file_path):
    """
    Processes an assignment submission using its ID and file path.
    """
    print(f"Task ID: {self.request.id} - Received submission ID: {submission_id}")
    try:
        # Fetch the submission object from the database
        submission = Submission.objects.get(pk=submission_id)
        submission.status = 'PROCESSING'
        submission.save(update_fields=['status']) # Update status immediately
        print(f"Processing submission {submission.id} from {submission.student_name}...")
        print(f"File expected at: {submission.uploaded_file.path}") # Path from DB
        print(f"File path received by task: {file_path}") # Path passed as argument

        # --- Actual Processing Logic ---
        # Check if the file actually exists at the given path
        if not os.path.exists(file_path):
             raise FileNotFoundError(f"File not found at path: {file_path}")

        # Simulate work (e.g., read file content, plagiarism check)
        print(f"Simulating work on {os.path.basename(file_path)}...")
        # with open(file_path, 'rb') as f:
        #     content = f.read() # Example: reading file content
        #     print(f"Read {len(content)} bytes.")
        time.sleep(10) # Simulate long processing

        result = f"Successfully processed submission {submission_id}."
        print(result)
        submission.status = 'COMPLETE'
        # --- End Processing Logic ---

    except Submission.DoesNotExist:
        result = f"Failed to process: Submission with ID {submission_id} not found."
        print(result)
        # No submission object to update status on
        # Potentially log this error more formally
        # You might want Celery to retry or just log the failure
        return result # Return failure message

    except FileNotFoundError as e:
        result = f"Failed to process submission {submission_id}: {e}"
        print(result)
        if 'submission' in locals(): # Check if submission object was fetched
            submission.status = 'FAILED'
            submission.save(update_fields=['status'])
        # Log error
        return result # Return failure message

    except Exception as e:
        # Catch any other unexpected errors during processing
        result = f"Unexpected error processing submission {submission_id}: {e}"
        print(result)
        if 'submission' in locals():
            submission.status = 'FAILED'
            submission.save(update_fields=['status'])
        # Log error, maybe re-raise to let Celery handle retries if configured
        # raise self.retry(exc=e, countdown=60) # Example retry
        return result # Return failure message

    finally:
        # Ensure final status is saved if processing completed or failed expectedly
        if 'submission' in locals() and submission.status != 'PENDING': # Avoid overwriting if error happened before fetch
             submission.save(update_fields=['status'])

    return result # Return success message