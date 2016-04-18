from django import forms
from datetime import datetime, timedelta
from django.forms import MultipleChoiceField, BooleanField, Textarea, ModelForm, TimeInput, DateInput, RadioSelect, CheckboxSelectMultiple, ModelMultipleChoiceField, ModelChoiceField
from .models import SubmitReport, Partner, Course
from django.db import models
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple


class SubmitReportForm(forms.ModelForm):

	start_time = forms.TimeField(input_formats=['%I:%M %p', '%H:%M'])
	end_time = forms.TimeField(input_formats=['%I:%M %p', '%H:%M'])

	class Meta:
		model = SubmitReport
		exclude= ['submitter', 'status']
		widgets = {
			'summary': Textarea(attrs={'cols': 50, 'rows': 3}),
			'service_type': RadioSelect(),
			'courses': CheckboxSelectMultiple(),
			'start_time': TimeInput(),
			'end_time': TimeInput(),
			'start_date': DateInput(attrs={'class': 'datepicker'}),
			'end_date': DateInput(attrs={'class': 'datepicker'}),
		}

	def clean(self):
		cleaned_data = super(SubmitReportForm, self).clean()
		start_time = cleaned_data['start_time']
		end_time = cleaned_data['end_time']
		start_date = cleaned_data['start_date']
		end_date = cleaned_data['end_date']
		twelve_hours = timedelta(hours=12)		
		
		if (datetime.combine(end_date, end_time) <= datetime.combine(start_date, start_time)):
			raise forms.ValidationError("Start time must come before end time.")
		if ((datetime.combine(end_date, end_time) - datetime.combine(start_date, start_time)) > twelve_hours):
			raise forms.ValidationError("Max allowed duration is 12 hours.")
		return self.cleaned_data

	def __init__(self, *args, **kwargs):
		super(SubmitReportForm, self).__init__(*args, **kwargs)
		self.fields['summary'].label = 'Notes'


class AddPartnerForm(forms.ModelForm):
	class Meta:
		model = Partner
		fields = ['name', 'is_active']

class AddStudentForm(forms.ModelForm):
	is_TA = BooleanField(label="Is this student a TA")
	courses = ModelMultipleChoiceField(queryset=Course.objects.all(),
		widget=FilteredSelectMultiple(("Course"), False))
	grad_year = forms.IntegerField(min_value=datetime.now().year,
		max_value=datetime.now().year + 4,
		error_messages={'invalid': "Not a valid graduation year",
		'required': "No graduation year entered",})

	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email']

	def __init__(self, *args, **kwargs):
		super(AddStudentForm, self).__init__(*args, **kwargs)
		for key in self.fields:
	   		self.fields[key].required = True

	def clean(self):
		cleaned_data = super(AddStudentForm, self).clean()
		cleaned_data['password'] = User.objects.make_random_password(length=10,
			allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
		print cleaned_data['password']




class AddFacultyForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email']

	def __init__(self, *args, **kwargs):
		super(AddFacultyForm, self).__init__(*args, **kwargs)
		for key in self.fields:
	   		self.fields[key].required = True

	def clean(self):
		cleaned_data = super(AddFacultyForm, self).clean()
		cleaned_data['password'] = User.objects.make_random_password(length=10,
			allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
		print cleaned_data['password']


class AddCourseForm(forms.ModelForm):
	class Meta:
		model = Course
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super(AddCourseForm, self).__init__(*args, **kwargs)
		for key in self.fields:
	   		self.fields[key].required = True


class ReportSearchForm(forms.ModelForm):
	class Meta:
		model = SubmitReport
		fields = '__all__'
		widgets = {
			'start_time': TimeInput(),
			'end_time': TimeInput(),
			'start_date': DateInput(attrs={'class': 'datepicker'}),
			'end_date': DateInput(attrs={'class': 'datepicker'}),
			'courses': FilteredSelectMultiple(("Course"), False),
			'service_type': RadioSelect(),
		}

	def __init__(self, *args, **kwargs):
		user_type = None
		if 'user_type' in kwargs:
			user_type = kwargs.pop('user_type')

		super(ReportSearchForm, self).__init__(*args, **kwargs)
		if user_type is not None:
			self.fields['courses'].choices = user_type.course_set.all()
		else:
			self.fields['courses'].choices = Course.objects.all()
		for key in self.fields:
			self.fields[key].required = False

	def filter_queryset(self, queryset):
		temp = queryset
		if self.cleaned_data['first_name']:
			temp = temp.filter(first_name__icontains=self.cleaned_data['first_name'])
			print queryset
		if self.cleaned_data['last_name']:
			temp = temp.filter(last_name__icontains=self.cleaned_data['last_name'])
		if self.cleaned_data['start_date']:
			temp = temp.filter(start_date__gte=self.cleaned_data['start_date'])
			if self.cleaned_data['start_time']:
				temp = temp.filter(start_time__gte=self.cleaned_data['start_time'])
		if self.cleaned_data['end_date']:
			temp = temp.filter(end_date__gte=self.cleaned_data['end_date'])
			if self.cleaned_data['end_time']:
				temp = temp.filter(start_time__gte=self.cleaned_data['end_date'])
		if self.cleaned_data['courses']:
			temp2 = SubmitReport.objects.none()
			for choice in self.cleaned_data['courses']:
				temp2 = temp2 | temp.filter(courses__in=[choice])
			temp = temp2
		if self.cleaned_data['service_type']:
			print('got here')
			temp = temp.filter(service_type__exact=self.cleaned_data['service_type'])
		if self.cleaned_data['status']:
			temp = temp.filter(status__exact=self.cleaned_data['service_type'])
		if self.cleaned_data['partner']:
			temp = temp.filter(partner__exact=self.cleaned_data['partner'])
		return temp
