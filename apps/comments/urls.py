from django.urls import path

from apps.comments import views

app_name = 'comments'
urlpatterns = [
    path('post/<str:hash>/', views.PostCommentListAPIView.as_view(), name='post_comments'),
    path('replies/<int:parent_id>/', views.CommentReplyListAPIView.as_view(), name='replies'),

    path('add/<str:post_hash>/', views.PostCommentCreateAPIView.as_view(), name='add'),
    path('delete/<int:pk>/', views.PostCommentDestroyAPIView.as_view(), name='delete'),
]
