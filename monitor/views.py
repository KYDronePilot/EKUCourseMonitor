from django.shortcuts import render, redirect
from django.views.generic.base import View
from .forms import NewMonitoredCourse
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


# Thanks you page, to be displayed after the user has filled out a form.
def thank_you_page(request):
    return render(request, 'thank_you_page.html')
