from worker.main import celery_app


@celery_app.task
def ten_minute_crontab():
    print("tem_minute_crontab called")
    return True
