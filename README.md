# Food CO2 Estimator

This repository contains code for estimating CO2 emissions from the ingredient lists of recipes using Large Language Models (LLMs). The project leverages various tools and libraries to fetch, parse, and analyze recipe data to provide CO2 emission estimates.

## Table of Contents

- [Food CO2 Estimator](#food-co2-estimator)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Running the Flask App](#running-the-flask-app)
  - [Heroku](#heroku)
  - [Using the CO2 Estimator](#using-the-co2-estimator)
  - [Project Structure](#project-structure)
  - [Environment Variables](#environment-variables)
  

## Installation

To install the necessary packages, use the following command:

```bash
poetry install
```

This will install all the dependencies listed in the `pyproject.toml` file.

## Running the Flask App

To run the Flask app, follow these steps:

1. Ensure you have all dependencies installed using `poetry install`.
2. Run the Flask app using the following command:

```bash
poetry run flask run
```

The app will be available at `http://127.0.0.1:8000`.

## Heroku
The app is automatically deployed in heroku every time code is merged into main. To make sure the deployment does not fail, the pyproject.toml and poetry.lock file must be updated with all required packages.

## Using the CO2 Estimator

The CO2 estimator can be used to calculate the CO2 emissions of recipes. Here's how you can use it:

1. **Calculate CO2 Emission**:
   - Navigate to the home page of the Flask app.
   - Enter the recipe URL or the ingredients manually in the provided textarea.
   - Click on the "Calculate CO2e Emission" button.
   - The result will be displayed after processing.

2. **Monitor App Output**:
   - You can monitor the app output using Heroku logs (if deployed on Heroku):

```bash
heroku logs --source app
```

## Project Structure

The project is organized as follows:

```
.
├── .github/
│   └── workflows/
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── food_co2_estimator/
│   ├── chains/
│   ├── data/
│   ├── language/
│   ├── output_parsers/
│   ├── prompt_templates/
│   ├── pydantic_models/
│   ├── retrievers/
│   ├── url/
│   ├── __init__.py
│   ├── main.py
├── sandbox/
├── templates/
│   └── index.html
├── tests/
├── .coverage
├── .DS_Store
├── .flake8
├── .gitignore
├── .python-version
├── LICENSE
├── Makefile
├── poetry.lock
├── pyproject.toml
├── README.md
└── app.py
```

## Environment Variables
The following environment variables must be set in the .env file:

- `OPENAI_API_KEY`: Your OpenAI API key for accessing language models.
- `SERPER_API_KEY`: Your Serper API key for using Serper to search google and structure results
- `MY_MAIL`: Your mail for MyMemory translation provider. Increases the number of translations cap.
- `GPT_MODEL`: Model to be used when calling OpenAI.

Set the following environment variables in your `.env` file:

bash```
OPENAI_API_KEY=<your_key>
SERPER_API_KEY=<your_key>
MY_MAIL=<your_email>
GPT_MODEL=<gpt_model>
```



