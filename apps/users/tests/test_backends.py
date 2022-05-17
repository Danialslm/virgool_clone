from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.utils import otp

UserModel = get_user_model()
factory = APIRequestFactory()


class AuthBackendTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            email='sample@sample.sample',
        )

    def test_authenticate(self):
        """ Test authentication with custom authentication backend. """
        request = factory.get('')
        otp_code = otp.create_new_otp(self.user.id)
        user = authenticate(request, username=self.user.username, otp_code=otp_code)

        self.assertIsNotNone(user)

    def test_authenticate_failure(self):
        request = factory.get('')
        user = authenticate(request, username=self.user.username, otp_code='invalid')

        self.assertIsNone(user)