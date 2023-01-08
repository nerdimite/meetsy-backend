# Meetsy: AI Meeting Assistant

Meetsy is a meeting assistant that transcribes, summarizes, extracts actions items from meetings and also makes it all searchable so you don't have to go through the whole meeting again to find that one thing you were looking for.

This repository contains the code for the AI backend of the project. The frontend can be found [here](https://github.com/nerdimite/meetsy-app) and the demo can be found [here](https://meetsy.netlify.app).

## Setup

### Whisper API

The app uses the [CellStrat Whisper API](https://cellstrathub.com/marketplace/cellstrat/whisper-gpu) to transcribe the meetings. You can sign up for a free account [here](https://cellstrathub.com/request-access). Once you have an account, you can get your API key from the [deployment dashboard](https://console.cellstrathub.com/deployments).

### Insights API

The Insights API is responsible for the Meeting Summarization and Action Item Extraction. Both of these tasks use the GPT-3 API from OpenAI. This part is setup as a lambda function on AWS for additional post processing. You can find the code for the lambda function [here](insights_api) and the lambda layer setup for the openai package [here](lambda_layer).

#### Instructions

1. Follow the instructions in the [lambda_layer](lambda_layer)'s readme to setup the lambda layer.
2. Create a new lambda function on AWS with the following settings:
   - Runtime: Python 3.8
   - Handler: `lambda_function.lambda_handler`
   - Layers: The lambda layer you created in step 1.
   - Environment Variables
     - OPENAI_API_KEY: Your OpenAI API key
3. Copy the code in [insights_api](insights_api) folder to the lambda function.
4. Create a Lambda Function URL to invoke the lambda function from the frontend. Make sure to apply the appropriate CORS settings and authentication to None.
5. Don't forget to increase the timeout of the lambda function to 2 minutes or something similar.

### Search API

The search API works on the transcript of the meeting to find the relevant timestamps for the search query. It uses Sentence Transformers to find the most similar sentences to the search query. This model is deployed on CellStrat Hub as well who's code can be found at [transcript_search](transcript_search).

#### Instructions

1. Open your workspace on CellStrat Hub and upload the [transcript_search](transcript_search) folder.
2. Open up a terminal and run the following commands as a pre-requisite to install the required packages:
   ```bash
   cd transcript_search
   pip install sentence-transformers
   python download_model.py
   ```
3. Now build and deploy the model using the following commands:
   ```bash
   hub build
   hub deploy
   ```

Learn more about deploying models on CellStrat Hub [here](https://docs.cellstrathub.com/hubapi%20deployment%20%F0%9F%9A%80/quickstart/).
