# National Park Chatbot

This repository contains a Flask application designed to serve as a webhook for Dialogflow, enabling interaction with a National Park Chatbot. The chatbot provides information about national parks, including activities, alerts, weather, and more. By building upon the foundation of the previous Park Dashboard project(GitHub - https://github.com/rutujapadgilwar/Park-Dashboard and WebDemo - https://parks-dashboard.netlify.app/), this chatbot and voice assistant provide a more effective and user-friendly experience, allowing users to easily and quickly find all related information.

## Features

1. **Welcome Intent:** Greets users and provides an overview of the chatbot's capabilities.
2. **Get Park Activities:** Retrieves activities available at a specified national park.
3. **Get Alerts Information:** Fetches alerts for a specific national park.
4. **Get Park Weather Information:** Retrieves current weather conditions for a specified national park.
5. **Get Park Name with Alert Type:** Lists national parks with a specific type of alert.
6. **Get Park Names in State:** Provides a list of national parks located in a specific state.

## Setup

### Clone the repository:

```bash
git clone https://github.com/yourusername/national-park-chatbot.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set up environment variables:
```bash
# Replace 'your_NPS_API_key_here' and 'your_OpenWeather_API_key_here' with your actual API keys
NPS_API_KEY="your_NPS_API_key_here"
OPENWEATHER_API_KEY="your_OpenWeather_API_key_here"
```
### Run the Flask application:

```bash
 python pp.py
```
### Dialogflow
Create a new project in Dialogflow and add the .zip from the repository.

### Test the Dialogflow Messenger
For testing purposes, we can interact with ngrok to create a tunnel and expose our local server to the internet. By adding the ngrok URL to Dialogflow, we can seamlessly integrate the chatbot or voice assistant and interact with it in real-time. This setup enables us to thoroughly test and refine the functionality of the National Park Chatbot before deploying it for broader use

### Web demo
I have developed both a voice assistant as well as a chatbot. I created the chatbot so it can be added to the previous national park project, but for a demo, you can view my work using the links below:

Voice Assistance: https://bot.dialogflow.com/603c58a0-a891-443e-a66b-824337a6ca13

Chat bot: https://park-helper-2.onrender.com/webhook
