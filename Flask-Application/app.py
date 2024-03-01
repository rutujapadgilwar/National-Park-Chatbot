from flask import Flask, request, jsonify, render_template
import requests
from fuzzywuzzy import process

app = Flask(__name__)

NPS_API_KEY = ''
NPS_BASE_URL = 'https://developer.nps.gov/api/v1'
OPENWEATHER_API_KEY = ''
UNITS = 'metric'
PARKS_URL = f"{NPS_BASE_URL}/parks?limit=500&api_key={NPS_API_KEY}"
ALERTS_URL = f"{NPS_BASE_URL}/alerts?limit=700&api_key={NPS_API_KEY}"
WEATHER_URL = 'https://api.openweathermap.org/data/2.5'

# Fetch parks data
response = requests.get(PARKS_URL)
parks_data = response.json()['data']

valid_alert_types = ["Information", "Danger", "Park Closure", "Caution"]

# Dictionary to store national parks with their codes
national_parks_to_code = {}
# Iterate through parks data and filter national parks
for park in parks_data:
    if park['designation'] == "National Park":
        national_parks_to_code[park['fullName']] = park['parkCode']

parkCode_to_National_park = {}

for park in parks_data:
    if park['designation'] == "National Park":
        parkCode_to_National_park[park['parkCode']] = park['fullName']

# Function to extract alert type with fuzzy matching


def get_alert_type(query):
    best_match, score = process.extractOne(query, valid_alert_types)
    if score > 80:
        return best_match
    else:
        return None


def get_best_match_park(user_input):
    best_match, score = process.extractOne(
        user_input, national_parks_to_code.keys())
    if score > 80:
        return best_match, national_parks_to_code[best_match]
    else:
        return None, None


def fetch_park_alerts(park_name):
    _, park_code = get_best_match_park(park_name)
    if park_code:
        response = requests.get(
            f"{NPS_BASE_URL}/alerts?&limit=800&api_key={NPS_API_KEY}&parkCode={park_code}")
        data = response.json()
        alerts = [alert['description'] for alert in data['data']]
        return alerts
    else:
        return None


def fetch_park_activities(park_name):
    # Get park code using fuzzy matching
    _, park_code = get_best_match_park(park_name)
    if park_code:
        # Query the NPS API to get park activities
        response = requests.get(
            f"{NPS_BASE_URL}/activities?parkCode={park_code}&api_key={NPS_API_KEY}")
        data = response.json()
        activities = [activity['name'] for activity in data['data']]
        return activities
    else:
        return None


def fetch_parks_with_alert_type(alert_type):
    national_parks_with_alert = []
    alerts_data = requests.get(f"{ALERTS_URL}").json()['data']
    for alert in alerts_data:
        if alert['category'] == alert_type and alert['parkCode'] in parkCode_to_National_park:
            national_parks_with_alert.append(
                parkCode_to_National_park[alert['parkCode']])
    return national_parks_with_alert


def fetch_park_weather(park_name):
    _, park_code = get_best_match_park(park_name)
    if park_code:
        response = requests.get(
            f"{NPS_BASE_URL}/parks?&limit=800&api_key={NPS_API_KEY}&parkCode={park_code}")
        data = response.json()['data']
        latitude = data[0]['latitude']
        longitude = data[0]['longitude']
        park_image = data[0]['images'][0]['url']
        fetchWeatherInfo = requests.get(
            f"{WEATHER_URL}/forecast?lat={latitude}&lon={longitude}&units={UNITS}&appid={OPENWEATHER_API_KEY}")
        weatherData = fetchWeatherInfo.json()
        weatherInfo = weatherData['list'][0]['weather'][0]['description']
        temperature = weatherData['list'][0]['main']['temp']
        humidity = weatherData['list'][0]['main']['humidity']
        return weatherInfo, temperature, humidity, park_image
    else:
        return None


def fetch_park_names_in_state(stateName):
    state_abbreviations = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "DC": "DC",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "Other": "Other",
    }
    best_match, _ = process.extractOne(stateName, state_abbreviations.keys())
    state_abbreviation = state_abbreviations.get(best_match)
    if not state_abbreviation:
        return None

    response = requests.get(
        f"{NPS_BASE_URL}/parks?limit=800&api_key={NPS_API_KEY}")
    data = response.json()['data']

    parkList = []
    for park in data:
        if park['addresses'][0]['stateCode'] == state_abbreviation and park['parkCode'] in parkCode_to_National_park:
            parkList.append(park['fullName'])
    return parkList


