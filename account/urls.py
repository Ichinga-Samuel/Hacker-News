from django.urls import path
from .views import UserCreateView, UserUpdateView, UserDetailView

urlpatterns = [
    path('signup/', UserCreateView.as_view(), name='signup'),
    path('edit/<str:slug>/', UserUpdateView.as_view(), name='edit-profile'),
    path('profile/<str:slug>/', UserDetailView.as_view(), name='profile'),
]
