import json
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.db.models import Max
from django.http import JsonResponse
from django.views import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm
from .tokens import account_activation_token

User = get_user_model()


class UserCreationView(FormView):
    form_class = UserRegistrationForm
    template_name = 'registration/signup.html'
    success_url = '/auth/login'

    def form_valid(self, form):
        # form.send_email()
        max_id = User.objects.aggregate(Max('id'))['id__max']
        user = form.save(commit=False)
        user.id = max_id + 1
        user.save()
        current_site = get_current_site(self.request)
        context1 = {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        }
        subject = 'Activate Your Hackers Digest Account'
        html_msg = render_to_string('user/activation_email.html', context1)
        message = render_to_string('user/activation_text.html', context1)
        try:
            user.email_user(subject, message, html_message=html_msg)
            messages.add_message(self.request, messages.INFO, 'An activation link has been sent to your email account')
            return super().form_valid(form)
        except Exception as e:
            messages.add_message(self.request, messages.WARNING, 'Unable to verify your email address please confirm your email and try again')
            return redirect('user:login')


class UserView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'user/profile.html'

    def test_func(self):
        return self.request.user.id == self.kwargs['pk']

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        data = json.loads(request.body)
        try:
            u = User.objects.filter(id=pk).update(**data)
            messages.add_message(request, messages.INFO, 'Profile Update Successful')
            return JsonResponse({'ok': True})
        except Exception as err:
            messages.add_message(request, messages.WARNING, 'Profile Update Unsuccessful')
            return JsonResponse({'ok': False})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.verified = True
        user.save()
        messages.add_message(request, messages.SUCCESS, 'congratulations Your account has been verified')
        return redirect('user:login')
    else:
        messages.add_message(request, messages.ERROR, 'Unable to verify you account please try again')
        return redirect('user:login')
