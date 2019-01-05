"""
Info regarding course URLs

"""
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = 'https://web4s.eku.edu/prod/bwckschd.p_disp_detail_sched?term_in={year}{semester_code}&crn_in={crn}'


class URL:
    @staticmethod
    def get_url(year, semester, crn):
        """
        Get a URL given course information.

        Args:
            year (int): Year of the course.
            semester (str): Semester constant.
            crn (int): Course registration number.

        Returns: The course seating information URL.

        """
        from ..models import Course
        if semester == Course.FALL or semester == Course.WINTER:
            year += 1
        semester_code = Course.SEMESTER_CODES[semester]
        url = BASE_URL.format(
            year=year,
            semester_code=semester_code,
            crn=crn
        )
        return url

    @staticmethod
    def validate_url(url):
        """
        Validate a URL.

        Args:
            url (str): The URL to validate.

        Returns: True if valid, False if not.

        """
        # Get raw data from web page.
        raw = urllib.request.urlopen(url).read()
        # Parse HTML.
        parsed = BeautifulSoup(raw, features='html.parser')
        # Get the table associated with seating.
        seating_table = parsed.body.find('table', attrs={
            'class': 'datadisplaytable',
            'summary': 'This layout table is used to present the seating numbers.'
        })
        # If nothing found, URL is invalid.
        if seating_table is None:
            return False
        return True
