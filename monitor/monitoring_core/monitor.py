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
        # Start threads for each course that needs to be monitored.
        # TODO: Finish here.

    def new_worker(self, course):
        """
        Create new monitor thread for a course.

        Args:
            course (Course): The course to be monitored.

        """
        emails = list(course.emails.all())
        worker = SeatingTracker(
            course.id,
            course.url,
            course.name,
            *emails
        )
        worker.start()
        self.workers.append(worker)

    def close_workers(self, workers):
        """
        Close monitor threads for a list of courses.
         - Set stop control for each worker.
         - Join worker threads.

        Args:
            workers (list): The worker threads to be closed.

        """
        for worker in workers:
            worker.shut.set()
        for worker in workers:
            worker.join()

    def get_new_courses(self):
        """
        Get new courses from the DB that need to be monitored.
         - Gets new courses and sets their thread status to active.

        Returns: New courses to add to workers.

        """
        new_courses = Course.objects.filter(
            thread_active=False,
            is_monitored=True
        )
        for course in new_courses:
            course.thread_active = True
            course.save()
        return new_courses

    def get_deactivated_courses(self):
        """
        Get courses that have been disabled and should not be monitored (deactivated).
         - Gets deactivated courses and sets their thread status to not active.

        Returns: Deactivated courses.

        """
        deactivated_courses = Course.objects.filter(
            thread_active=True,
            is_monitored=False
        )
        for course in deactivated_courses:
            course.thread_active = False
            course.save()
        return deactivated_courses

    def scan(self):
        """
        Scans the DB, creating new threads for any new courses and closing
        threads for any deactivated ones.

        """
        # Get courses that should be monitored but aren't currently.
        new_courses = list(self.get_new_courses())
        # Start monitoring each new course.
        for course in new_courses:
            self.new_worker(course)
        # Get deactivated courses that are being monitored.
        deactivated_courses = list(self.get_deactivated_courses())
        # Close threads for deactivated courses.
        self.close_workers(deactivated_courses)

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
