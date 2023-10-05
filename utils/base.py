import asyncio
from typing import Type, TypeVar
from logging import getLogger
from dataclasses import dataclass, field
from enum import StrEnum
from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.exceptions import ObjectDoesNotExist

from account.models import User as UserModel, Base as _Model
from story.models import Story as StoryModel, Comment as CommentModel
from poll.models import Poll as PollModel, PollOption as PollOptionModel

logger = getLogger()

Model = TypeVar('Model', bound=_Model)
tz = ZoneInfo('UTC')


def get_default_password():
    return 'TheDefaultP@ssw0rd'


class Types(StrEnum):
    JOB = 'job'
    STORY = 'story'
    COMMENT = 'comment'
    POLL = 'poll'
    POLLOPT = 'pollopt'


@dataclass
class BaseClass:
    id: int
    type: Types
    deleted: bool = False
    by: str = 'anon'
    time: float = field(default=datetime.now().timestamp())
    dead: bool = False
    kids: list[int] = field(default_factory=list)
    model: Model = None

    def set_date(self):
        return datetime.fromtimestamp(self.time, tz=tz)

    @property
    def defaults(self):
        return dict(type=self.type, created=self.set_date(), id=self.id,
                    deleted=self.deleted, dead=self.dead)
    
    async def user(self):
        try:
            user = await User(id=self.by).save()
            return user
        except Exception as exe:
            logger.error(exe)
    
    async def get(self, *, model: Type[Model], **query) -> Model | None:
        try:
            obj = await model.objects.aget(**query)
            return obj
        except ObjectDoesNotExist:
            return None


@dataclass
class Story(BaseClass):
    descendants: int = 0
    title: str = ''
    url: str = ''
    text: str = ''
    score: int = 0
    # noinspection DuplicatedCode

    async def save(self):
        try:
            user = await self.user()
            defaults = self.defaults | dict(url=self.url, title=self.title, text=self.text, user=user, score=self.score)
            story, _ = await StoryModel.objects.aupdate_or_create(id=self.id, defaults=defaults)
        except Exception as err:
            logger.error(err)
        

@dataclass
class Comment(BaseClass):
    parent: int = 0
    text: str = ''
    
    async def save(self):
        try:
            res: list[StoryModel, CommentModel] = await asyncio.gather(self.get(model=StoryModel, id=self.parent),
                                                                        self.get(model=CommentModel, id=self.parent))
            story, comment = res
            if story == comment is None:
                return

            user = await self.user()
            defaults = self.defaults | dict(text=self.text, user=user, id=self.id)
            if story:
                defaults['story'] = story
                obj, _ = await CommentModel.objects.aupdate_or_create(id=self.id, defaults=defaults)

            if comment:
                obj, _ = await CommentModel.objects.aupdate_or_create(id=self.id, defaults=defaults)
                await comment.replies.aadd(obj)
        except Exception as err:
            logger.error(err)
            
        
@dataclass
class Poll(BaseClass):
    parts: list[int] = field(default_factory=list)
    descendants: int = 0
    score: int = 0
    title: str = ''
    text: str = ''
    
    async def save(self):
        try:
            user = await self.user()
            defaults = self.defaults | dict(score=self.score, title=self.title, text=self.text, user=user)
            poll, _ = await PollModel.objects.aupdate_or_create(id=self.id, defaults=defaults)
        except Exception as err:
            logger.error(err)


@dataclass
class PollOption(BaseClass):
    parent: int = 0
    score: int = 0
    
    async def save(self):
        try:
            user = await self.user()
            poll = await self.get(model=PollModel, id=self.parent)
            if poll is None:
                return
            defaults = self.defaults | dict(score=self.score, user=user, poll=poll)
            pollopt, _ = await PollOptionModel.objects.aupdate_or_create(id=self.id, defaults=defaults)
        except Exception as err:
            logger.error(err)


@dataclass
class User:
    id: str
    created: float = field(default=datetime.now().timestamp())
    karma: int = 0
    about: str = ''
    delay: int = 0
    submitted: list[int] = field(default_factory=list)

    def set_date(self):
        return datetime.fromtimestamp(self.created, tz=tz)

    async def save(self):
        try:
            defaults = {'karma': self.karma, 'about': self.about, 'created': self.set_date()}
            if self.id == 'anon':
                defaults['email'] = 'anon@gmail.com'
            user, new = await UserModel.objects.aupdate_or_create(username=self.id, defaults=defaults)
            if new:
                user.set_password(get_default_password())
                await user.asave()
            return user
        except Exception as err:
            logger.error(err)
        