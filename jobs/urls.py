from django.urls import path

from .views import JobDetailView, JobListView

app_name = 'jobs'

urlpatterns = [
    path('<int:pk>/', JobDetailView.as_view(), name='job'),
    path('jobs/', JobListView.as_view(), name='jobs'),
]
