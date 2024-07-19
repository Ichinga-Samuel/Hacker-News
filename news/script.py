import asyncio
import traceback
import requests
from datetime import datetime as dt
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware

from news.models import StoryComments, Story
from jobs.models import Job
from polls.models import Poll, PollOptions, PollComments

User = get_user_model()
try:
    anon = User.objects.get(username='anon')  # anonymous user for items without a specified user
except User.DoesNotExist:
    u = User(username='anon', about='I am anonymous')
    u.set_password('123456anon')
    u.save()
    anon = User.objects.get(username='anon')


async def get_item(item_id, url=None):
    """
    Get item from hacker news api
    :param item_id:
    :param url: optional url of item
    :return: Item as a dict or None
    """
    if url is None:
        url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    try:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(None, requests.get, url)
        res = resp.json()
        if resp.status_code == 200 and res:
            exclude = ('delay', 'submitted')  # fields not needed in the models
            for field in exclude:
                if field in res:
                    del res[field]
            for field in ('dead', 'deleted',):
                if field in res:
                    return None
            return res
        else: return None
    except Exception as err:
        traceback.print_exc()
        return None


async def get_latest_stories(url, with_comments=True):
    """

    :param url: url of stories, ASK, Show, etc.
    :param with_comments: Load Comments at the same time
    :return:
    """
    loop = asyncio.get_running_loop()
    try:
        resp = await loop.run_in_executor(None, requests.get, url)
        resp = resp.json() if resp.status_code == 200 else []
    except Exception:
        print('Something went wrong')
        return
    print(f'Uploading {len(resp)} Stories')
    tasks = []
    # create tasks for adding new stories
    for item in resp:
        try:
            res = await check_item(item, Story)
            if res[0]: print('Story already exists. Skipping')
            if not res[0]:
                story = await get_item(item)
                if story and story.get('type') == 'story':
                    tasks.append(loop.create_task(set_story(story, with_comments=with_comments)))
        except Exception as err:
            traceback.print_exc()
            continue
    await asyncio.gather(*tasks, return_exceptions=True)
    print('Complete')


async def set_story(story, with_comments=True):
    loop = asyncio.get_running_loop()
    try:
        # remove unnecessary fields
        # add the story creator to the database
        del story['type']
        user = await set_user(story['by']) if 'by' in story else anon
        if 'descendants' in story:
            reviews = story.get('descendants')
            story['reviews'] = reviews
            del story['descendants']
        comments = []
        if 'parent' in story: del story['parent']
        if 'kids' in story:
            comments = story['kids']
            del story['kids']
        story['by'] = user
        if 'time' in story:
            story['time'] = await loop.run_in_executor(None, make_aware, dt.fromtimestamp(story['time']))
        obj = await loop.run_in_executor(None, lambda: Story(**story))
        del story['id']
        await loop.run_in_executor(None, obj.save)
        print(f"{story['title']} Added")
        if comments and obj and with_comments:
            await set_story_comments(comments, obj)
        return
    except Exception as err:
        raise err


async def set_story_comments(comments, story):
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(create_comment(comment, StoryComments, post=story)) for comment in comments]
    await asyncio.gather(*tasks, return_exceptions=True)


async def create_comment(comment, model, post=None):
    """
    :param comment: The item id comment to be created
    :param model: The Model for creating the comment can be a StoryComment, PollComment or another Comment
    :param post:   The main post that the comment belongs to if it is a direct comment to a post it can be either a Poll or a Story
    :return:
    """
    loop = asyncio.get_running_loop()
    comment = await get_item(comment)
    if comment and comment.get('type') == 'comment':
        del comment['type']
        user = await set_user(comment['by']) if 'by' in comment else anon
        comment['by'] = user
        replies = []
        if 'kids' in comment:
            replies = comment['kids']
            del comment['kids']

        if 'parent' in comment: del comment['parent']

        if 'time' in comment:
            comment['time'] = await loop.run_in_executor(None, make_aware, dt.fromtimestamp(comment['time']))

        # determine the type of post the comment belongs to
        if post:
            if isinstance(post, Story):
                key = 'story'
            elif isinstance(post, StoryComments):
                key = 'comment'
            else:
                key = 'poll'
            comment[key] = post

        obj = await loop.run_in_executor(None, lambda: model(**comment))
        await loop.run_in_executor(None, obj.save)
        print(f'{obj} comment added for f{post}')
        # recursively add replies to the comment using the same function
        if replies and obj:
            tasks = [loop.create_task(create_comment(reply, model, post=obj)) for reply in replies]
            await asyncio.gather(*tasks, return_exceptions=True)


