import json
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.views.generic import ListView, TemplateView, DetailView, CreateView
from django.contrib.auth import get_user_model, decorators

from .models import Story, StoryComments
from jobs.models import Job

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'news/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stories'] = Story.objects.exclude(title__iregex=r'^(Ask HN|Show HN)').order_by('-score', '-time')[:5]
        context['jobs'] = Job.objects.all().order_by('-time')[:5]
        context['asks'] = Story.objects.filter(title__icontains='Ask HN').order_by('-time', '-score')[:5]
        context['shows'] = Story.objects.filter(title__icontains='Show HN').order_by('-time', '-score')[:5]
        return context


class StoryListView(ListView):
    template_name = 'news/stories.html'
    context_object_name = 'stories'
    paginate_by = 10

    def get_queryset(self):
        stories = Story.objects.exclude(title__iregex=r'^(Ask HN|Show HN)').order_by('-score', '-time')
        return stories


class AskStoryListView(ListView):
    template_name = 'news/ask_stories.html'
    context_object_name = 'stories'
    paginate_by = 10

    def get_queryset(self):
        stories = Story.objects.filter(title__icontains='Ask HN').order_by('-time', '-score')
        return stories


class ShowStoryListView(ListView):
    template_name = 'news/show_stories.html'
    context_object_name = 'stories'
    paginate_by = 10

    def get_queryset(self):
        stories = Story.objects.filter(title__icontains='Show HN').order_by('-time', '-score')
        return stories


class StoryDetailView(DetailView):
    template_name = 'news/story_detail.html'
    context_object_name = 'story'
    model = Story

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stories'] = Story.objects.all().order_by('-score', '-time')[:5]
        return context


class SearchView(TemplateView):
    template_name = 'news/search_results.html'

    def get_results(self):
        all_ = self.request.GET.get('all', '')
        search = self.request.GET.get('search', '')
        ask = self.request.GET.get('ask', '')
        show = self.request.GET.get('show', '')
        job = self.request.GET.get('job', '')

        results = {}
        if all_:
            results['stories'] = Story.objects.exclude(title__iregex=r'^(Ask HN|Show HN)').filter(Q(text__icontains=search) | Q(title__icontains=search))[:5]
            results['asks'] = Story.objects.filter(title__icontains='Ask HN').filter(Q(text__icontains=search) | Q(title__icontains=search))
            results['shows'] = Story.objects.filter(title__icontains='Show HN').filter(Q(text__icontains=search) | Q(title__icontains=search))
            results['jobs'] = Job.objects.filter(Q(text__icontains=search) | Q(title__icontains=search))[:5]
        else:
            results['stories'] = Story.objects.exclude(title__iregex=r'^(Ask HN|Show HN)').filter(
                Q(text__icontains=search) | Q(title__icontains=search))[:5]
            if ask:
                results['asks'] = Story.objects.filter(title__icontains='Ask HN').filter(Q(text__icontains=search) | Q(title__icontains=search))

            if show:
                results['shows'] = Story.objects.filter(title__icontains='Show HN').filter(Q(text__icontains=search) | Q(title__icontains=search))

            if job:
                results['jobs'] = Job.objects.filter(Q(text__icontains=search) | Q(title__icontains=search))[:5]

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = self.get_results()
        context['query'] = self.request.GET.get('search', '')
        if any(len(result) for result in results.values()):
            context = {**context, **results, 'null': False}
        else:
            context['null'] = True
        return context


@decorators.login_required()
@require_POST
def create_comment(request):
    body = json.loads(request.body)
    text = body.get('text')
    uid = body.get('user_id')
    comment = body.get('comment_id')
    story = body.get('story_id')
    obj = {}
    try:
        if text:
            obj['text'] = text
        else:
            raise ValueError

        by = User.objects.get(id=uid)
        obj['by'] = by
        if comment:
            comment = StoryComments.objects.get(id=comment)
            obj['comment'] = comment
        if story:
            story = Story.objects.get(id=story)
            obj['story'] = story
        comment = StoryComments(**obj)
        comment.save()
        return JsonResponse({'ok': True})
    except (User.DoesNotExist, Story.DoesNotExist, StoryComments.DoesNotExist, ValueError) as err:
        print(err)
        return HttpResponseBadRequest()
