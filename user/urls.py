from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UserCreationView, UserView
from .forms import UserLoginForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(authentication_form=UserLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', UserCreationView.as_view(), name='signup'),
    path('profile/<int:pk>/', UserView.as_view(), name='user_profile')
]
