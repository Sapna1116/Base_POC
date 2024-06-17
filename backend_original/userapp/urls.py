from django.urls import path

from .views import (
    SearchUserView,
    UserLoggedDataView,
    PostLikeView,
    PostRemoveLikeView,
    PostDislikeView,
    PostRemoveDislikeView,
    CommentLikeView,
    CommentRemoveLikeView,
    CommentDislikeView,
    CommentRemoveDislikeView,
)

urlpatterns = [
    path('users-search/', SearchUserView.as_view(), name='users-search'),
    path('user-logged/', UserLoggedDataView.as_view(), name='users-logged'),
    # USER-POST
    path('posts/<int:postId>/like/', PostLikeView.as_view(), name='post-like'),
    path('posts/<int:postId>/remove-like/', PostRemoveLikeView.as_view(), name='post-remove-like'),
    path('posts/<int:postId>/dislike/', PostDislikeView.as_view(), name='post-dislike'),
    path('posts/<int:postId>/remove-dislike/', PostRemoveDislikeView.as_view(), name='post-remove-dislike'),
    # USER-COMMENT
    path('comments/<int:commentId>/like/', CommentLikeView.as_view(), name='comment-like'),
    path('comments/<int:commentId>/remove-like/', CommentRemoveLikeView.as_view(), name='comment-remove-like'),
    path('comments/<int:commentId>/dislike/', CommentDislikeView.as_view(), name='comment-dislike'),
    path('comments/<int:commentId>/remove-dislike/', CommentRemoveDislikeView.as_view(), name='comment-remove-dislike'),
]
