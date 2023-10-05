from django.forms import ModelForm, Textarea, CharField, IntegerField, HiddenInput, URLField

from .models import Comment, Story


class CommentForm(ModelForm):
    parent = CharField(max_length=255, widget=HiddenInput())
    parent_id = IntegerField(widget=HiddenInput())
    story_url = CharField(max_length=255, widget=HiddenInput())

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={'class': 'form-control', 'rows': 10, 'cols': 30}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        parent = self.cleaned_data['parent']
        parent_id = self.cleaned_data['parent_id']
        if parent == 'story':
            story = Story.objects.get(id=parent_id)
            instance.story = story
        if commit:
            instance.save()
            if parent == 'comment':
                Comment.objects.get(id=parent_id).replies.add(instance)
        return instance
