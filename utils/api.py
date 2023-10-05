"""
API class for Hacker News API. It uses async http requests to get data from Hacker News API.
"""
import http.client
import asyncio
import json
from logging import getLogger

from .base import User, Story, Comment, Poll, PollOption, BaseClass
from .task_queue import QueueItem, TaskQueue

logger = getLogger()


class API:
    api = 'hacker-news.firebaseio.com'
    version = 'v0'
    url = f'{api}/{version}'
    payload = {}
    connections = []
    ids = set()
    models: dict[str: BaseClass | User] = {'story': Story, 'comment': Comment, 'poll': Poll, 'pollopt': PollOption,
                                           'job': Story, 'user': User}

    def __init__(self, timeout=300, size=2000):
        self.task_queue = TaskQueue(size=size, timeout=timeout)

    async def get(self, *, path: str, payload: dict = None):
        try:
            conn = http.client.HTTPSConnection('hacker-news.firebaseio.com')
            self.connections.append(conn)
            payload = payload or self.payload
            path = f'/{self.version}/{path}'
            await asyncio.to_thread(conn.request, 'GET', path, payload)
            res = await asyncio.to_thread(conn.getresponse)
            return json.loads(res.read().decode('utf-8'))
        except Exception as e:
            logger.error(e)
            return

    async def close(self):
        [await asyncio.to_thread(conn.close) for conn in self.connections]

    def save(self, *, data: dict, key: str = ''):
        key = data.get('type', key)
        model = self.models[key]
        data = model(**data)
        self.task_queue.add(QueueItem(data.save))
        self.ids.add(data.id)

    async def get_by_id(self, *, item_id):
        if item_id in self.ids:
            return
        path = f'item/{item_id}.json'
        res = await self.get(path=path)
        if res is None:
            return
        self.save(data=res)
        if 'kids' in res:
            [self.task_queue.add(QueueItem(self.get_by_id, item_id=item)) for item in res['kids']]

        if 'by' in res:
            self.task_queue.add(QueueItem(self.get_user, user_id=res['by']))
        return res

    async def get_user(self, *, user_id):
        if user_id in self.ids:
            return

        path = f'user/{user_id}.json'
        res = await self.get(path=path)
        self.save(data=res, key='user')

    async def max_item(self) -> int:
        path = 'maxitem.json'
        return await self.get(path=path)

    async def top_stories(self) -> list[int]:
        """
        Up to 500 top and new stories
        :return:
        """
        path = 'topstories.json'
        return await self.get(path=path)

    async def ask_stories(self) -> list[int]:
        path = 'askstories.json'
        return await self.get(path=path)

    async def job_stories(self) -> list[int]:
        path = 'jobstories.json'
        return await self.get(path=path)

    async def show_stories(self) -> list[int]:
        path = 'showstories.json'
        return await self.get(path=path)

    async def updates(self) -> dict:
        path = 'updates.json'
        return await self.get(path=path)

    async def initiate(self):
        """
        Populate the database with latest stories from Hackernews
        """
        stories = await self.top_stories()
        asks = await self.ask_stories()
        show = await self.show_stories()
        stories = set(stories) | set(show) | set(asks)
        [self.task_queue.add(QueueItem(self.get_by_id, item_id=item)) for item in stories]
        await self.task_queue.run()

    async def walk_back(self, end=0):
        """Walk back from the maximum item to get the all historical data"""
        max_item = await self.max_item()
        [self.task_queue.add(QueueItem(self.get_by_id, item_id=item)) for item in range(max_item, end, -1)]
        await self.task_queue.run()

    async def update_objects(self):
        """Update items and profile"""
        updates = await self.updates()
        [self.task_queue.add(QueueItem(self.get_by_id, item_id=item)) for item in updates['items']]
        [self.task_queue.add(QueueItem(self.get_user, user_id=uid)) for uid in updates['profiles']]
        await self.task_queue.run()
        