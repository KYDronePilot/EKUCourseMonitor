"""
Base monitoring script. Continually checks the DB for new courses to monitor
and adds threads for each one. Also removes threads for courses that have
been deactivated.

"""
import os
import signal
import sys
import time


sys.path.insert(0, '/Users/mikegalliers/Documents/repos/EKUCourseMonitor/EKUCourseMonitorWebpage')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EKUCourseMonitorWebpage.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from monitor.models import Course
from monitor.monitoring_core.seat_tracker import SeatingTracker


class Monitor:
    """
    Main class for performing monitoring tasks.

    Attributes:
        workers (list): List of active monitoring threads.

    """
    # Timeout between scanning.
    TIMEOUT = 10

    def __init__(self):
        self.workers = []
        # Start threads for courses that should have them.
        self.initialize()
        # Set signal handler for script.
        signal.signal(signal.SIGTERM, self.catch)
        signal.signal(signal.SIGHUP, self.catch)

    def initialize(self):
        """
        Actions to perform on startup of the monitoring script.
         - Start threads for all courses that should have them.

        """
        active_course_threads = Course.objects.filter(thread_active=True)
        for course in active_course_threads:
            self.new_worker(course)

    def new_worker(self, course, new=False):
        """
        Create new monitor thread for a course.

        Args:
            course (Course): The course to be monitored.
            new (boolean): Whether or not this is the first time this course is being monitored.

        """
        emails = course.emails.all()
        addrs = emails.values_list('email', flat=True)
        worker = SeatingTracker(
            course.id,
            course.url,
            course.name,
            *addrs
        )
        # Send out an initial alert if this is the first time monitoring this course.
        if new:
            worker.initial_alert()
        worker.start()
        self.workers.append(worker)

    @staticmethod
    def close_workers(workers):
        """
        Close monitor threads for a list of workers.
         - Set stop control for each worker.
         - Join worker threads.

        Args:
            workers (list): The worker threads to be closed.

        """
        for worker in workers:
            worker.shut.set()
        for worker in workers:
            worker.join()

    def setup_new_courses(self):
        """
        Check and setup monitoring on any new courses.

        Returns:
            True if new courses setup, False if not.

        """
        new_courses = Course.objects.filter(
            thread_active=False,
            is_monitored=True
        )
        if not new_courses:
            return False
        # Set them to have active threads.
        new_courses.update(thread_active=True)
        for course in new_courses:
            # Welcome the emails associated with this course.
            for email in course.emails.all():
                email.welcome_if_new()
            # Create worker for this course.
            self.new_worker(course, new=True)
        return True

    def close_deactivated_courses(self):
        """
        Stop monitoring any deactivated courses.

        Returns: True if any were found and deactivated, False if not.

        """
        deactivated_courses = Course.objects.filter(
            thread_active=True,
            is_monitored=False
        )
        if not deactivated_courses:
            return False
        # Set course thread status to deactivated.
        deactivated_courses.update(thread_active=False)
        # Close workers and remove from worker list.
        deactivated_courses = list(deactivated_courses)
        self.close_workers(deactivated_courses)
        for worker in deactivated_courses:
            self.workers.remove(worker)
        return True

    def scan(self):
        """
        Scans the DB, creating new threads for any new courses and closing
        threads for any deactivated ones. Waits the timeout amount before
        scanning again.

        """
        try:
            while True:
                self.setup_new_courses()
                self.close_deactivated_courses()
                time.sleep(Monitor.TIMEOUT)
        # Shut down threads on interrupt.
        except KeyboardInterrupt:
            self.close_workers(self.workers)

    def catch(self, signum, frame):
        """
        Shut down program on termination. This involves:
         - closing all the threads
         - pausing to ensure the threads are closed
         - and exiting

        """
        self.close_workers(self.workers)
        time.sleep(0.1)
        exit()


if __name__ == '__main__':
    monitor = Monitor()
    monitor.scan()
