from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, PostViewSet, CommentViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'comments', CommentViewSet, basename='comments')

# urlpatterns = router.urls
urlpatterns = [
    path('', include(router.urls)),
    # Other URL patterns if any
]