async def set_poll(poll, with_comments=True):
    loop = asyncio.get_running_loop()
    user = await set_user(poll['by']) if 'by' in poll else anon
    poll['by'] = user
    if 'descendants' in poll:
        poll['reviews'] = poll['descendants']
        del poll['reviews']

    if 'score' in poll: del poll['score']

    if 'parent' in poll: del poll['parent']

    options = ()
    if 'parts' in poll:
        options = poll['parts']
        del poll['parts']

    comments = ()
    if 'comments' in poll:
        comments = poll['kids']
        del poll['kids']

    if 'time' in poll:
        poll['time'] = await loop.run_in_executor(None, make_aware, dt.fromtimestamp(poll['time']))

    obj = await loop.run_in_executor(None, lambda: Poll(**poll))
    await loop.run_in_executor(obj.save)
    print(f'Poll {obj.title} Added')
    if comments and obj and with_comments:
        await set_poll_comments(comments, obj)

    if options and obj:
        await set_poll_options(options, obj)
    return


async def set_poll_comments(comments, poll):
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(create_comment(comment, PollComments, post=poll)) for comment in comments]
    await asyncio.gather(*tasks, return_exceptions=True)


async def set_poll_options(options, poll):
    loop = asyncio.get_running_loop()
    for id_ in options:
        try:
            option = await get_item(id_)
            if option and option.get('type') == 'pollopt':
                del option['type']
                user = await set_user(option['by']) if 'by' in option else anon
                option['by'] = user
                if 'parent' in option: del option['parent']
                if 'score' in option:
                    option['votes'] = option['score']
                    del option['score']

                for f in ('kids', 'parent'):
                    if f in option: del option[f]

                if 'time' in option:
                    option['time'] = await loop.run_in_executor(None, make_aware, dt.fromtimestamp(option['time']))

                option['poll'] = poll
                obj = await loop.run_in_executor(None, lambda: PollOptions(**option))
                await loop.run_in_executor(None, obj.save)
        except Exception as err:
            continue


async def check_item(item_id, model):
    """
    check if an item is already in the database
    :param model: The model to check with
    :param item_id: The primary key of the item
    :return: True and the object if it is existing else return False
    """
    loop = asyncio.get_running_loop()
    try:
        item = await loop.run_in_executor(None, lambda: model.objects.get(id=item_id))
        return (True, item) if item else (False, None)
    except Exception as err:
        return False, None


async def set_user(name):
    loop = asyncio.get_running_loop()
    try:
        user = await loop.run_in_executor(None, lambda: User.objects.get(username=name))
        if user:
            return user
    except Exception as err:
        try:
            url = f"https://hacker-news.firebaseio.com/v0/user/{name}.json"
            user = await get_item(name, url=url)
            user['username'] = user['id']
            del user['id']
            if 'created' in user:
                user['created'] = await loop.run_in_executor(None, make_aware, dt.fromtimestamp(user['created']))

            if 'karma' in user:
                del user['karma']
            user = await loop.run_in_executor(None, lambda: User(**user))
            await loop.run_in_executor(None, lambda: user.set_password('12345FooBar'))
            await loop.run_in_executor(None, user.save)
            return user if user else anon
        except Exception as err:
            return anon


