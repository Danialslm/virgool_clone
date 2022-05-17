from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework.reverse import reverse

from apps.users import views


class UserUrlsTest(SimpleTestCase):
    def test_login_url(self):
        url = reverse('users:login')
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.LoginAPIView.__name__,
        )

    def test_login_verification_url(self):
        url = reverse('users:login_verification')
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.LoginVerificationAPIView.__name__,
        )

    def test_signup_url(self):
        url = reverse('users:signup')
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.SignupAPIView.__name__,
        )

    def test_signup_verification_url(self):
        url = reverse('users:signup_verification')
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.SignupVerificationAPIView.__name__,
        )

    def test_logout_url(self):
        url = reverse('users:logout')
        view = resolve(url)
        self.assertIs(
            view.func.view_class.__name__,
            views.LogoutAPIView.__name__,
        )

    def test_profile_url(self):
        url = reverse('users:profile', kwargs={'username': 'sample'})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.ProfileAPIView.__name__,
        )