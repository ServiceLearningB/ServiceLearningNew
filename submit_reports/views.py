from django.shortcuts import render, RequestContext
from .forms import *
import datetime
from django.forms import modelformset_factory
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
from django.core.mail import send_mail
# Create your views here.

class FilteredListView(FormMixin, ListView):
	def get_form_kwargs(self):
		return {
			'initial': self.get_initial(),
			'prefix': self.get_prefix,
			'data': self.request.GET or None
		}

	def get(self, request, *args, **kwargs):
		self.object_list = self.get_queryset()
		form = self.get_form(self.get_form_class())
		if form.is_valid():
			self.object_list = form.filter_queryset(request, self.object_list)

		context = self.get_context_data(form=form, object_list=self.object_list)
		return self.render(request, context)

@login_required(redirect_field_name=None)
@user_passes_test(lambda u: hasattr(u, 'student'), redirect_field_name=None,
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

# Faculty view of reports
######################################################################
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
@login_required
@user_passes_test(lambda u: hasattr(u, 'faculty'))
def faculty_view(request):

	reports = SubmitReport.objects.filter(courses__in=request.user.faculty.course_set.all()).distinct()
	reports.filter(status='APPROVED')
	form = ReportSearchForm(request.POST, user_type=request.user.faculty)
	courses = request.user.faculty.course_set.all()
	course_choices = []
	for course in courses:
		course_choices += [[course.pk, course]]

	df = pd.DataFrame(list(reports.values('first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary')))
	form.fields['courses'].choices = course_choices
	from django.template import Template, Context
	if form.is_valid():
		reports = form.filter_queryset(reports)
		df = pd.DataFrame(list(reports.values(
		'first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary')))
	if reports:
		table = df.to_html(escape=False, index=False,
		columns=['first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary'],
		formatters={
			'summary': (lambda s: '<abbr title=\"' + s + '\">Notes</abbr>'),
			# 'start_time': (lambda s: readable_datetime(s)),
			# 'end_time': (lambda s: readable_datetime(s)),
		})
	else:
		table = "No reports matched your search."

	return render(request, "faculty_view.html", {'form': form,
			'table': table,
		})

#View for TA
########################################################################## 
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy
@login_required
@user_passes_test(lambda u: hasattr(u, 'staff'))
def ta_view(request):
	
	reports = SubmitReport.objects.query_pending_reports()
	reports = reports.filter(courses__in=request.user.staff.courses.all()).distinct()
	ApproveReportFormSet = modelformset_factory(SubmitReport, form=ReportApproveForm, extra=0)


	if request.method == 'POST':
		form = ReportSearchForm(request.POST, user_type=request.user.staff)
		courses = request.user.staff.courses.all()
		course_choices = []
		for course in courses:
			course_choices += [[course.pk, course]]
		form.fields['courses'].choices = course_choices

		if form.is_valid():
			reports = form.filter_queryset(reports)

		import pickle
		request.session['search_results'] = pickle.dumps(reports.query)

		return HttpResponseRedirect('/accounts/ta_search_results/')
	else:
		form = ReportSearchForm(request.POST, user_type=request.user.staff)
		courses = request.user.staff.courses.all()
		course_choices = []
		for course in courses:
			course_choices += [[course.pk, course]]
		form.fields['courses'].choices = course_choices

		report_forms = ApproveReportFormSet(queryset=reports)

		return render(request, "ta_view.html", {'form': form,
				'report_forms': report_forms,
			})

@login_required
@user_passes_test(lambda u: hasattr(u, 'staff'))
def ta_results_view(request):
	import pickle
	ApproveReportFormSet = modelformset_factory(SubmitReport, form=ReportApproveForm, extra=0)
	reports = SubmitReport.objects.query_pending_reports().filter(courses__in=request.user.staff.courses.all()).distinct()
	reports.query = pickle.loads(request.session['search_results'])
	print reports
	if request.method == 'POST':
		report_forms = ApproveReportFormSet(request.POST, queryset=reports)

		if report_forms.is_valid():
			report_forms.save()
			reports.filter(status__exact='PENDING')
		return render(request, "ta_search_results.html", {'formset': report_forms,})
	else:
		report_forms = ApproveReportFormSet(queryset=reports)
		print report_forms

		return render(request, "ta_search_results.html", {'formset': report_forms,})

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
		auth.login(request, user)
		if hasattr(user, 'student'):
			return HttpResponseRedirect('/accounts/student_view/')
		if hasattr(user, 'faculty'):
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
@user_passes_test(lambda u: hasattr(u, 'student'))
def student_logged_in_view(request):
	"""Homepage for logged in users"""
	return render(request, 'loggedin.html',
		{'username': request.user.username, 'is_TA': hasattr(request.user, "staff"),
		'is_Student': hasattr(request.user, 'student')})


def invalid_login_view(request):
	"""Page for users who have not successfully logged in"""
	return render(request, 'invalid_login.html')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_home_view(request):
	"""Homepage for logged in admin"""
	return render(request, 'admin_loggedin.html',
		{'username': request.user.username})

#Views for doing the actual stuff that users want to do
##########################################################################

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_partners_view(request):
	'''Page for adding partners'''
	form = AddPartnerForm(request.POST or None)
	if form.is_valid():
		save_form = form.save(commit=False)
		save_form.save()
		if '_add_another' in request.POST:
			return HttpResponseRedirect('/admin/add_partner/')
		return HttpResponseRedirect('/admin/home/')
	return render(request, "add_partner.html", {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser or hasattr(u, 'staff'))
def add_student_view(request):
	'''Page for adding students'''
	form = AddStudentForm(request.POST or None)
	if form.is_valid():
		user = form.save()
		user.set_password(form.cleaned_data['password'])
		user.save()
		student = Student.objects.create(user=user,
			grad_year=form.cleaned_data['grad_year'])
		student.courses = form.cleaned_data['courses']
		student.save()
		if form.fields['is_TA'] == True:
			TA = Staff(user=user, courses = form.cleaned_data['courses'])
		print "Student made"
		send_mail('Service Learning Registration',
			"""You have been registered Northeastern Service Learning to report hours for your service learning class.
your current password is: """ + form.cleaned_data['password'] + '\n' +
			""" Please log in to the service learning hours reporting website to change your password""",
			'servicelearningadmin@nusl.com', [user.email,])

		if '_add_another' in request.POST:
			return HttpResponseRedirect('/admin/add_student/')
		return HttpResponseRedirect('/admin/home/')
	return render(request, "add_student.html", {'form': form,})



@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_faculty_view(request):
	'''Page for adding faculty'''
	form = AddFacultyForm(request.POST or None)
	if form.is_valid():
		user = form.save()
		user.set_password(form.cleaned_data['password'])
		user.save()
		faculty = Faculty.objects.create(user=user)
		faculty.save()
		print "Faculty made"
		send_mail('Service Learning Registration',
			"""You have been registered Northeastern Service Learning to view reported hours for your service learning class.
your current password is: """ + form.cleaned_data['password'] + '\n' +
			""" Please log in to the service learning hours reporting website to change your password""",
			'servicelearningadmin@nusl.com', [user.email,])

		if '_add_another' in request.POST:
			return HttpResponseRedirect('/admin/add_faculty/')
		return HttpResponseRedirect('/admin/home/')
	return render(request, "add_faculty.html", {'form': form,})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_course_view(request):
	'''Page for adding faculty'''
	form = AddCourseForm(request.POST or None)
	if form.is_valid():
		course = form.save()
		print "Faculty made"
		send_mail('Service Learning Registration',
			"Your course(" + course.__unicode__() + ") has been added to Northeastern Service Learning's hours reporting database.",
			'servicelearningadmin@nusl.com', [course.instructor.user.email,])

		if '_add_another' in request.POST:
			return HttpResponseRedirect('/admin/add_course/')
		return HttpResponseRedirect('/admin/home/')
	return render(request, "add_course.html", {'form': form,})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_view(request):
	reports = SubmitReport.objects.all()
	form = ReportSearchForm(request.POST)
	courses = Course.objects.all()
	course_choices = []
	for course in courses:
		course_choices += [[course.pk, course]]

	df = pd.DataFrame(list(reports.values('pk', 'first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary')))
	form.fields['courses'].choices = course_choices
	if form.is_valid():
		reports = form.filter_queryset(reports)
		df = pd.DataFrame(list(reports.values(
		'first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary')))
	if reports:
		table = df.to_html(escape=False, index=False,
		columns=['first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'summary'],
		formatters={
			'summary': (lambda s: '<abbr title=\"' + s + '\">Notes</abbr>'),
			# 'start_time': (lambda s: readable_datetime(s)),
			# 'end_time': (lambda s: readable_datetime(s)),
		})
	else:
		table = "No reports matched your search."

	return render(request, "admin_view.html", {'form': form,
			'table': table,
		})
