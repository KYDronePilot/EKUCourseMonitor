"""
Base monitoring script. Continually checks the DB for new courses to monitor
and adds threads for each one. Also removes threads for courses that are no
longer in the DB.

"""
import time

from monitor.models import Course
from monitor.monitoring_core.seat_tracker import SeatingTracker


class Monitor:
    """
    Main class for performing monitoring tasks.

    Attributes:
        workers (list): List of active monitor threads.

    """
    # Timeout between scanning.
    TIMEOUT = 10

    def __init__(self):
        self.workers = []
        # Start threads for courses that should have them.
        self.initialize()

    def initialize(self):
        """
        Actions to perform on startup of the monitoring script.
         - Start threads for all courses that should have them.

        """
        active_course_threads = Course.objects.filter(thread_active=True)
        for course in active_course_threads:
            self.new_worker(course)

    def new_worker(self, course):
        """
        Create new monitor thread for a course.

        Args:
            course (Course): The course to be monitored.

        Returns:
            True if a worker was created, False if not.

        """
        emails = course.emails.filter(deactivated=False)
        # If none, do not monitor.
        if not emails:
            return False
        addrs = emails.values_list('email', flat=True)
        worker = SeatingTracker(
            course.id,
            course.url,
            course.name,
            *addrs
        )
        worker.start()
        self.workers.append(worker)
        return True

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
        for course in new_courses:
            # Set them to have active threads.
            course.thread_active = True
            course.save()
            # Welcome the emails associated with this course.
            for email in course.emails.all():
                email.welcome_if_new()
        # Create workers for each one.
        for course in new_courses:
            self.new_worker(course)
        return True

    def close_deactivated_courses(self):
        """
        Stop monitoring any deactivated courses.

        Returns: True if any were found, False if not.

        """
        deactivated_courses = Course.objects.filter(
            thread_active=True,
            is_monitored=False
        )
        if not deactivated_courses:
            return False
        deactivated_courses = list(deactivated_courses)
        # Set course thread status to deactivated.
        for course in deactivated_courses:
            course.thread_active = False
            course.save()
        # Close workers and remove from worker list.
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
        while True:
            self.setup_new_courses()
            self.close_deactivated_courses()
            time.sleep(Monitor.TIMEOUT)

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
