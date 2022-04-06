from django.urls import path

from apps.users import views

app_name = 'users'
urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('login-verification/', views.LoginVerificationAPIView.as_view(), name='login_verification'),
    path('signup/', views.SignupAPIView.as_view(), name='signup'),
    path('signup-verification/', views.SignupVerificationAPIView.as_view(), name='signup_verification'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),

    path('search/', views.UserSearchListAPIView.as_view(), name='search'),

    path('<str:username>/', views.ProfileAPIView.as_view(), name='profile'),
]
