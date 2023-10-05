from django.urls import path

from .views import HomeView, StoriesView, AskView, ShowView, JobView, StoryView, JobsView, SearchView, StoryUpdateView,\
    StoryCreateView, CommentCreateView, story_delete, comment_delete

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('stories/', StoriesView.as_view(), name='stories'),
    path('stories/ask/', AskView.as_view(), name='ask'),
    path('stories/show/', ShowView.as_view(), name='show'),
    path('jobs/', JobsView.as_view(), name='jobs'),
    path('stories/search/', SearchView.as_view(), name='search'),
    path('stories/<str:type>/<int:pk>/', StoryView.as_view(), name='story-detail'),
    path('stories/delete/<str:type>/<int:pk>/', story_delete, name='story-delete'),
    path('stories/create/', StoryCreateView.as_view(), name='story-create'),
    path('stories/update/<str:type>/<int:pk>/', StoryUpdateView.as_view(), name='story-update'),
    path('jobs/<str:type>/<int:pk>/', JobView.as_view(), name='job-detail'),
    path('stories/comment/create/', CommentCreateView.as_view(), name='comment-create'),
    path('stories/comment/delete/<int:story>/<int:pk>/', comment_delete, name='comment-delete'),
    ]

