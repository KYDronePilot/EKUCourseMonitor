from django import forms
from .models import Course


# For saving a new course to be monitored.
class NewMonitoredCourse(forms.ModelForm):
    emails = forms.CharField(max_length=250, label='Emails Addresses (to be alerted, separated by commas)')

    class Meta:
        model = Course
        # Fields for the main signup form.
        fields = ['crn', 'name', 'semester', 'year', 'emails', 'future_alert']
        # Change labels to make more human readable.
        labels = {
            'crn': 'CRN (course registration number)',
            'name': 'Course Name',
            'future_alert': "I would like to be notified of this website's new address next semester"
        }
        # Add placeholders to specific fields.
        widgets = {
            'crn': forms.TextInput(attrs={'placeholder': '12345'}),
            'name': forms.TextInput(attrs={'placeholder': 'ENG 101'})
        }
