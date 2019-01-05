import smtplib
import threading
import time
import urllib.request as request

from bs4 import BeautifulSoup
from decouple import config

# Text templates for alert messages.
OVERRIDE_ALERT = "There are no available seats and {seats} people have overrides"
NO_AVAILABLE_ALERT = "There are no available seats in the course"
AVAILABLE_ALERT = "There are {seats} seats available in the course"
AVAILABLE_CHANGE_ALERT = "The number of available seats has {incr_decr} by {value}. "

# Email template.
EMAIL_TEMPLATE = '''\
From: {from_field}
To: {{to_field}}
Subject: {subject_field}

{body}
'''

# Gmail authentication information.
GMAIL_USERNAME = config('GMAIL_USERNAME')
GMAIL_PASSWORD = config('GMAIL_PASSWORD')


class SeatingValue:
    """
    Simple abstraction class for holding the values of of each seating attribute.

    Attributes:
        cur_val (int): The current seating value.
        prev_val (int): The previous seating value.

    """

    def __init__(self):
        self.cur_val = 0
        self.prev_val = 0

    def get_diff(self):
        """
        Get the difference between the new and previous values.

        Returns: Difference between current and previous values.

        """
        return self.cur_val - self.prev_val

    def update(self, new_val):
        """
        Update current seating value with an inputted value.

        """
        self.prev_val = self.cur_val
        self.cur_val = new_val


# For tracking whether the seating data changes.
class SeatingTracker(threading.Thread):
    """
    Tracks the seating of a specific course and sends email alerts whenever
    the number of available seats changes.

    Attributes:
        INTERVAL (int): Number of seconds to sleep between each scan.
        shut (threading.Event): Stop control for the thread.
        pk (int): Database PK for this entry.
        emails (list): The email addresses to be alerted whenever the seating changes.
        course_name (str): Name of the course being monitored.
        url (str): URL that contains seating information for this course.
        capacity (SeatingValue): The capacity of the course.
        actual (SeatingValue): The actual number of seats in the course.
        remaining (SeatingValue): The number of remaining seats in the course.

    """
    INTERVAL = 500

    def __init__(self, pk, url, course_name, *emails):
        threading.Thread.__init__(self)
        self.shut = threading.Event()
        self.pk = pk
        self.emails = emails
        self.course_name = course_name
        self.url = url
        self.capacity = SeatingValue()
        self.actual = SeatingValue()
        self.remaining = SeatingValue()
        # Update the seating initially.
        self.update_seating()

    def update_seating(self):
        """
        Update seating attributes with data from EKU's website.

        """
        # Get raw data from web page.
        raw = request.urlopen(self.url).read()
        # Parse HTML.
        parsed = BeautifulSoup(raw, features='html.parser')
        # Get the table associated with seating.
        seating_table = parsed.body.find('table', attrs={
            'class': 'datadisplaytable',
            'summary': 'This layout table is used to present the seating numbers.'
        })
        # Get the second table row, containing information about open seats.
        seating_row = seating_table.find_all('tr')[1]
        # Get a list of columns as such: [Capacity, Actual, Remaining]
        seating_cols = seating_row.find_all('td')
        # Convert to ints.
        raw_vals = [int(seat_tag.string) for seat_tag in seating_cols]
        # Update seating attributes.
        self.capacity.update(raw_vals[0])
        self.actual.update(raw_vals[1])
        self.remaining.update(raw_vals[2])

    def get_alert_text(self):
        """
        Get the alert text for a change in the number of available seats.

        Returns: User-friendly alert text describing how the seating has changed.

        """
        diff = self.remaining.get_diff()
        # If no changes, exit.
        if diff == 0:
            return None
        # Format text for how value changed.
        incr_decr = 'increased' if diff > 0 else 'decreased'
        change_text = AVAILABLE_CHANGE_ALERT.format(
            incr_decr=incr_decr,
            value=abs(diff)
        )
        # Get text describing the current number of available seats.
        remaining_text = self.get_remaining_text()
        return change_text + remaining_text

    def get_remaining_text(self):
        """
        Get text describing the number of remaining seats available.

        Returns: Description of the remaining seats.

        """
        if self.remaining.cur_val < 0:
            remaining_text = OVERRIDE_ALERT.format(
                seats=self.remaining.cur_val * -1
            )
        elif self.remaining.cur_val > 0:
            remaining_text = AVAILABLE_ALERT.format(
                seats=self.remaining.cur_val
            )
        else:
            remaining_text = NO_AVAILABLE_ALERT
        return remaining_text

    def email_alert(self, text):
        """
        Email an alert through a Gmail account.

        Args:
            text (str): The text to be sent.

        """
        # Make an ssl connection to Gmail's SMTP server.
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.ehlo()
        # Login to email account.
        server_ssl.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        # Format the email to be sent.
        content = EMAIL_TEMPLATE.format(
            from_field='EKU Course Monitor',
            subject_field='[Course Monitor] {0} Seating Changes'.format(
                self.course_name
            ),
            body=text
        )
        # Send email to each specified person.
        for email in self.emails:
            # Send the email.
            server_ssl.sendmail(
                GMAIL_USERNAME,
                email,
                content.format(to_field=email)
            )
        # Close the server connection.
        server_ssl.close()

    def initial_alert(self):
        """
        Send an initial alert email to the contacts.
        Works by,
         - Updating the seating values.
         - Getting text describing the seats remaining.
         - Sending the email.

        """
        self.update_seating()
        text = self.get_remaining_text()
        self.email_alert(text)

    def scan(self):
        """
        Check if seating has changed and send alert if so.

        Returns: True if seating changed, False if not.

        """
        # Exit if there are no changes.
        self.update_seating()
        text = self.get_alert_text()
        if text is None:
            return False
        # Send alert otherwise.
        self.email_alert(text)

    def sleep(self, secs):
        """
        Sleep while checking thread event.

        Args:
            secs (int): The number of seconds to wait.

        """
        while secs > 0 and not self.shut.is_set():
            time.sleep(1)
            secs -= 1

    def run(self):
        """
        Main thread execution; scan for updates every update interval.

        """
        while not self.shut.is_set():
            self.scan()
            self.sleep(SeatingTracker.INTERVAL)
