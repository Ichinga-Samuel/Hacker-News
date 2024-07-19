from django.urls import path
from .views import StoryViewSet, StoryCreateView, StoryEditView, JobViewSet, JobCreateView, JobEditView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('jobs', JobViewSet, basename='tips')

router.register('stories', StoryViewSet, basename='tags')

app_name = 'api'

urlpatterns = [
    path('create_story/', StoryCreateView.as_view(), name='create-story'),
    path('edit_story/<int:pk>/', StoryEditView.as_view(), name='edit-story'),
    path('create_job/', JobCreateView.as_view(), name='create-job'),
    path('edit_job/<int:pk>/', JobEditView.as_view(), name='edit-job')
]
urlpatterns += router.urls
