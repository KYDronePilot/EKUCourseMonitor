import threading
from time import sleep

from .seat_tracker import SeatingTracker

# Timeout between each polling of the website.
TIMEOUT = 30


# A thread for monitoring a particular course.
class MonitorThread(threading.Thread):
    def __init__(self, pk, url, course_name, *emails):
        threading.Thread.__init__(self)
        # Database primary key.
        self.id = pk
        # Create new SeatingTracker object.
        self.tracker = SeatingTracker(url, course_name, *emails)
        # Thread flow control.
        self.shut = threading.Event()

    # Thread run section.
    def run(self):
        # Run loop while control variable is not set.
        while not self.shut.is_set():
            # Check and send an alert if necessary.
            self.tracker.check_and_send_alerts()
            # Wait the specified time before checking again.
            self.sleep(TIMEOUT)

    # Custom sleep function, checks thread control status every second.
    def sleep(self, secs):
        """

        :type secs: int
        """
        # Run till secs has been decremented to 0 or thread control var is set.
        while secs > 0 and not self.shut.is_set():
            # Wait a second and decrement the number of secs.
            sleep(1)
            secs -= 1
