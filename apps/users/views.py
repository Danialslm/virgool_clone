from django.contrib.auth import login, logout, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import (
    GenericAPIView, ListAPIView, RetrieveUpdateAPIView
)
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users import serializers
from apps.core.paginators import BaseResultsPagination

UserModel = get_user_model()


class LoginAPIView(GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_email = serializer.validated_data['user'].email

        # we need to access the user email in verification step
        request.session['user_email'] = user_email

        msg = _(
            f'Verification code for email {user_email} submitted.'
        )
        return Response({'detail': msg})


class LoginVerificationAPIView(GenericAPIView):
    serializer_class = serializers.EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)
        return Response({'success': True})


class SignupAPIView(GenericAPIView):
    serializer_class = serializers.SignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_email = serializer.validated_data['email']

        # we need to access the user email in verification step
        request.session['user_email'] = user_email
        msg = _(
            f'Verification code for email {user_email} submitted.'
        )

        return Response({'success': True, 'detail': msg})


class SignupVerificationAPIView(GenericAPIView):
    serializer_class = serializers.EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user.is_active = True
        user.save(update_fields=['is_active'])
        login(request, user)
        return Response({'success': True})


class LogoutAPIView(APIView):
    """
    Logout user by POST method.
    """

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({'detail': _('Successfully logged out.')})


class ProfileAPIView(RetrieveUpdateAPIView):
    """
    Return user details.

    If the given username was for logged-in user,
    it prevent querying again for getting user.
    """
    serializer_class = serializers.UserDetailsSerializer
    lookup_field = 'username'
    queryset = UserModel.objects.all()

    def get_me(self):
        return self.request.user

    def initial(self, request, *args, **kwargs):
        # for unsafe methods, user must be authenticated
        if request.method not in SAFE_METHODS:
            self.permission_classes = (IsAuthenticated,)

        super().initial(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # user can't update another user profile
        if kwargs.get(self.lookup_field) != request.user.username:
            raise MethodNotAllowed(
                method=request.method,
                detail=_(f'Method "{request.method}" only allowed your profile.')
            )

        self.get_object = self.get_me
        return super().update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if kwargs.get(self.lookup_field) == request.user.username:
            self.get_object = self.get_me
        return super().retrieve(request, *args, **kwargs)


class UserSearchListAPIView(ListAPIView):
    """
    Search in users and return result list.
    """
    serializer_class = serializers.UserSearchListSerializer
    pagination_class = BaseResultsPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return UserModel.objects.search(query)
