from monitor.models import Course


# For calculating the URL of a course object.
class URLCalculator:
    # Base URL to have the necessary information formatted in.
    BASE_URL = 'https://web4s.eku.edu/prod/bwckschd.p_disp_detail_sched?term_in={year}{semester_code}&crn_in={crn}'
    # URL codes for each specific semester.
    SEMESTER_CODES = {
        Course.SPRING: 20,
        Course.SUMMER: 50,
        Course.FALL: 10,
        Course.WINTER: 15
    }

    # Calculates the URL.
    @classmethod
    def calculate(cls, course):
        # Get the course year.
        year = course.year
        # If semester is Fall or Winter, increment year (just the way EKU's website works...).
        if course.semester == Course.FALL or course.semester == Course.WINTER:
            year += 1

        # Format the URL, including the necessary information.
        url = cls.BASE_URL.format(
            year=year,
            semester_code=cls.SEMESTER_CODES[course.semester],
            crn=course.crn
        )
        # Return the formatted URL.
        return url
