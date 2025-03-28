import schedule
import time
import threading
from .services import OAuthServices

def periodic_task():
    """Scheduler test function"""
    print("Execution check for periodic task...")


def refresh_token():
    OAuthServices.refresh_access_token()


# Function to start the scheduler
def run_scheduler():
    
    schedule.every(15).hours.do(refresh_token)
    # schedule.every(10).minutes.do(periodic_task)
    # schedule.every(5).seconds.do(periodic_task)
    

    while True:
        schedule.run_pending()
        time.sleep(1)

# Thread function to start the scheduler in the background
def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
