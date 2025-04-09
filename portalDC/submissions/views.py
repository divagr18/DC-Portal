# submissions/views.py

from django.shortcuts import render, redirect # Keep render if you ever need HTML fallback
from django.http import HttpResponse, JsonResponse # Import JsonResponse for API responses
from django.conf import settings # To check DEBUG status if needed
from .forms import SubmissionForm
from .models import Submission
from .tasks import process_submission
import os
import traceback # Import traceback for detailed error logging

def submit_assignment_view(request):
    """
    Handles assignment submissions, expecting POST requests typically from a JS frontend.
    Returns JSON responses.
    """
    print(">>> VIEW START <<<", flush=True) # Log view entry

    try:
        print(f"--- Request Method Check: {request.method} ---", flush=True) # Log the method

        # Initialize context (less relevant now we return JSON, but good practice)
        context = {'is_debug': settings.DEBUG}
        print("--- Context Initialized ---", flush=True)

        # Handle POST requests (the expected method for submissions)
        if request.method == 'POST':
            print("--- Inside POST Block ---", flush=True) # Confirm POST logic entry

            # Log raw data received - crucial for debugging frontend issues
            print("Raw POST data:", request.POST, flush=True)
            print("Raw FILES data:", request.FILES, flush=True)

            # Instantiate the form - wrap in try/except as errors can occur here
            try:
                print("--- Instantiating Form ---", flush=True)
                form = SubmissionForm(request.POST, request.FILES)
                print("--- Form Instantiated ---", flush=True)
            except Exception as e:
                print(f"--- ERROR DURING FORM INSTANTIATION ---", flush=True)
                print(traceback.format_exc(), flush=True) # Print full traceback
                # Return a server error response if form creation fails
                return JsonResponse({
                    'status': 'error',
                    'message': f'Server error during form processing: {e}'
                }, status=500)

            # Validate the form
            if form.is_valid():
                print("--- Form IS valid ---", flush=True) # Confirm validation success
                # Process the valid form - wrap in try/except for robustness
                try:
                    submission_instance = form.save(commit=False) # Create model instance
                    submission_instance.status = 'PENDING' # Set initial status
                    submission_instance.save() # Save to DB (also saves file)

                    # Ensure file path is accessible (critical for Celery)
                    if not submission_instance.uploaded_file:
                         raise ValueError("File not found on submission instance after save.")
                    file_path = submission_instance.uploaded_file.path
                    print(f"--- File saved at: {file_path} ---", flush=True)

                    # Queue the background task
                    task = process_submission.delay(
                        submission_instance.id,
                        submission_instance.student_name,
                        file_path
                    )
                    print(f"--- Celery task queued: {task.id} ---", flush=True)

                    # Optionally save Celery task ID to the model
                    submission_instance.celery_task_id = task.id
                    submission_instance.save(update_fields=['celery_task_id'])

                    # Prepare success message
                    success_message = f"Assignment submitted successfully! ID: {submission_instance.id} (Task ID: {task.id}). Processing started."
                    print(f"--- Success: {success_message} ---", flush=True)

                    # Return a JSON success response
                    return JsonResponse({
                        'status': 'success',
                        'message': success_message,
                        'submission_id': submission_instance.id,
                        'task_id': task.id
                    }, status=201) # 201 Created is appropriate

                except Exception as e:
                     # Catch errors during saving, queuing, etc.
                     print(f"--- ERROR during processing valid form ---", flush=True)
                     print(traceback.format_exc(), flush=True) # Log the full error
                     # Return a server error response
                     return JsonResponse({
                         'status': 'error',
                         'message': f'Internal server error after validation: {e}'
                     }, status=500)
            else:
                # Form validation failed
                print("--- Form IS INVALID ---", flush=True) # Log validation failure
                # Log the specific errors
                print("Form errors:", form.errors.as_json(), flush=True)
                # Return a JSON response indicating validation errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Form validation failed.',
                    'errors': form.errors.get_json_data() # Structured errors for frontend
                }, status=400) # 400 Bad Request

        else: # Handle methods other than POST (e.g., GET, PUT, DELETE)
            print(f"--- Inside ELSE (Method was {request.method}) ---", flush=True)
            # For an API endpoint primarily for POST, other methods are often disallowed
            return JsonResponse({
                'status': 'error',
                'message': f'Method {request.method} not allowed for this endpoint. Please use POST.'
            }, status=405) # 405 Method Not Allowed

    except Exception as e:
        # Catch any unexpected error early in the view execution
        print(f"--- UNEXPECTED ERROR IN VIEW (OUTER TRY) ---", flush=True)
        print(traceback.format_exc(), flush=True) # Log the full error
        # Return a generic server error response
        return JsonResponse({
            'status': 'error',
            'message': f'Unexpected server error: {e}'
        }, status=500)

    # This part should ideally not be reached if all code paths return a response
    print("--- Reached end of view unexpectedly? Should have returned earlier. ---", flush=True)
    return JsonResponse({
        'status': 'error',
        'message': 'Server error: View execution reached unexpected end.'
    }, status=500)



def submission_status_view(request, pk):
    """
    Handles GET requests to check the status of a specific submission.
    Returns JSON response with detailed submission info.
    """
    print(f">>> STATUS VIEW START (ID: {pk}) <<<", flush=True)

    if request.method == 'GET':
        try:
            print(f"--- Attempting to fetch Submission with pk={pk} ---", flush=True)
            # Fetch the submission object by its primary key (pk)
            submission = Submission.objects.get(pk=pk)
            print(f"--- Found Submission: ID={submission.id}, Status={submission.status} ---", flush=True)

            # --- Prepare the data for the JSON response ---
            file_name = os.path.basename(submission.uploaded_file.name) if submission.uploaded_file else None
            submitted_at_iso = submission.submitted_at.isoformat() if submission.submitted_at else None # Use ISO format for consistency

            response_data = {
                'status': 'success', # Indicates the API call succeeded
                # --- Match keys expected by the React component ---
                'id': submission.id,
                'student_name': submission.student_name,
                'status': submission.status, # This is the submission status itself
                'file_name': file_name,
                'submitted_at': submitted_at_iso,
                # --- End of matched keys ---
            }
            # --- End data preparation ---

            print(f"--- Sending response data: {response_data} ---", flush=True)
            # Return the detailed status in a JSON response
            return JsonResponse(response_data, status=200) # 200 OK

        except Submission.DoesNotExist:
            print(f"--- Submission with pk={pk} NOT FOUND ---", flush=True)
            return JsonResponse({
                'status': 'error',
                'message': f'Submission with ID {pk} not found.'
            }, status=404) # 404 Not Found

        except Exception as e:
            print(f"--- UNEXPECTED ERROR fetching status for pk={pk} ---", flush=True)
            print(traceback.format_exc(), flush=True)
            return JsonResponse({
                'status': 'error',
                'message': f'An unexpected server error occurred: {e}'
            }, status=500) # 500 Internal Server Error

    else:
        print(f"--- Method {request.method} not allowed for status check ---", flush=True)
        return JsonResponse({
            'status': 'error',
            'message': f'Method {request.method} not allowed. Please use GET.'
        }, status=405) # 405 Method Not Allowed
