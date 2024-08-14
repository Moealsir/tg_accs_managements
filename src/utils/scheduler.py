# src/utils/scheduler.py

import schedule
import time
import threading

class Scheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, func, time_str):
        job = schedule.every().day.at(time_str).do(func)
        self.jobs.append(job)

    def run_pending(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        threading.Thread(target=self.run_pending).start()

# Example usage:
# scheduler = Scheduler()
# scheduler.add_job(my_function, "12:00")
# scheduler.start()
