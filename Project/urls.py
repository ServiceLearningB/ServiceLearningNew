"""Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from submit_reports.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import login
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/home$', admin_home_view, name='admin_home_page'),
    url(r'^admin/add_partner$', add_partners_view, name='add_partners_page'),
    url(r'^admin/add_student$', add_student_view, name='add_student_page'),
    url(r'^submit_report/$', submit_page, name='submit_page'),
    url(r'^accounts/login/$', login_view, name='login_page'),
    url(r'^accounts/auth/$', auth_view, name='authorization_page'),
    url(r'^accounts/logout/$', logout_view, name='logout_page'),
    url(r'^accounts/student_view/$', student_logged_in_view, name='student_logged_in_page'),
    url(r'^accounts/invalid/$', invalid_login_view, name='invalid_login_page'),
    url(r'^accounts/faculty_view/$', faculty_view, name='faculty_view_page'),
]

#authentication urls


"""
if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL,
		document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL,
		document_root=settings.MEDIA_ROOT)"""