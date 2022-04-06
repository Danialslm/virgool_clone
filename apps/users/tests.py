from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.reverse import reverse

from apps.users import views
from apps.users.models import User, get_email_username
from apps.utils import otp

UserModel = get_user_model()


class UserModelTestCase(TestCase):
    def test_custom_user_model(self):
        """ Check the custom user model is set correctly. """
        self.assertIs(UserModel, User)

    def test_user_creation(self):
        """ Check creation normal user and superuser. """
        info = {
            'email': 'test@test.localhost',
        }
        email_username = get_email_username(info['email'])
        # normal user
        user = UserModel.objects.create_user(**info)
        self.assertEqual(user.email, info['email'])
        # check that `full_name` and `username` is filled
        self.assertEqual(user.full_name, email_username)
        self.assertEqual(user.username, email_username)

        self.assertEqual(user.biography, '')
        self.assertEqual(user.avatar, 'default-avatar.jpg')
        # delete created user to avoid email duplicated error
        user.delete()

        # superuser
        admin = UserModel.objects.create_superuser(**info)
        self.assertEqual(admin.email, info['email'])
        # check that `full_name` and `username` is filled
        self.assertEqual(admin.full_name, email_username)
        self.assertEqual(admin.username, email_username)

        self.assertEqual(admin.biography, '')
        self.assertEqual(admin.avatar, 'default-avatar.jpg')


class UserViewsTestCase(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='test@test.localhost',
        )
        self.client.post(
            reverse('users:login'),
            data={
                'email': self.user.email,
            }
        )
        # create otp code to authenticate
        code = otp.create_new_otp(self.user.id)
        self.client.post(
            reverse('users:login_verification'),
            data={
                'verification_code': code,
            }
        )

    def test_login_view(self):
        url = reverse('users:login')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.LoginAPIView.__name__,
        )

        # login request with email and username
        response = self.client.post(url, data={'username': self.user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(url, data={'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # login verification
        url = reverse('users:login_verification')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.LoginVerificationAPIView.__name__,
        )

    def test_signup_view(self):
        url = reverse('users:signup')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.SignupAPIView.__name__,
        )

        response = self.client.post(url, data={'email': 'sample@localhost.test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # signup verification
        url = reverse('users:signup_verification')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.SignupVerificationAPIView.__name__,
        )

        created_user = User.objects.filter(email='sample@localhost.test').first()
        # create otp code to authorization
        code = otp.create_new_otp(created_user.id)
        response = self.client.post(
            url,
            data={
                'verification_code': code,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_view(self):
        url = reverse('users:logout')
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.LogoutAPIView.__name__,
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_view(self):
        url = reverse('users:profile', kwargs={'username': self.user.username})
        view = resolve(url)
        self.assertEqual(
            view.func.view_class.__name__,
            views.ProfileAPIView.__name__,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(
            url,
            content_type='application/json',
            data={
                'biography': 'test biography'
            }
        )
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.biography, 'test biography')

        # try to update user which is not logged-in
        url = reverse('users:profile', kwargs={'username': 'sample'})
        response = self.client.patch(
            url,
            content_type='application/json',
            data={
                'biography': 'test biography'
            }
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
