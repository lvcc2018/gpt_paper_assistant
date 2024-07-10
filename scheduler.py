import sched
import time
import os
import datetime
from threading import Thread

def run_script():
    script_path = "/mnt/user/lvchuancheng/gpt_paper_assistant/main.py"
    os.system('cd /mnt/user/lvchuancheng/gpt_paper_assistant')
    os.system(f'pipenv run python3 {script_path}')

def schedule_task(scheduler, task_time):
    now = datetime.datetime.now()
    run_at = now.replace(hour=task_time.hour, minute=task_time.minute, second=0, microsecond=0)
    
    if now >= run_at:
        run_at += datetime.timedelta(days=1)
    
    delay = (run_at - now).total_seconds()
    scheduler.enter(delay, 1, run_daily, (scheduler, task_time))

def run_daily(scheduler, task_time):
    run_script()
    schedule_task(scheduler, task_time)

def start_scheduler():
    scheduler = sched.scheduler(time.time, time.sleep)
    task_time = datetime.time(hour=11, minute=0)
    schedule_task(scheduler, task_time)
    
    thread = Thread(target=scheduler.run)
    thread.daemon = True
    thread.start()
    
    while True:
        time.sleep(1)

if __name__ == "__main__":
    start_scheduler()