def index():
    return render_template('dialogflow_messenger.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    intent_name = req['queryResult']['intent']['displayName']

    if intent_name == 'welcomeIntent':
        # fulfillment_text = [
        #     {
        #         "payload": {
        #             "richContent": [
        #                 [
        #                     {
        #                         "type": "description",
        #                         "title": "Hello! Welcome to our National Parks Assistant.",
        #                         "text": [
        #                                 "I can help you with providing alerts, weather information, and activities at national parks.",
        #                                 "Additionally, you can search for national park names by state and find parks with specific alert types.",
        #                             "How can I assist you today?"
        #                         ]
        #                     }
        #                 ]
        #             ]
        #         }
        #     }
        # ]
        fulfillment_text = [
            {"text": {
                "title": ["Hello! Welcome to our National Parks Assistant."]}},
            {"text": {"text": [
                "I can help you with providing alerts, weather information, and activities at national parks."]}},
            {"text": {"text": [
                "Additionally, you can search for national park names by state and find parks with specific alert types."]}},
            {"text": {"text": ["How can I assist you today?"]}}
        ]
    elif intent_name == "ByeIntent":
        fulfillment_text = [{"text": {"text": ["Goodbye! Have a nice day."]}}]
    elif intent_name == "getParkActivitiesInfo":
        park_name = req['queryResult']['parameters']['parkName']
        activities = fetch_park_activities(park_name)
        if activities:
            message = f"Here are some activities you can do at {park_name}:\n\n"
            message += '\n'.join(activities)
            fulfillment_text = [{"text": {"text": [message]}}]
        else:
            fulfillment_text = [{"text": {"text": [
                f"Sorry, I couldn't find information about activities at {park_name}."]}}]
    elif intent_name == "getAlertsInfo":
        park_name = req['queryResult']['parameters']['parkName']
        alerts = fetch_park_alerts(park_name)
        if alerts:
            alert_list = "\n\n".join([f"-- {alert}" for alert in alerts])
            fulfillment_text = [
                {"text": {"text": [f"Here are some alerts at {park_name}:\n\n{alert_list}"]}}]
        else:
            fulfillment_text = [
                {"text": {"text": [f"No alerts found at {park_name}."]}}]
    elif intent_name == "getParkWeatherInfo":
        park_name = req['queryResult']['parameters']['parkName']
        weather_info = fetch_park_weather(park_name)
        if weather_info:
            weather, temperature, humidity, park_image = weather_info
            fulfillment_text = [{"text": {"text": [
                f"Weather at {park_name} is {weather}, Temperature: {temperature}°C, Humidity: {humidity}%"]}}]
        else:
            fulfillment_text = [
                {"fulfillmentText": f"Sorry, I couldn't fetch the weather information for {park_name}."}]
    elif intent_name == "getParkNameWithAlertType":
        user_alert_type = req['queryResult']['parameters']['alertType']
        alert_type = get_alert_type(user_alert_type)
        if alert_type:
            parks_with_alert = fetch_parks_with_alert_type(alert_type)
            if parks_with_alert:
                parks_with_alert = "\n".join(
                    [f"- {park}" for park in parks_with_alert])
                fulfillment_text = [{"text": {"text": [
                    f"The following national parks have {alert_type} alerts: \n\n{parks_with_alert}"]}}]
            else:
                fulfillment_text = [
                    {"text": {"text": [f"No national parks found with {alert_type} alerts."]}}]
        else:
            fulfillment_text = [{"text": {"text": [
                f"Sorry, I couldn't understand the alert type {user_alert_type}. Please try again."]}}]
    elif intent_name == "getParkNamesInState":
        state = req['queryResult']['parameters']['geo-state-us']
        park_names = fetch_park_names_in_state(state)
        if park_names:
            park_names = "\n".join([f"- {park}" for park in park_names])
            fulfillment_text = [
                {"text": {"text": [f"The national parks in {state} are: \n\n{park_names}"]}}]
        else:
            fulfillment_text = [
                {"text": {"text": [f"No national parks found in {state}."]}}]
    else:
        fulfillment_text = [{"text": {"text": ["Intent not recognized."]}}]

    response = {'fulfillmentMessages': fulfillment_text}
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
