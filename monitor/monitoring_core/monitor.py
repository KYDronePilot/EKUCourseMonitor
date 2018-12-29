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

        Attributes:
            workers (list): The worker threads to be closed.

        """
        pass

    def scan(self):
        """
        Scans the DB, creating new threads for any new courses and closing
        threads for any old ones.

        """
        # Get all course IDs.
        all_pks = [x[0] for x in list(Course.objects.all().values_list('id'))]
        # Get new PKs.
        active_pks = {pk: True for pk in all_pks}
        new_pks = [pk for pk in all_pks if pk not in active_pks]
        # Get removed PKs.
        all_pks_dict = {pk: True for pk in all_pks}
        removed_pks = [worker for worker in self.workers if worker not in all_pks_dict]
        # TODO: Finish here.



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
