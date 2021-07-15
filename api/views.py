from django.contrib.auth import get_user_model
from rest_framework import generics, response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework import viewsets

from .serializer import JobSerializer, StorySerializer, Story, Job, ByCreator

User = get_user_model()


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class StoryCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StorySerializer

    def create(self, request, *args, **kwargs):
        obj = {}
        for field in ('title', 'url', 'text'):
            val = request.POST.get(field)
            if val:
                obj[field] = val
        try:
            id_ = request.user.id
            user = User.objects.get(id=id_)
            obj['by'] = user
            obj = Story(**obj)
            obj.save()
            return response.Response(201)
        except User.DoesNotExist:
            return response.Response(404)


class StoryEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = StorySerializer
    queryset = Story.objects.all()


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class JobCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def create(self, request, *args, **kwargs):
        obj = {}
        for field in ('title', 'url', 'text'):
            val = request.POST.get(field)
            if val:
                obj[field] = val
        try:
            id_ = request.user.id
            user = User.objects.get(id=id_)
            obj['by'] = user
            obj = Job(**obj)
            obj.save()
            return response.Response(201)
        except User.DoesNotExist:
            return response.Response(404)


class JobEditView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser, ByCreator]
    serializer_class = JobSerializer
    queryset = Job.objects.all()
