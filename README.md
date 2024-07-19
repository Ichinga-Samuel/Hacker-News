# Hackers Digest

## Obtain News Stories from [Hacker News API](https://hacker-news.firebaseio.com/v0/)

## [Hackers Digest](https://groovy-works-328500.ew.r.appspot.com/)

# http://restunited.com/docs/2xp560aomidj 

### Features
- Fast Asynchronous and concurrent implementation of requests from the API and writing to database using _asyncio_ library

- Use Advanced Python Scheduler Library **Apscheduler** to periodically look for the latest stories by walking backward from the current largest item

- Google Authentication using Social Django

### Management Commands
  #### Use Thread Pool Executor for fast execution. The boolean flag *comment* indicates if you want to add the comments when adding a story
- ```python manage.py top_stories --comments```
  
  Load Up to 500 top and new stories from https://hacker-news.firebaseio.com/v0/topstories.json

	
- `python manage.py ask_stories --comments`
  
	Load Up to 200 of the latest Ask HN Stories! from https://hacker-news.firebaseio.com/v0/askstories.json

	
- `python manage.py show_stories --comments`
  
  Load Up to 200 of the latest Show HN Stories! from https://hacker-news.firebaseio.com/v0/showstories.json

- `python manage.py top_job`

	Load Up to 200 of the latest Job Stories! from https://hacker-news.firebaseio.com/v0/jobstories.json

	
- `python manage.py load_latest --comments`
  
	Walk backward from the current largest item to discover the latest items of different types using https://hacker-news.firebaseio.com/v0/maxitem.json
	
### Routes
- _**/**_
  
	See latest Stories and Jobs on the homepage


- _**/news/stories**_
  
	See all stories that are not Ask HN or Show HN

	
- **_/news/ask_**

	See all Ask HN stories


- **_/news/show_**
  
	See all Show HN stories
	

- **_/news/story/id_**
  
	See the details of a particular story including comments


- **_/news/create/comment_**
  
	Comment on a story. You have to log in.


- **/news/search** 
  
	Search the database for a story or job, can use filter to search for Jobs, Ask HN, Show HN.


- _**/jobs/id**_
  
	See a specific Job


- _**/jobs/jobs/**_
  
	See all jobs

### API Endpoints
- _**/api/stories/**_
  
	See all stories
	

- ***/api/jobs***

	See all jobs
	

- _**/api/create_story**_
  
	Create a story. Must log in first
	

- _**/api/edit_story/id**_
  
	Edit and Delete a story. You can only edit and delete your own story


- **_/api/create_job/_**
  
	Create a job. Must log in first


- _**/api/edit_job/**_
  
	Edit and Delete a job. You can only edit and delete your own job
  




