from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, View
from django.views.generic.edit import BaseFormView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from .models import Story, Comment
from .forms import CommentForm
from utils.pick_images import pick_image


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stories = Story.objects.order_by('created', '-score')
        context['latest'] = stories[:6]
        context['trending'] = stories.reverse()[:10]
        context['slides'] = lambda: pick_image('slides')
        context['post_landscapes'] = lambda: pick_image('post-landscapes')
        context['persons'] = lambda: pick_image('persons')
        context['stories'] = Story.objects.exclude(Q(title__icontains='Ask HN') | Q(title__icontains='Show HN')
                                              | Q(type__exact='job')).filter(type__exact='story').order_by('-score')[:10]

        context['asks'] = Story.objects.filter(title__icontains='Ask HN').order_by('created', '-score')[:10]
        context['shows'] = Story.objects.filter(title__icontains='Show HN').order_by('created', '-score')[:12]
        return context


def get_sidebar(queryset):
    context = dict()
    context['latest'] = Story.objects.all().order_by('created')[:7]
    context['popular'] = queryset.order_by('created')[:7]
    context['jobs'] = Story.objects.filter(type__exact='job').order_by('created', '-score')[:7]
    return context


class BaseDetailView(DetailView):
    template_name = 'story.html'
    context_object_name = 'story'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.object.type
        context['comments'] = self.object.comments.all()
        context['comment_form'] = CommentForm()
        context['slides'] = lambda: pick_image('slides')
        context['post_landscapes'] = lambda: pick_image('post-landscapes')
        context['persons'] = lambda: pick_image('persons')
        context |= get_sidebar(queryset=self.queryset)
        return context

    def post(self, request, *args, **kwargs):
        object_ = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.story = object_
            comment.save()
        return super().post(request, *args, **kwargs)
        # return self.get(request, *args, **kwargs)


class BaseListView(ListView):
    template_name = 'category.html'
    context_object_name = 'stories'
    ordering = ('created', '-score')
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = 'Tech'
        page = context['page_obj']
        context['pages'] = page.paginator.get_elided_page_range(page.number)
        context['slides'] = lambda: pick_image('slides')
        context['post_landscapes'] = lambda: pick_image('post-landscapes')
        context['persons'] = lambda: pick_image('persons')
        match self.__class__.__name__:
            case 'StoriesViews':
                category = 'Tech'

            case 'ShowView':
                category = 'Show HN'

            case 'AskView':
                category = 'Ask HN'

            case 'JobsView':
                category = 'Jobs'

        context['category'] = category
        context |= get_sidebar(queryset=self.get_queryset())
        return context


class StoriesView(BaseListView):
    def get_queryset(self):
        qs = (Story.objects.exclude(Q(title__icontains='Ask HN') | Q(title__icontains='Show HN') | Q(type__exact='job'))
              .filter(type__exact='story'))
        return qs


class ShowView(BaseListView):
    def get_queryset(self):
        qs = Story.objects.filter(title__icontains='Show HN', type__exact='story')
        return qs


class AskView(BaseListView):
    def get_queryset(self):
        qs = Story.objects.filter(title__icontains='Ask HN', type__exact='story')
        return qs


class SearchView(ListView):
    template_name = 'search-result.html'
    paginate_by = 5
    context_object_name = 'results'

    def get_queryset(self):
        query = self.request.GET.get('query', '')
        if len(query) < 3:
            return []
        return Story.objects.filter(Q(title__istartswith=query) | Q(text__icontains=query) | Q(title__icontains=query) |
                                    Q(user__username__icontains=query))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query', '')
        page = context['page_obj']
        context['query'] = query
        context['category'] = 'Search Results'
        context['pages'] = page.paginator.get_elided_page_range(page.number)
        context |= get_sidebar(Story.objects.all())
        return context


class JobsView(BaseListView):
    def get_queryset(self):
        qs = Story.objects.filter(type__exact='job')
        return qs


class JobView(BaseDetailView):
    queryset = Story.objects.filter(type__exact='job')


class StoryView(BaseDetailView):
    queryset = Story.objects.exclude(type__exact='job')


class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    fields = ('title', 'url', 'text')
    widgets = {}
    template_name = 'story_create_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.type = 'story'
        return super().form_valid(form)


class StoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Story
    fields = ('title', 'url', 'text')
    template_name = 'story_update_form.html'

    def test_func(self):
        return self.request.user == self.get_object().user or self.request.user.is_admin


class CommentCreateView(LoginRequiredMixin, BaseFormView):
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect(form.data['story_url'])

    def get_success_url(self):
        form = self.get_form()
        form.is_valid()
        return form.cleaned_data['story_url']


@login_required
def story_delete(request, type: str, pk: int):
    story = Story.objects.get(id=pk)
    story_owner = story.user
    user = request.user
    if user == story_owner or user.is_admin:
        story.delete()
    return redirect('stories')


@login_required
def comment_delete(request, story: int, pk: int):
    # story owner, admin and the comment owner can delete a comment
    user = request.user
    comment = Comment.objects.get(id=pk)
    story = Story.objects.get(id=story)
    story_owner = story.user
    comment_owner = comment.user
    if user == comment_owner or user == story_owner or user.is_admin:
        comment.delete()
    return redirect(story.get_absolute_url())
