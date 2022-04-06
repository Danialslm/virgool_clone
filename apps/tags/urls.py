from django.urls import path

from apps.tags import views

app_name = 'tags'
urlpatterns = [
    path('post/<str:hash>/', views.PostTagsAPIView.as_view(), name='post_tags'),
    path('search/', views.TagSearchListAPIView.as_view(), name='search'),

    path('<str:tag>/', views.TagPostListAPIView.as_view(), name='tag_posts'),
]
