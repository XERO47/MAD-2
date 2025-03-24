from celery.schedules import crontab

# Celery Configuration
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'UTC'
enable_utc = True

# Scheduled Tasks
beat_schedule = {
    'daily-reminder': {
        'task': 'app.tasks.send_daily_reminder',
        'schedule': crontab(hour=20, minute=0)  # Run at 8 PM daily
    },
    'monthly-report': {
        'task': 'app.tasks.send_monthly_report',
        'schedule': crontab(0, 0, day_of_month='1')  # Run on the first day of each month
    }
} 