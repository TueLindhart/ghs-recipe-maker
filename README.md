### Code for using LLMs to estimate CO2 emission from recipe lists

# Install
Install using the following command
```bash
poetry install
```

# Release to heroku
Heroku is linekd  to github repo and will deploys from main. To enable heroku to install the newest packages,
run the following command:

```bash
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

Monitor app output with

```bash
heroku logs --source app
```
