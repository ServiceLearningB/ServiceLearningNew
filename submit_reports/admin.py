from django.contrib import admin

# Register your models here.
from .models import SubmitReport, Student, Faculty, Partner, Course, Staff, AdminStaff

class SubmitReportAdmin(admin.ModelAdmin):
	class Meta:
		model = SubmitReport
	filter_horizontal = ('courses',)

class StudentAdmin(admin.ModelAdmin):
	class Meta:
		model = Student
	filter_horizontal = ('courses',)

class FacultyAdmin(admin.ModelAdmin):
	class Meta:
		model = Faculty

class PartnerAdmin(admin.ModelAdmin):
	class Meta:
		model = Partner

class CourseAdmin(admin.ModelAdmin):
	class Meta:
		model = Course

class StaffAdmin(admin.ModelAdmin):
	class Meta:
		model = Staff

class AdminStaffAdmin(admin.ModelAdmin):
	class Meta:
		model = AdminStaff

admin.site.register(SubmitReport, SubmitReportAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Partner, PartnerAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(AdminStaff, AdminStaffAdmin)