async def get_latest_jobs():
    url = "https://hacker-news.firebaseio.com/v0/jobstories.json"
    loop = asyncio.get_running_loop()
    try:
        res = await loop.run_in_executor(None, requests.get, url)
        resp = res.json() if res.status_code == 200 else []
    except Exception as err:
        print('An Error Occurred')
        return
    tasks = []
    print('Adding to task queue')
    for item in resp:
        try:
            res = await check_item(item, Job)
            if res[0]:
                print('Job already added')
                continue
            job = await get_item(item)
            if job and job.get('type') == 'job':
                del job['type']
                tasks.append(loop.create_task(set_job(job)))
        except Exception as err:
            traceback.print_exc()
            continue
    print(f'Adding {len(tasks)} Jobs Adverts')
    completed = 0
    for job in asyncio.as_completed(tasks):
        try:
            await job
            completed += 1
            print(f"{completed} Job Adverts Added")
        except Exception as err:
            traceback.print_exc()
            continue
    print(f"Added {completed} Job Adverts")


async def set_job(job):
    loop = asyncio.get_running_loop()
    try:
        user = await set_user(job['by']) if 'by' in job else anon
        job['by'] = user

        for f in ('parts', 'score', 'kids', 'parent'):  # won't be in jobs stories according to docs but just double checking
            if f in job: del job[f]

        if 'time' in job:
            job['time'] = await loop.run_in_executor(None, make_aware, dt.fromtimestamp(job['time']))
        obj = await loop.run_in_executor(None, lambda: Job(**job))
        await loop.run_in_executor(None, obj.save)
    except Exception as err:
        raise err


async def get_latest(with_comments=True, n=100):
    """
    Get The latest "n" items by going backward from the current maximum item in the api
    :param with_comments:
    :param n:
    :return:
    """
    loop = asyncio.get_running_loop()
    try:
        res = await loop.run_in_executor(None, requests.get, "https://hacker-news.firebaseio.com/v0/maxitem.json")
        max_id = res.json() if res.status_code == 200 else None
    except Exception as err:
        print('Something went wrong')
        return

    print(f'uploading {n} items')
    tasks = []
    for i in reversed(range(max_id - n, max_id + 1)):
        try:
            tasks.append(loop.create_task(set_item(i, with_comments=with_comments)))
        except Exception as err:
            traceback.print_exc()
            continue
    await asyncio.gather(*tasks, return_exceptions=True)
    print('Complete')


async def check_id(id_):
    """
    Check if Item is already existing in the database using all the models
    :param id_:
    :return: if the item is existing return (True, Model, Item) else (False, None, None)
    """
    models = (Story, Job, StoryComments, PollOptions, Poll, PollComments)
    for model in models:
        res = await check_item(id_, model)
        if res[0]:
            return True, model, res[1]
    else:
        return False, None, None


async def set_item(id_, with_comments=True):
    item = await check_id(id_)
    if item[0]:
        print('Item already exists. Skipping')
        return                          # exit if item is already existing
    try:
        item = await get_item(id_)
        type_ = item.get('type')
        if type_ == 'story':
            return await set_story(item, with_comments=with_comments)
        if type_ == 'job':
            del item['job']
            return await set_job(item)

        if type_ == 'poll':
            return await set_poll(item, with_comments=with_comments)

        if type_ == 'comment':
            return await set_comment(id_, item)
    except Exception as err:
        raise err


async def set_comment(id_, item):
    pid = item.get('parent')
    if pid is None:
        return                              # a comment must have a parent
    res = await check_id(pid)               # get the parent from the database
    if not res[0]:                          # if the item has no parent set the parent
        await set_item(pid, with_comments=True)
        return

    if isinstance(res[1], (Story, StoryComments)):
        return await create_comment(id_, StoryComments, post=res[2])

    if isinstance(res[1], (PollComments, Poll)):
        return await create_comment(id_, PollComments, post=res[2])
