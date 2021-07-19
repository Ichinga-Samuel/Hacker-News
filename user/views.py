import json
from django.db.models import Max
from django.http import JsonResponse
from django.views import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm

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
        return super().form_valid(form)


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
            return JsonResponse({'ok': True})
        except Exception as err:
            print(err)
            return JsonResponse({'ok': False})
