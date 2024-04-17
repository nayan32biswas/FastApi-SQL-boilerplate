from worker.main import celery_app


@celery_app.task
def send_email(*args, **kwargs):
    print("Successfully send the email...", args, kwargs)
    return True
