from django.test import TestCase
from ..models import Comment, Story
from account.models import User


class CommentTestCase(TestCase):

    def setUp(self) -> None:
        user = User.objects.create_user(username='anon', email='anon@gmail.com')
        story = Story.objects.create(title='A Test Story', text='The Test Story', type='story', user=user)
        comment = Comment.objects.create(story=story, text='The Comment', user=user, type='comment')
        reply = Comment.objects.create(text='The Reply', user=user, type='comment')
        comment.replies.add(reply)

    def test_objects_created(self):
        user = User.objects.get(username='anon')
        story = Story.objects.get(title='A Test Story')
        comment = Comment.objects.filter(text__exact='The Comment').first()
        reply = comment.replies.first()
        self.assertEquals(reply.text, 'The Reply')
        self.assertEquals(user.username, 'anon')
        self.assertEquals(comment.text, 'The Comment')
        self.assertEquals(story.title, 'A Test Story')
