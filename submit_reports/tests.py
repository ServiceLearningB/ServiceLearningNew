from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from submit_reports import models
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class StudentUserTestCase(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username='testname1', password='testpassword1',
			first_name='Foo', last_name='Bar')

	def test_student_creation(self):
		# With User
		self.student = models.Student.objects.create_student(self.user, 12345, '2018')
		self.assertEqual(self.user, self.student.user)
		self.assertEqual(self.user.first_name, self.student.first_name)
		self.assertEqual(self.user.last_name, self.student.last_name)
		self.assertEqual(self.student.nuid, 12345)
		self.assertEqual(self.student.grad_year, '2018')
		# Without user
		self.student2 = models.Student.objects.create_student_without_user("test", "test", 98765, "2019")
		self.assertEqual(self.student2.nuid, 98765)
		self.assertEqual(self.student2.grad_year, '2019')

class StudentSubmitViewTestCase(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.user = User.objects.create_user(username='testname1', password='testpassword1',
			first_name='Foo', last_name='Bar')
		
	def test_access_denied_to_anon(self):
		response = self.client.get(reverse('submit_page'), follow=True)
		self.assertRedirects(response, reverse('login_page'))
		response = self.client.get(reverse('submit_page'), follow=True)
		self.assertRedirects(response, reverse('login_page'))