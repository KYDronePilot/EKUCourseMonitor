import datetime
import string
import random
import smtplib
from decouple import config

from django.db import models

# Gmail authentication information.
GMAIL_USERNAME = config('GMAIL_USERNAME')
GMAIL_PASSWORD = config('GMAIL_PASSWORD')
# Email template.
EMAIL_TEMPLATE = '''\
From: {from_field}
To: {to_field}
Subject: {subject_field}

{body}
'''
# Template for welcome email.
WELCOME_TEMPLATE = """\
Welcome to the EKU course monitor!

Your deactivation code is: {code}

If you ever want to stop receiving alerts, please go to {website} and enter this code to deactivate your email.

A few things to go over:
- This program was developed by a fellow EKU student and thus does not have professional support
  or guarantee of working.
- The program will run for 2 weeks past the first day of courses and then be shut down.
- Email alerts will be sent out when the website opens back up for another semester.

If you have any questions, please reply to this email.

Good luck getting into classes!
"""


# Get possibilities for year selection of Course objects.
def years():
    # Get the datetime right now.
    now = datetime.datetime.now()
    # Get the year value of now plus approximately 5 months.
    end_year = (now + datetime.timedelta(days=150)).year
    # Return list of possibilities, built from a range from 10 years to the end year.
    return [(x, x) for x in range(end_year - 10, end_year + 1)]


class Course(models.Model):
    """
    For holding information about each course to be monitored.

    """
    BASE_URL = 'https://web4s.eku.edu/prod/bwckschd.p_disp_detail_sched?term_in={year}{semester_code}&crn_in={crn}'
    # Constants for the possible semester selections.
    SPRING = 'spr'
    SUMMER = 'sum'
    FALL = 'fal'
    WINTER = 'win'
    # URL codes for each specific semester.
    SEMESTER_CODES = {
        SPRING: 20,
        SUMMER: 50,
        FALL: 10,
        WINTER: 15
    }
    # Course registration number.
    crn = models.PositiveIntegerField()
    # The name of the course (for alerts).
    # TODO make a constraint on the related form.
    name = models.CharField(max_length=25)
    # Possible choices for the semester column.
    SEMESTERS = (
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
        (FALL, 'Fall'),
        (WINTER, 'Winter')
    )
    # The semester this course is in (Spring, Summer, Fall, or Winter)
    semester = models.CharField(max_length=10, choices=SEMESTERS)
    # The year of the course, choices generated by the years property.
    year = models.PositiveSmallIntegerField(choices=years(), default=datetime.date.today().year)
    # Whether or not the associated emails should be alerted of the server's new IP next semester.
    future_alert = models.BooleanField(default=True)
    # Is there an active monitor thread.
    thread_active = models.BooleanField(default=False, blank=True)
    # Whether this course should be monitored.
    is_monitored = models.BooleanField(default=True, blank=True)

    @property
    def url(self):
        """
        Get the URL for the course. Works by,
         - incrementing the year if fall or winter (how EKU's system works)
         - getting the proper semester code
         - formatting the URL

        Returns: The course URL for monitoring.

        """
        year = self.year
        if self.semester == Course.FALL or self.semester == Course.WINTER:
            year += 1
        semester_code = Course.SEMESTER_CODES[self.semester]
        url = Course.BASE_URL.format(
            year=year,
            semester_code=semester_code,
            crn=self.crn
        )
        return url

    def __str__(self):
        return "{0} ({1}), {2}, {3}".format(self.name, self.crn, self.semester, self.year)


# Holds the emails to be alerted for different courses.
class Email(models.Model):
    # An email address to be alerted.
    email = models.EmailField()
    # Related course.
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='emails')
    # Whether or not this email has been sent a welcome email.
    welcomed = models.BooleanField(default=False)
    # Deactivation code for this email.
    deactivation_code = models.CharField(max_length=20, null=True, blank=True)
    # Whether the email has been deactivated.
    deactivated = models.BooleanField(default=False)

    # For debugging.
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """
        Generate a deactivation code before saving.

        Args:
            *args: Args for save function.
            **kwargs: KW args for save function.

        """
        self.deactivation_code = self.get_deactivation_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        """
        Generates deactivation codes.

        Returns: A deactivation code unique to the database.

        """
        while True:
            random_set = (random.choice(string.ascii_letters + string.digits) for n in range(20))
            random_code = ''.join(random_set)
            # Stop generating if code is unique to the database.
            if not Email.objects.filter(deactivation_code=random_code):
                return random_code

    def get_deactivation_code(self):
        """
        Get a deactivation code for this email.

        Returns: A deactivation code.

        """
        # Get reset code from any other emails that are the same.
        emails = Email.objects.filter(email=self.email)
        # If this is a new email, generate a new one.
        if not emails:
            return Email.generate_code()
        # Otherwise, use the code from another record of this email.
        else:
            codes = emails.values_list('deactivation_code', flat=True)
            return codes[0]

    def welcome(self):
        """
        Send welcome email to this email address.

        """
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.ehlo()
        # Make an ssl connection to Gmail's SMTP server.
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.ehlo()
        # Login to email account.
        server_ssl.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        # Format the welcome message, email, and send it.
        msg = WELCOME_TEMPLATE.format(
            code=self.deactivation_code
        )
        content = EMAIL_TEMPLATE.format(
            from_field='EKU Course Monitor',
            to_field=self.email,
            subject_field='Welcome to the EKU Course Monitor',
            body=msg
        )
        server_ssl.sendmail(
            GMAIL_USERNAME,
            self.email,
            content
        )
        server_ssl.close()
        # Signify that welcome email was sent.
        self.welcomed = True

    def welcome_if_new(self):
        """
        Welcome email address if new.

        Returns: True if new and was welcomed, False if not.

        """
        same_emails = Email.objects.filter(email=self.email, welcomed=True)
        # If already exits and welcomed, set welcomed and exit.
        if same_emails:
            self.welcomed = True
            return False
        # Else, welcome.
        self.welcome()
