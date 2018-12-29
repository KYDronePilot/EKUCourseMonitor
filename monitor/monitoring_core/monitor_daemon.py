import os
import signal
import sys
from time import sleep

# Set up the django environment.
sys.path.insert(0, '../../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EKUCourseMonitor.settings")

from monitor.models import Course
from monitor.monitoring_core.daemon import Daemon
from monitor.monitoring_core.thread_monitor import MonitorThread
from monitor.monitoring_core.url_calculator import URLCalculator

# File that indicates a change was made to the database if exists.
CHANGE_FILE = 'changes/change'
# Timeout (in seconds) between checking for changes.
CHANGE_CHECK_TIMEOUT = 15


class CourseMonitorDaemon(Daemon):
    def __init__(self, pidfile):
        # Call super init.
        Daemon.__init__(self, pidfile)
        # For holding the worker threads.
        self.workers = list()

    # Daemon main loop.
    def run(self):
        # Initialize and start threads for each Course object in the database.
        self.initialize()
        # Continually check if a change file exists, indicating that the workers need to be rescanned.
        while True:
            # Check if change indicator file exists.
            if os.path.exists(CHANGE_FILE):
                # Rescan the workers and Course database objects, creating and deleting workers as necessary.
                self.rescan()
                # Remove the change indicator file.
                os.remove(CHANGE_FILE)
            # Wait before checking again for changes.
            sleep(CHANGE_CHECK_TIMEOUT)

    # Create a new worker thread for a course object.
    def new_worker(self, course):
        # Get the emails associated with this Course object.
        emails = list(course.emails.all())
        # Calculate the URL for the course.
        url = URLCalculator.calculate(course)
        # Create the thread, providing necessary information.
        worker = MonitorThread(
            course.id, url, course.name, *emails
        )
        # Start the worker thread.
        worker.start()
        # Append to list of workers.
        self.workers.append(worker)

    # Rescan the database and worker threads, removing and creating new threads if necessary.
    def rescan(self):
        # Get the ID of each Course object from the DB.
        courses_ids = list(Course.objects.all().values_list('id'))
        # Get list of DB IDs for each worker.
        worker_ids = [x.pk for x in self.workers]
        # Handle each course_id from the database at a time.
        for course_id in [x[0] for x in courses_ids]:
            # If the course_id doesn't have a worker, get the course object and create a worker.
            if course_id not in worker_ids:
                # Get Course object.
                course = Course.objects.get(id=course_id)
                # Create worker.
                self.new_worker(course)
                # Add course_id to list of worker_ids (prevents extra checking below).
                worker_ids.append(course_id)
            # Remove the worker_id matching the current course_id.
            worker_ids.remove(course_id)
        # Whatever worker_ids are left over need to be stopped. Get the workers based on their ID.
        workers = [worker for worker in self.workers if worker.pk in worker_ids]
        # Close those worker objects.
        self.close_workers(workers)

    # Close a list of workers.
    @staticmethod
    def close_workers(workers):
        # Set each worker's control var.
        for worker in workers:
            worker.shut.set()
        # Join all the threads.
        for worker in workers:
            worker.join()

    # Set signal handling method and start thread for each Course database object.
    def initialize(self):
        # Set catch method to handle SIGTERM and SIGHUP.
        signal.signal(signal.SIGTERM, self.catch)
        signal.signal(signal.SIGHUP, self.catch)
        # Get Course objects from the database to monitor.
        courses = Course.objects.all()
        # For each course, create a monitoring thread.
        for course in courses:
            self.new_worker(course)

    # Actions to take when the Daemon is terminated.
    def catch(self, signum, frame):
        # Close all threads.
        self.close_workers(self.workers)
        # Give the threads a little time to close.
        sleep(0.05)
        # Exit the program.
        sys.exit()
