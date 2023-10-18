# Hacker-News

## Django Backend Project

### Features
- Pull data from (https://hackernews.api-docs.io/v0/overview/introduction)[HackerNews] web api.
- Postgres Database.
- Docker-Compose to couple webapp and database services.
- Custom management commands to populate database.
- **populate:** populate database with latest and top stories
- **walkback:** Walk back from the the maximum item to any number specified. 
- Use customized asynchronous task queues for pulling large amount of data form the api concurrently.
- Email and username login.
