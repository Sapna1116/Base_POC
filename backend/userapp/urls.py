from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    # SearchUserView,
    # UserLoggedDataView,
)

urlpatterns = [
    # path('users-search/', SearchUserView.as_view(), name='users-search'),
    # path('user-logged/', UserLoggedDataView.as_view(), name='users-logged'),
    # ????
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('test/', views.testEndPoint, name='test'),
    # path('', views.getRoutes),
]