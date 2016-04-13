from django.shortcuts import render, RequestContext
from .forms import *
import datetime
from .models import SubmitReport, Student, Faculty, Staff, Course
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib import auth
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required,user_passes_test, permission_required
from django.contrib.auth.mixins import UserPassesTestMixin
import pandas as pd
# Create your views here.


@login_required(redirect_field_name=None)
@user_passes_test(lambda u: u.is_superuser or u.student is not None, redirect_field_name=None,
	login_url='/accounts/login/')
def submit_page(request):
	'''Page for submitting records, accessible to student users'''
	student = Student.objects.get(user=request.user)
	if request.method == 'POST':
		form = SubmitReportForm(request.POST or None, student)
		form.fields['courses'].queryset = Course.objects.filter(students__in=[student])
		if form.is_valid():
			save_form = form.save(commit=False)
			save_form.submitter = student
			save_form.first_name = student.user.first_name
			save_form.last_name = student.user.last_name
			save_form.save()
			form.save_m2m()
			return HttpResponseRedirect('/accounts/student_view')
	else:
		form = SubmitReportForm()
		form.fields['courses'].queryset = Course.objects.filter(students__in=[student])
	return render(request, "submit_report.html", {'form': form})

#####################################################################
# Because the defualt template loader won't find templates that aren't stored on files
class Tplate(object):

	    def __init__(self, template):
	        self.template = template

	    def render(self, context=None, request=None):
	        if context is None:
	            context = {}
	        if request is not None:
	            context['request'] = request
	            context['csrf_input'] = csrf_input_lazy(request)
	            context['csrf_token'] = csrf_token_lazy(request)
	        return self.template.render(context)

def readable_datetime(datetime):
	return datetime.strftime("%-I:%M%p %b %d, %Y")

# Faculty view of reports
######################################################################
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
@login_required
@user_passes_test(lambda u: u.is_superuser or u.faculty is not None)
def faculty_view(request):

	reports = SubmitReport.objects.filter(courses__in=request.user.faculty.course_set.all()).distinct()
	reports.filter(status='APPROVED')
	form = ReportSearchForm(request.POST)
	courses = request.user.faculty.course_set.all()
	df = pd.DataFrame(list(reports.values(
		'first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary')))
	from django.template import Template, Context
	if form.is_valid():
		reports = form.filter_queryset(request, reports)
		df = pd.DataFrame(list(reports.values(
		'first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary')))
	if reports:
		#df.columns = ['First Name', 'Last Name', 'start_time', 'end_time', 'Notes']
		table = df.to_html(escape=False, index=False,
		columns=['first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary'],
		formatters={
			'Notes': (lambda s: '<abbr title=\"' + s + '\">Summary</abbr>'),
			# 'start_time': (lambda s: readable_datetime(s)),
			# 'end_time': (lambda s: readable_datetime(s)),
		})
	else:
		table = "No reports matched your search."

	return render(request, "faculty_view.html", {'form': form,
			'table': table,
		})


#Related to login
##############################################################

def login_view(request):
	"""Page for logging in"""
	c = {}
	c.update(csrf(request))
	return render(request, 'login.html', c)


def auth_view(request):
	"""Redirects users after login, or if login fails"""
	username = request.POST.get('username', '')
	password = request.POST.get('password', '')
	user = auth.authenticate(username=username, password=password)
	if user is not None:
		if user is not None:
			auth.login(request, user)
		if user.student is not None:
			return HttpResponseRedirect('/accounts/student_view/')
		if user.faculty is not None:
			return HttpResponseRedirect('/accounts/faculty_view/')
	else:
		return HttpResponseRedirect('/accounts/invalid/')


def logout_view(request):
	"""Page for users which have just logged out"""
	auth.logout(request)
	return render(request, 'logout.html')

#Home pages for different users (and also bd login info)
###################################################################

@login_required
@user_passes_test(lambda u: u.is_superuser or u.student is not None)
def student_logged_in_view(request):
	"""Homepage for logged in users"""
	return render(request, 'loggedin.html',
		{'username': request.user.username})


def invalid_login_view(request):
	"""Page for users who have not successfully logged in"""
	return render(request, 'invalid_login.html')


@login_required
@user_passes_test(lambda u: u.is_superuser or u.adminstaff is not None)
def admin_home_view(request):
	"""Homepage for logged in admin"""
	return render(request, 'admin_loggedin.html',
		{'username': request.user.username})

#Views for doing the actual stuff that users want to do
##########################################################################

@login_required
@user_passes_test(lambda u: u.is_superuser or u.adminstaff is not None)
def add_partners_view(request):
	'''Page for adding partners'''
	form = AddPartnerForm(request.POST or None)
	if form.is_valid():
		save_form = form.save(commit=False)
		save_form.save()
		if '_add_another' in request.POST:
			return HttpResponseRedirect('/admin/add_partner')
		return HttpResponseRedirect('admin_home_page')
	return render(request, "add_partner.html")

@login_required
@user_passes_test(lambda u: u.is_superuser or u.adminstaff is not None)
def add_student_view(request):
	'''Page for adding partners'''
	form = AddPartnerForm(request.POST or None)
	if form.is_valid():
		save_form = form.save(commit=False)
		save_form.save()
		if '_add_another' in request.POST:
			return HttpResponseRedirect('/admin/add_student')
		return HttpResponseRedirect('admin_home_page')
	return render(request, "add_student.html")