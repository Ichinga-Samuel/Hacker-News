from rest_framework import serializers
from rest_framework import permissions

from news.models import Story, StoryComments
from jobs.models import Job


class StorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Story
        read_only_fields = ('id', 'reviews', 'score', 'time')
        fields = ('id', 'title', 'text', 'url', 'reviews', 'score', 'comments', 'by', 'time')
        depth = 1


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ('id', 'title', 'text', 'url', 'comments', 'by', 'time')
        read_only_fields = ('id', 'time')
        depth = 1


class ByCreator(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.by == request.user
