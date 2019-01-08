from django import forms
from .models import Course
from .monitoring_core.url import URL


# For saving a new course to be monitored.
class NewMonitoredCourse(forms.ModelForm):
    emails = forms.CharField(max_length=250, label='Emails Addresses (to be alerted, separated by commas)')

    def clean(self):
        """
        Validate that the course exists.

        """
        super(NewMonitoredCourse, self).clean()
        year = self.cleaned_data.get('year')
        semester = self.cleaned_data.get('semester')
        crn = self.cleaned_data.get('crn')
        url = URL.get_url(year, semester, crn)
        # If not valid, add error to each course field.
        if not URL.validate_url(url):
            msg = 'A course does not exist for the information entered.'
            self.add_error('crn', msg)
            self.add_error('name', msg)
            self.add_error('semester', msg)
            self.add_error('year', msg)

    class Meta:
        model = Course
        # Fields for the main signup form.
        fields = ['crn', 'name', 'semester', 'year', 'emails', 'future_alert']
        # Change labels to make more human readable.
        labels = {
            'crn': 'CRN (course registration number)',
            'name': 'Course Name',
            'future_alert': 'I would like to be notified when this website reopens next semester'
        }
        # Add placeholders to specific fields.
        widgets = {
            'crn': forms.TextInput(attrs={'placeholder': '12345'}),
            'name': forms.TextInput(attrs={'placeholder': 'ENG 101'})
        }
