from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from apps.users import views
from apps.utils import otp

UserModel = get_user_model()
factory = APIRequestFactory()


def add_session(request):
    """ Add session store to given request object. """
    middleware = SessionMiddleware('')
    middleware.process_request(request)
    request.session.save()


class UserLoginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.validation_code = None

    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )

    def test_login_with_username(self):
        view = views.LoginAPIView.as_view()
        request = factory.post('/users/login/', data={'username': self.user.username})
        add_session(request)

        response = view(request)
        self.assertContains(response, 'Verification code for email sample@sample.sample submitted.')

    def test_login_with_email(self):
        view = views.LoginAPIView.as_view()
        request = factory.post('/users/login/', data={'email': self.user.email})
        add_session(request)

        response = view(request)
        self.assertContains(response, 'Verification code for email sample@sample.sample submitted.')

    def test_login_verification(self):
        verification_code = otp.create_new_otp(self.user.id)
        view = views.LoginVerificationAPIView.as_view()
        request = factory.post('/users/login-verification/', data={'verification_code': verification_code})
        add_session(request)
        request.session['user_email'] = self.user.email

        response = view(request)
        self.assertEqual(response.data, {'success': True})
        self.assertEqual(request.user.id, self.user.id)


class UserSignupTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample', is_active=False,
        )

    def test_signup(self):
        view = views.SignupAPIView.as_view()
        request = factory.post('/users/signup/', data={'email': self.user.email})
        add_session(request)

        response = view(request)
        self.assertContains(response, 'Verification code for email sample@sample.sample submitted.')

    def test_signup_verification(self):
        verification_code = otp.create_new_otp(self.user.id)
        view = views.SignupVerificationAPIView.as_view()
        request = factory.post('/users/signup-verification/', data={'verification_code': verification_code})
        add_session(request)
        request.session['user_email'] = self.user.email

        response = view(request)
        self.assertEqual(response.data, {'success': True})
        self.assertEqual(request.user.id, self.user.id)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class UserViewsTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )

    def test_logout_view(self):
        view = views.LogoutAPIView.as_view()
        request = factory.post('/users/logout/')
        add_session(request)

        response = view(request)
        self.assertContains(response, 'Successfully logged out.')

    def test_user_profile(self):
        view = views.ProfileAPIView.as_view()
        request = factory.get('/users/')

        response = view(request, username=self.user.username)
        self.assertContains(response, self.user.email)

    def test_update_profile(self):
        view = views.ProfileAPIView.as_view()
        request = factory.patch('/users/', data={'username': 'sample_username'})
        force_authenticate(request, user=self.user)

        response = view(request, username=self.user.username)
        self.user.refresh_from_db()
        self.assertEqual(response.data['username'], self.user.username)

    def test_update_profile_failure(self):
        another_user = UserModel.objects.create_user(
            email='another@sample.sample',
        )
        view = views.ProfileAPIView.as_view()
        request = factory.patch('/users/', data={'username': 'sample_username'})
        force_authenticate(request, user=another_user)

        response = view(request, username=self.user.username)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
