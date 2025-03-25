import schedule
import time
import threading
from .services import OAuthServices

def periodic_task():
    """Scheduler test function"""
    print("Executing periodic task...")


def refresh_token():
    OAuthServices.refresh_access_token()


# Function to start the scheduler
def run_scheduler():
    schedule.every(24).hours.do(refresh_token)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Thread function to start the scheduler in the background
def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
