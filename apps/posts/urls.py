from django.urls import path

from apps.posts import views

app_name = 'posts'
urlpatterns = [
    path('latest/', views.LatestPostListView.as_view(), name='latest'),
    path('search/', views.PostSearchListAPIView.as_view(), name='search'),
    path('draft/', views.UserDraftPostListAPIView.as_view(), name='user_draft_posts'),
    path('user/<str:username>/', views.UserPostListAPIView.as_view(), name='user_published_posts'),

    path('create/', views.PostCreateAPIView.as_view(), name='create'),
    path('update/<str:hash>/', views.PostUpdateAPIView.as_view(), name='update'),
    path('publish/<str:hash>/', views.PublishPostAPIView.as_view(), name='publish'),
    path('draft/<str:hash>/', views.DraftPostAPIView.as_view(), name='draft'),
    path('delete/<str:hash>/', views.PostDeleteAPIView.as_view(), name='delete'),

    path('like/<str:hash>/', views.PostLikeAPIView.as_view(), name='like'),

    path('<slug:slug>/', views.PostRetrieveAPIView.as_view(), name='detail'),
]
