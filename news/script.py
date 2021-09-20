import traceback
import requests
from datetime import datetime as dt
from django.contrib.auth import get_user_model
from django.db.models import Max
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


class NewsApi:

    def get_item(self, item_id, url=None):
        if url is None:
            url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        try:
            resp = requests.get(url)
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
            print(err)
            traceback.print_exc()
            return None

    def get_latest_stories(self, url, with_comments=False):
        try:
            resp = requests.get(url)
            resp = resp.json() if resp.status_code == 200 else []
        except Exception:
            return

        total = len(resp)
        msg = f'Uploading {total} Stories'
        if with_comments:
            msg += ' With Comments'
        else: msg += ' Without Comments'
        print(msg)
        completed = 0
        for item in resp:
            try:
                if not self.check_item(item, Story)[0]:
                    story = self.get_item(item)
                    print(story)
                    if story and story.get('type') == 'story':
                        self.set_story(story, with_comments=with_comments)
            except Exception as err:
                print(err)
                traceback.print_exc()
                total -= 1
                completed += 1
                print(f"{completed} Stories uploaded {total} remaining")
                continue
            total -= 1
            completed += 1
            print(f"{completed} Stories uploaded {total} remaining")
        print('Complete')

    def set_story(self, story, with_comments=False):
        try:
            del story['type']
            user = self.set_user(story['by']) if 'by' in story else anon
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
                story['time'] = make_aware(dt.fromtimestamp(story['time']))
            obj = Story(**story)
            del story['id']
            obj.save()
            if comments and obj and with_comments: self.set_story_comments(comments, obj)
            return obj
        except Exception as err:
            traceback.print_exc()

    def set_story_comments(self, comments, story):
        for comment in comments:
            self.create_comment(comment, StoryComments, post=story)

    def get_latest_jobs(self, with_comments=False):
        url = "https://hacker-news.firebaseio.com/v0/jobstories.json"
        try:
            res = requests.get(url)
            resp = res.json() if res.status_code == 200 else []
        except Exception as err:
            resp = []
        print(f'Adding {len(resp)} Jobs')
        for item in resp:
            try:
                if not self.check_item(item, Job)[0]:
                    job = self.get_item(item)
                    if job and job.get('type') == 'job':
                        self.set_job(job, with_comments=with_comments)
            except Exception as err:
                traceback.print_exc()
        print("Complete")

    def set_job(self, job, with_comments=False):
        try:
            user = self.set_user(job['by']) if 'by' in job else anon
            job['by'] = user
            for f in ('parts', 'score', 'type'):
                if f in job: del job[f]
            comments = ()
            if 'parent' in job: del job['parent']
            if 'kids' in job:
                comments = job['kids']
                del job['kids']

            if 'time' in job:
                job['time'] = make_aware(dt.fromtimestamp(job['time']))
            obj = Job(**job)
            obj.save()
            if comments and with_comments and obj:
                self.set_job_comments(comments, obj)
            return obj
        except Exception as err:
            traceback.print_exc()

    def set_job_comments(self, comments, job):
        for comment in comments:
            self.create_comment(comment, JobComments, post=job)

    def set_poll(self, poll, with_comments=True):
        user = self.set_user(poll['by']) if 'by' in poll else anon
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
            poll['time'] = make_aware(dt.fromtimestamp(poll['time']))

        obj = Poll(**poll)
        obj.save(force_insert=True)
        if comments and obj and with_comments:
            self.set_poll_comments(comments, obj)

        if options and obj:
            self.set_poll_options(options, obj)

        return obj

    def set_poll_comments(self, comments, poll):
        for comment in comments:
            self.create_comment(comment, PollComments, post=poll)

    def set_poll_options(self, options, poll):
        for id_ in options:
            option = self.get_item(id_)
            if option and option.get('type') == 'pollopt':
                del option['type']
                user = self.set_user(option['by']) if 'by' in option else anon
                option['by'] = user

                if 'parent' in option: del option['parent']
                if 'score' in option:
                    option['votes'] = option['score']

                for f in ('kids', 'parent'):
                    if f in option: del option[f]

                if 'time' in option:
                    option['time'] = make_aware(dt.fromtimestamp(option['time']))

                option['poll'] = poll
                obj = PollOptions(**option)
                obj.save()

    def create_comment(self, comment, model, post=None, parent=None):
        """
        :param comment: The comment to be created
        :param model: The Model for creating the comment can be the JobComments Model or StoryComments
        :param post:   The main post that the comment belongs to if it is a direct comment to a post it can be either a Job or a Story
        :param parent:  The comment that a reply is been made to for replies
        :return:
        """
        comment = self.get_item(comment)
        if comment and comment.get('type') == 'comment':
            del comment['type']

            user = self.set_user(comment['by']) if 'by' in comment else anon
            comment['by'] = user

            replies = []
            if 'kids' in comment:
                replies = comment['kids']
                del comment['kids']

            if 'parent' in comment: del comment['parent']

            if 'time' in comment:
                comment['time'] = make_aware(dt.fromtimestamp(comment['time']))

            if post:
                if isinstance(post, Story):
                    key = 'story'
                elif isinstance(post, Job):
                    key = 'job'
                else:
                    key = 'poll'
                comment[key] = post

            obj = model(**comment)

            if parent:
                obj.comment = parent
            obj.save()

            if replies and obj:
                for reply in replies:
                    self.create_comment(reply, model, parent=obj)

    def check_item(self, item_id, model):
        """
        check if an item is already in the database
        :param model: The model to check with
        :param item_id: The primary key of the item
        :return: True,if it exists or False
        """
        try:
            item = model.objects.get(id=item_id)
            print(item)
            return (True, item) if item else (False, None)
        except Exception as err:
            return False, None

    def set_user(self, name):
        try:
            user = User.objects.get(username=name)
            if user:
                return user
        except Exception as err:
            try:
                url = f"https://hacker-news.firebaseio.com/v0/user/{name}.json"
                user = self.get_item(name, url=url)
                if user:
                    user['username'] = user['id']
                    del user['id']
                    if 'created' in user:
                        user['created'] = make_aware(dt.fromtimestamp(user['created']))

                    if 'karma' in user:
                        del user['karma']
                    user = User(**user)
                    user.set_password('12345FooBar')
                    user.save()
                    return user if user else anon
                else: return anon
            except Exception as err:
                print(err)
                # traceback.print_exc()
                return anon

    def get_latest(self, with_comments=False):
        s = Story.objects.aggregate(Max('id'))['id__max']
        j = Job.objects.aggregate(Max('id'))['id__max']
        p = Poll.objects.aggregate(Max('id'))['id__max']
        sc = StoryComments.objects.aggregate(Max('id'))['id__max']
        pc = PollComments.objects.aggregate(Max('id'))['id__max']
        maxs = (s, j, p, sc, pc, 1)
        c_max = max(i for i in maxs if i is not None)
        try:

            res = requests.get("https://hacker-news.firebaseio.com/v0/maxitem.json")
            max_id = res.json() if res.status_code == 200 else None
        except Exception as err:
            max_id = None

        if max_id:
            print(f'uploading {max_id-c_max} items')
            for i in reversed(range(c_max + 1, max_id + 1)):
                try:
                    self.set_item(i, with_comments=with_comments)
                except Exception as err:
                    traceback.print_exc()
                    continue
        print('Complete')

    def get_nth_latest(self, n=100, with_comments=True):
        s = Story.objects.aggregate(Max('id'))['id__max']
        j = Job.objects.aggregate(Max('id'))['id__max']
        p = Poll.objects.aggregate(Max('id'))['id__max']
        sc = StoryComments.objects.aggregate(Max('id'))['id__max']
        pc = PollComments.objects.aggregate(Max('id'))['id__max']
        maxs = (s, j, p, sc, pc, 1)
        c_max = max(i for i in maxs if i is not None)
        try:
            res = requests.get("https://hacker-news.firebaseio.com/v0/maxitem.json")
            max_id = res.json() if res.status_code == 200 else None
        except Exception as err:
            max_id = None

        if max_id:
            print(f'uploading {n} items')
            total = 0
            for i in reversed(range(c_max + 1, max_id + 1)):
                if total == n:
                    break
                try:
                    self.set_item(i, with_comments=with_comments)
                    total += 1
                except Exception as err:
                    traceback.print_exc()
                    continue


        print('Complete')

    def check_id(self, id_):
        """
        Check if Item is already existing in the database
        :param id_:
        :return:
        """
        models = (Story, Job, StoryComments, PollOptions, Poll, PollComments)
        for model in models:
            res = self.check_item(id_, model)
            if res[0]:
                return True, model, res[1]
        else:
            return False, None, None

    def set_item(self, id_, with_comments=False):
        if self.check_id(id_)[0]:
            return                          # exit if item is already existing
        item = self.get_item(id_)
        if item and ((type_ := item.get('type')) is not None):
            if type_ == 'story':
                return self.set_story(item, with_comments=with_comments)
            if type_ == 'job':
                return self.set_job(item, with_comments=with_comments)
            if type_ == 'poll':
                return self.set_poll(item, with_comments=with_comments)
            if type_ == 'comment':
                return self.set_comment(id_, item)
        return

    def get_parent(self, id_):
        """
        get the parent of a comment or reply
        :param id_:
        :return:
        """
        res = self.check_id(id_)
        if res[0]:
            return res[2]
        else:
            return None

    def set_comment(self, id_, item):
        print('check')
        pid = item.get('parent')
        if pid is None:
            return
        parent = self.get_parent(pid)               # get the parent from the database
        if parent is None:                          # if the item has no parent set the parent
            self.set_item(pid, with_comments=True)
            return

        if isinstance(parent, Story):
            self.create_comment(id_, StoryComments, post=parent)

        if isinstance(parent, StoryComments):
            self.create_comment(id_, StoryComments, parent=parent)

        if isinstance(parent, PollComments):
            self.create_comment(id_, PollComments, parent=parent)

        if isinstance(parent, Poll):
            self.create_comment(id_, PollComments, post=parent)

        print('check complete')

