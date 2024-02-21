from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler  # Import the APScheduler extension
import app

scheduler = APScheduler()

def send_email():
    try:
        print("hello nisa")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

# Configure the scheduler to run the send_email function every Thursday at 10:52
scheduler.add_job(id='send_email', func=send_email, trigger='cron', day_of_week='thu', hour=13, minute=56)

scheduler.start()