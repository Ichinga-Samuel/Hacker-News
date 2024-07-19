from django.urls import path

from .views import HomeView, SearchView, AskStoryListView, ShowStoryListView, StoryDetailView, StoryListView, create_comment

app_name = 'news'


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('news/stories', StoryListView.as_view(), name='stories'),
    path('news/search/', SearchView.as_view(), name='search'),
    path('news/ask/', AskStoryListView.as_view(), name='ask'),
    path('news/show/', ShowStoryListView.as_view(), name='show'),
    path('news/story/<int:pk>/', StoryDetailView.as_view(), name='story'),
    path('news/create/comment/', create_comment, name='comment')
]
