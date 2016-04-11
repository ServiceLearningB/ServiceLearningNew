from django import forms
from django.forms import MultipleChoiceField
from django.forms import Textarea, ModelForm, widgets, RadioSelect, CheckboxSelectMultiple
from .models import SubmitReport, Partner
from django.db import models
from django.contrib.auth.models import User

class SubmitReportForm(forms.ModelForm):
	error_css_class = 'error'
	required_css_class = 'required'
	class Meta:
		model = SubmitReport
		fields = ['start_time', 'end_time', 'courses', 'service_type', 'summary']
		#exclude = ['submitter', 'status']
		widgets = {
			'summary': Textarea(attrs={'cols': 50, 'rows': 3}),
			'service_type': RadioSelect(),
			'courses': CheckboxSelectMultiple(),
		}

		def clean(self):
			cleaned_data = super(SubmitReportForm, self).clean()
			start_time = cleaned_data['start_time']
			end_time = cleaned_data['end_time']

			if (end_time <= start_time):
				raise forms.ValidationError("Start time must come before end time.")


class AddPartnerForm(forms.ModelForm):
	class Meta:
		model = Partner
		fields = ['name', 'is_active']

class AddStudentForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name']

class ReportSearchForm(forms.Form):
	first_name = forms.CharField(label='First Name', required=False)
	last_name = forms.CharField(label='Last Name', required=False)

	def filter_queryset(self, request, queryset):
		temp = queryset
		if self.cleaned_data['first_name']:
			temp = temp.filter(first_name__icontains=self.cleaned_data['first_name'])
			print queryset
		if self.cleaned_data['last_name']:
			temp = temp.filter(last_name__icontains=self.cleaned_data['last_name'])
		return temp
