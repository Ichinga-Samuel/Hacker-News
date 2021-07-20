from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import UserCreationView, UserView, activate
from .forms import UserLoginForm, ResetPasswordForm, PasswordChange

app_name = 'user'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(authentication_form=UserLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', UserCreationView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(success_url=reverse_lazy('user:reset_done'), form_class=ResetPasswordForm,
                    template_name='user/password_reset_form.html', html_email_template_name="user/password_reset_email.html",  email_template_name="user/password_reset_email.html",  subject_template_name="user/password_reset_subject.txt"), name='reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name="user/password_reset_done.html"), name='reset_done'),
    path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('user:login'), form_class=PasswordChange, template_name="user/password_reset_confirm.html"), name='password_reset'),
    path('profile/<int:pk>/', UserView.as_view(), name='user_profile')
]
