from django.shortcuts import render
from django.views.generic import DetailView, ListView

from jobs.models import Job


class JobDetailView(DetailView):
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    model = Job


class JobListView(ListView):
    template_name = 'jobs/jobs.html'
    model = Job
    context_object_name = 'jobs'
    paginate_by = 20
