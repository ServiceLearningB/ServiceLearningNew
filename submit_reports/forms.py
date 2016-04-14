from django import forms
from datetime import datetime
from django.forms import MultipleChoiceField
from django.forms import Textarea, ModelForm, TimeInput, DateInput, RadioSelect, CheckboxSelectMultiple
from .models import SubmitReport, Partner
from django.db import models
from django.contrib.auth.models import User

class SubmitReportForm(forms.ModelForm):

	start_time = forms.TimeField(input_formats=['%I:%M %p', '%H:%M'])
	end_time = forms.TimeField(input_formats=['%I:%M %p', '%H:%M'])

	class Meta:
		model = SubmitReport
		fields = ['start_time', 'end_time', 'start_date', 'end_date', 'courses', 'service_type', 'summary']

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

		if (datetime.combine(end_date, end_time) <= datetime.combine(start_date, start_time)):
			raise forms.ValidationError("Start time must come before end time.")
		return self.cleaned_data

	def __init__(self, *args, **kwargs):
		super(SubmitReportForm, self).__init__(*args, **kwargs)
		self.fields['summary'].label = 'Notes'


class AddPartnerForm(forms.ModelForm):
	class Meta:
		model = Partner
		fields = ['name', 'is_active']

class AddStudentForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name']

class ReportSearchForm(forms.ModelForm):
	class Meta:
		model = SubmitReport
		fields = ['first_name', 'last_name', 'start_date', 'start_time', 'end_date', 'end_time', 'courses', 'service_type', 'status']
		widgets = {
			'start_time': TimeInput(),
			'end_time': TimeInput(),
			'start_date': DateInput(attrs={'class': 'datepicker'}),
			'end_date': DateInput(attrs={'class': 'datepicker'}),
			'courses': CheckboxSelectMultiple(),
			'service_type': RadioSelect(),
		}

	def __init__(self, *args, **kwargs):

		user_type = kwargs.pop('user_type')


		super(ReportSearchForm, self).__init__(*args, **kwargs)

		self.fields['courses'].choices = user_type.course_set.all()
		for key in self.fields:
			self.fields[key].required = False

	def filter_queryset(self, queryset):
		temp = queryset
		if self.cleaned_data['first_name']:
			temp = temp.filter(first_name__icontains=self.cleaned_data['first_name'])
			print queryset
		if self.cleaned_data['last_name']:
			temp = temp.filter(last_name__icontains=self.cleaned_data['last_name'])
		if self.cleaned_data['start_date'] and self.cleaned_data['start_time']:
			temp = temp.filter(start_date__gte=self.cleaned_data['start_date']).filter(start_time__gte=self.cleaned_data['start_time'])
		if self.cleaned_data['end_date'] and self.cleaned_data['end_time']:
			temp = temp.filter(end_date__gte=self.cleaned_data['end_date']).filter(start_time__gte=self.cleaned_data['end_date'])
		if self.cleaned_data['courses']:
			temp2 = SubmitReport.objects.none()
			for choice in self.cleaned_data['courses']:
				temp2 = temp2 | temp.filter(courses__in=[choice])
			temp = temp2
		if self.cleaned_data['service_type']:
			print('got here')
			temp = temp.filter(service_type__exact=self.cleaned_data['service_type'])

		return temp
