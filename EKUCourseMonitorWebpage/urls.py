"""EKUCourseMonitorWebpage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from monitor.views import CourseForm, thank_you_page
from monitor.views import DeactivationForm, deactivation_confirmation

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CourseForm.as_view(), name='new_course_form'),
    path('thank-you-page/', thank_you_page, name='thank_you_page'),
    path('deactivation/', DeactivationForm.as_view(), name='deactivation'),
    path('deactivation-conformation', deactivation_confirmation, name='deactivation_confirmation'),
]
