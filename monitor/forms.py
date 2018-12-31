from django import forms
from .models import Course, Email


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


class DeactivateEmail(forms.Form):
    """
    Obtains deactivation code from the user.

    Attributes:
        code: The deactivation code.

    """
    code = forms.CharField(
        max_length=20,
        label='Deactivation Email'
    )

    def clean(self):
        """
        Validate the deactivation code.
         - Add an error if there are no active emails associated with the entered code.

        """
        super(DeactivateEmail, self).clean()
        code = self.cleaned_data.get('code')
        emails = Email.objects.filter(
            deactivation_code=code,
            deactivated=False
        )
        # Add an error if no active emails associated with this code.
        if not emails:
            self.add_error('code', 'This code is either not valid or has already been used.')

    class Meta:
        # Placeholder for deactivation code.
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'abcdefghij1234567890'})
        }
