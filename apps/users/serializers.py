from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.utils import otp

UserModel = get_user_model()


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            'id', 'email', 'full_name',
            'avatar', 'biography', 'username',
        )
        read_only_fields = ('email',)


class UserSearchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'avatar')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True, min_length=3)
    email = serializers.EmailField(required=False, allow_blank=True)

    @staticmethod
    def get_user(username, email):
        return UserModel.objects.filter(
            Q(username=username) |
            Q(email=email)
        ).only('is_active', 'email').first()

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = _('User account is disabled.')
            raise ValidationError(msg)

    @staticmethod
    def send_verification_code(user):
        code = otp.create_new_otp(user.id)

        # todo: real template message
        user.email_user('Email-address verification', f'Your login verification code is {code}')

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')

        if not username and not email:
            raise ValidationError(_('Please enter your username or email address.'))

        user = self.get_user(username, email)
        if not user:
            raise ValidationError(_('Unable to login with provided credentials.'))

        # did we get back an active user?
        self.validate_auth_user_status(user)
        # send verification code to user email
        self.send_verification_code(user)

        attrs['user'] = user
        return attrs


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()

    @staticmethod
    def get_or_create_user(email):
        """
        Get or create user by given email.
        Raise validation error if any active user have this email.
        """
        user, created = UserModel.objects.get_or_create(
            email=email,
            defaults={
                'is_active': False,
            },
        )
        if user.is_active:
            raise ValidationError({'email': _('A user with that email address already exists.')})
        return user

    def create(self, validated_data):
        user = validated_data['user']

        code = otp.create_new_otp(user.id)
        # todo: real template message
        user.email_user('Email-address verification', f'Your login verification code is {code}')
        return user

    def validate(self, attrs):
        attrs['user'] = self.get_or_create_user(email=attrs.get('email'))
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    verification_code_validator = RegexValidator(
        regex=r'^[0-9]{6}$',
        message=_('The verification code is invalid.'),
    )

    verification_code = serializers.CharField(validators=[verification_code_validator])

    def get_user_email_from_session(self):
        user_email = self.context['request'].session.get('user_email')
        if not user_email:
            raise ValidationError(_('The session does not have required data.'))
        return user_email

    @staticmethod
    def verify_code(user, code):
        valid = otp.verify_otp(user.id, code)
        if not valid:
            raise ValidationError(_('The verification code is incorrect or has expired.'))

    @staticmethod
    def get_user_by_email(email):
        try:
            return UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

    def validate(self, attrs):
        user_email = self.get_user_email_from_session()
        user = self.get_user_by_email(user_email)
        if not user:
            raise ValidationError(_('The code is incorrect or has expired.'))

        code = attrs.get('verification_code')
        self.verify_code(user, code)

        attrs['user'] = user
        return attrs
