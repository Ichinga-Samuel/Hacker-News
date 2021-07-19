from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django import forms

attrs = {'class': 'form-control', 'placeholder': '', 'required': True}
User = get_user_model()


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(widget=forms.TextInput(attrs=attrs))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}))

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': (
            "Please enter the correct %(username)s and password"
            " Note that both fields may be case-sensitive."
        ),
    }
    required_css_class = 'required'


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs=attrs))
    email = forms.EmailField(max_length=254, help_text='Enter a valid email address.',
                             widget=forms.EmailInput(attrs=attrs))
    password1 = forms.CharField(help_text='Your password must be 8-20 characters long, and must contain'
                                          ' numeric, lower and upper case letters',
                                widget=forms.PasswordInput(attrs=attrs))
    password2 = forms.CharField(help_text="Enter the same password as before, for verification.", widget=forms.PasswordInput(attrs=attrs))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", )