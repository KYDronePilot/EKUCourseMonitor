from django.shortcuts import render, redirect
from django.views.generic.base import View
from .forms import NewMonitoredCourse, DeactivateEmail
from .models import Email


# For gathering monitoring information from the user.
class CourseForm(View):
    # Handle GET requests (return an empty form).
    def get(self, request):
        # Create a new NewMonitoredCourse form.
        form = NewMonitoredCourse()
        return render(request, 'home.html', {'form': form})

    # Handle POST requests (process the form).
    def post(self, request):
        # Create a filled out form from the request.
        form = NewMonitoredCourse(request.POST)
        # If the form is valid, process the data and save it.
        if form.is_valid():
            # Save new Course object.
            course = form.save()
            # Get the string of comma separated email addresses.
            emails = form.cleaned_data.get('emails')
            # Split at each comma and strip whitespace from either end.
            emails = [x.strip() for x in emails.split(',')]
            # Create new related email objects for each one in the list.
            for email in emails:
                Email.objects.create(
                    email=email,
                    course=course
                )
            # Redirect to thank you page.
            return redirect('thank_you_page')
        # Otherwise, render the bound form with errors.
        return render(request, 'home.html', {'form': form})


class DeactivationForm(View):
    """
    Deactivation form to remove an email from monitoring.

    """
    @staticmethod
    def get(request):
        """
        Create an empty form.

        Args:
            request: Request data.

        Returns: Response with empty form.

        """
        form = DeactivateEmail()
        return render(
            request,
            'deactivate.html',
            {'form': form}
        )

    @staticmethod
    def post(request):
        """

        Args:
            request: Request data.

        Returns: Redirect to confirmation page or form errors.

        """
        form = DeactivateEmail(request.POST)
        if form.is_valid():
            # Grab the address and deactivate each email.
            emails = Email.objects.filter(
                deactivation_code=form.code
            )
            addr = emails[0].email
            for email in emails:
                email.deactivated = True
                email.save()
            # Show user a confirmation.
            return redirect('deactivation_confirmation', addr)
        # Else, handle form errors.
        return render(
            request,
            'deactivate.html',
            {'form': form}
        )


# Thanks you page, to be displayed after the user has filled out a form.
def thank_you_page(request):
    return render(request, 'thank_you_page.html')


def deactivation_confirmation(request, addr):
    """
    Deactivation confirmation page.

    Args:
        request: Request data.
        addr (str): Email address deactivated.

    Returns: Response with the address that was removed.

    """
    return render(
        request,
        'deactivation_confirmation.html',
        {'addr': addr}
    )
