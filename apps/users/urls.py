from django.urls import path
from . import views
from apps.users.views import UserLoginView

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
]
