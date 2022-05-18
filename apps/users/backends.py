from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from apps.utils.otp import verify_otp

UserModel = get_user_model()


class OTPModelBackend(ModelBackend):
    """
    Authenticate by otp code verifier.
    """

    def authenticate(self, request, username=None, email=None, otp_code=None, **kwargs):
        if otp_code is None:
            return

        try:
            user = UserModel.objects.get(
                Q(username=username) | Q(email=email)
            )
        except UserModel.DoesNotExist:
            return

        if verify_otp(user.id, otp_code):
            return user
