from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import UpdateView
from django.db.models import Count, Min, Max
from .forms import UserCreationForm
from .models import User


class UserCreateView(FormView):
    template_name = 'registration/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    slug_field = 'username'
    model = User
    login_url = reverse_lazy('login')
    fields = ('username', 'email', 'about')
    template_name = 'user_update_form.html'

    def test_func(self):
        return self.request.user == self.get_object()

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'slug': self.object.username})


class UserDetailView(DetailView):
    model = User
    template_name = 'user_detail.html'
    context_object_name = 'me'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alls = self.object.stories.all().order_by('created')
        rated = self.object.stories.order_by('-score')[0]
        context['rated'] = rated
        context['count'] = len(alls)
        context['recent'] = alls[0]
        return context
