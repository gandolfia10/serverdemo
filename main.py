# [START app]
import logging

from flask import Flask
from flask import request
from flask import make_response

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

app = Flask(__name__)
def do_json(state_, city_, command, timend, start):
	from urllib.request import urlopen
	import json
	f = 'http://api.wunderground.com/api/e8f0daedd86a461e/forecast10day/conditions/q/'
	f = f + state_ + '/' + city_ + '.json'
	fe = urlopen(f)
	json_string = fe.read()
	parsed_json = json.loads(json_string)
	location = parsed_json['current_observation']
	location = location['display_location']
	city = location['city']
	state = location['state']
	tempf = parsed_json['current_observation']['temp_f']
	tempc = parsed_json['current_observation']['temp_c']
	forecast_ = parsed_json['forecast']
	forecast_ = forecast_['simpleforecast']['forecastday']
	data = {}
	data['key'] = 'weather'
	data['city'] = city
	data['state'] = state
	data['command'] = command
	data['timend'] = timend - start
	data['tempf'] = tempf
	data['tempc'] = tempc
	data['results'] = []
	data['humidity'] = parsed_json['current_observation']['relative_humidity']
	for x in range(0,7):
		data['results'].append({'temp_highf': '', 'temp_lowf': '', 'temp_highc': '', 'day': '', 'month': '', 'year': '', 'temp_lowc': '', 'url': '', 'humidity': '', 'condition': '', 'precip': ''})
		data['results'][x]['temp_highf'] = forecast_[x]['high']['fahrenheit']
		data['results'][x]['temp_highc'] = forecast_[x]['high']['celsius']
		data['results'][x]['temp_lowf'] = forecast_[x]['low']['fahrenheit']
		data['results'][x]['temp_lowc'] = forecast_[x]['low']['celsius']
		data['results'][x]['precip'] = forecast_[x]['pop']
		data['results'][x]['url'] = forecast_[x]['icon_url']
		data['results'][x]['day'] = forecast_[x]['date']['day']
		data['results'][x]['month'] = forecast_[x]['date']['month']
		data['results'][x]['year'] = forecast_[x]['date']['year']
		data['results'][x]['condition'] = forecast_[x]['conditions']
		data['results'][x]['humidity'] = forecast_[x]['avehumidity']
	json_data = json.dumps(data)
	return json_data
	
	
def youtube_search(query, max_result):
	from googleapiclient.discovery import build
	from googleapiclient.errors import HttpError
	import json
	DEVELOPER_KEY = 'AIzaSyB-ux3WI-PQGLTy475xQ7Te1ySOCdY5fxY'
	YOUTUBE_API_SERVICE_NAME = 'youtube'
	YOUTUBE_API_VERSION = 'v3'
	youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
	search_response = youtube.search().list(q=query, part='id,snippet', maxResults=max_result).execute()
	json_youtube={}
	for search_result in search_response.get('items', []):
		if search_result['id']['kind'] == 'youtube#video':
			json_youtube['title']=search_result['snippet']['title']
			json_youtube['id']=search_result['id']['videoId']
			json_youtube['key'] = 'youtube'
			json_ = json.dumps(json_youtube)
			return json_

@app.route('/hello')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World! CORS WORK?'
    
@app.route('/recognize_v1/<Format>/<State>/<City>/<Device>')
def recognize_v1(State, City, Format, Device):
	import os
	import io
	import pyrebase
	from firebase_admin import credentials
	import firebase_admin
	from google.auth import compute_engine
	import re
	import time
	start = time.time()
	if 'text' in Format:
		commands = Format.split('_')
		if commands[1] == 'weather':
			end = time.time()
			return do_json(State, City, 'none', end, start)
		elif commands[1] == 'search':
			import urllib
			import json
			query = commands[2]
			f = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyDXPStB0SkGvzwAsef7OkfjyWMjoMAyIx0&cx=001196199226615081657:fto8g4831ii&q='
			f = f + query
			fe = urllib.urlopen(f)
			json_string = fe.read()
			parsed_json = json.loads(json_string)
			data = parsed_json['items']
			result1 = {}
			json_data = {}
			result1['key'] = 'google search'
			result1['title'] = data[0]['title']
			result1['snippet'] = data[0]['snippet']
			result1['url'] = data[0]['link']
			json_data['results'] = result1
			to_return = json.dumps(json_data)
			return to_return
			
			
	config = {
		"apiKey": "AIzaSyA8E94qwPa4Um0UMoG83rOJ_izZVQt-lGE",
		"authDomain": "personalassistant-ec554.firebaseapp.com",
		"databaseURL": "https://personalassistant-ec554.firebaseio.com",
		"storageBucket": "personalassistant-ec554.appspot.com",
		"serviceAccount": "firebaseadmin_api.json"
		}
	pyre = pyrebase.initialize_app(config)
	cred = credentials.Certificate("firebaseadmin_api.json")
	db = pyre.database()
	credentials = compute_engine.Credentials(service_account_email='my-account@personalassistant-ec554.iam.gserviceaccount.com')
	users = db.child("users").get()
	db.child("users")
	storage = pyre.storage()
# Instantiates a client
	from google.cloud import speech
	from google.cloud.speech import enums
	from google.cloud.speech import types
	client = speech.SpeechClient()
	if Device == 'ios':
		file_name = os.path.join(os.path.dirname(__file__),'resources','ios_voice.amr')
		wav = storage.child("ios_voice.amr").download(file_name)
		wav = file_name
#		storage.delete('ios_voice.amr')
		config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,sample_rate_hertz=8000,language_code='en-US')
	else:
		file_name = os.path.join(os.path.dirname(__file__),'resources','new_audio.amr')
		wav = storage.child("new_audio.amr").download(file_name)
		wav = file_name
#		storage.delete('new_audio.amr')
		config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.AMR,sample_rate_hertz=8000,language_code='en-US')
# The name of the audio file to transcribe
# Loads the audio into memory
	with io.open(file_name, 'rb') as audio_file:
		content = audio_file.read()
		audio = types.RecognitionAudio(content=content)
#		os.remove(file_name)
    
    # Detects speech in the audio file
	response = client.recognize(config, audio)
	for result in response.results:
		word = result.alternatives[0].transcript
		if 'weather' in word:
			from geotext import GeoText
			import pandas
			state_and_capital = os.path.join(os.path.dirname(__file__), 'resources','state_and_capital.csv')
			cities_data = os.path.join(os.path.dirname(__file__), 'resources','uscitiesv1.4AB.csv')
			data = pandas.read_csv(cities_data)
			us_states = data['state_name'].unique()
			us_states.sort()
			stuff = GeoText(word)
			us_stateid = data['state_id'].unique()
			us_stateid.sort()
			state_id = 'nothing'
			state_raw= 'stuff'
			capitals = pandas.read_csv(state_and_capital)
			if stuff.cities:
				if stuff.cities[0] in us_states:
					state_data = data[data['state_name']==stuff.cities[0]]
					state_raw = stuff.cities[0]
					state_id = state_data['state_id'].head(1).values[0]
					command = word.replace(stuff.cities[0], '')
					stuff = GeoText(command)
					if stuff.cities:
						city_ = stuff.cities[0]
						if any(data['city_ascii'] == city_):
							location2 = State
							thing = ((data['city_ascii'] == city_) & (data['state_id'] == state_id))
							if any(thing):
								end = time.time()
								return do_json(state_id, city, word, end, start)
                                # get json and return values
							elif any((data['city_ascii'] == city_) & (data['state_id'] == State)):
								end = time.time()
								return do_json(State, city_, word)
							else:
								if any(capitals['name'] == state_raw):
									city_ = capitals[capitals['name'] == state_raw]
									city1 = city_['description'].values[0]
									end = time.time()
									return do_json(_state['state_id'].values[0], city1, word, end, start)
					else:
						if any(capitals['name'] == state_raw):
							city_ = capitals[capitals['name'] == state_raw]
							city1 = city_['description'].values[0]
							end = time.time()
							return do_json(state_id, city1, word, end, start)
				else:
					city_ = stuff.cities[0]
					command = word.replace(stuff.cities[0], '')
					stuff = GeoText(command)
            
					if stuff.cities:
						if stuff.cities[0] in us_states:
							state_data = data[data['state_name'] == stuff.cities[0]]
							state_raw = stuff.cities[0]
							state_id = state_data['state_id'].head(1).values[0]
							if any(data['city_ascii'] == city_):
								location2 = State
								thing = ((data['city_ascii'] == city_) & (data['state_id'] == state_id))
								if any(thing):
									end = time.time()
									return do_json(state_id, city_, word, end, start)
                                # get json and return values
								elif any((data['city_ascii'] == city_) & (data['state_id'] == state)):
									end = time.time()
									return do_json(state_id, city_, word, end, start)
								else:
									if any(capitals['name'] == state_raw):
										city_ = capitals[capitals['name'] == state_raw]
										city1 = city_['description'].values[0]
										end = time.time()
										return do_json(state_id, city1, word)
					else:
						if any((data['city_ascii'] == city_) & (data['state_id'] == State)):
							end = time.time()
							return do_json(State, city_, word, end, start)
						else:
							data_ = data[data['city_ascii'] == city_].values[0]
							state_ = data_[2]
							end = time.time()
							return do_json(state_, city_, word, end, start)
			else:
				end = time.time()
				return do_json(State, City, word, end, start)
				
            
		elif 'search for' in word:
			if 'search for ' in command:
				reg_ex = re.search('search for (.*)', command)
				if reg_ex:
					domain = reg_ex.group(1)
					import urllib
					import json
					f = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyDXPStB0SkGvzwAsef7OkfjyWMjoMAyIx0&cx=001196199226615081657:fto8g4831ii&q='
					f = f + domain
					fe = urllib.urlopen(f)
					json_string = fe.read()
					parsed_json = json.loads(json_string)
					data = parsed_json['items']
					json_data = {}
					json_data['key'] = 'google search'
					json_data['title'] = data[0]['title']
					json_data['snippet'] = data[0]['snippet']
					json_data['url'] = data[0]['link']
					to_return = json_data.dumps(data)
					return to_return
					
					
			
		else:
			return 'voice'
	return 'Does not work'
@app.route('/recognize/<Command>/<State>/<City>/', defaults={'UserId':"none"})
@app.route('/recognize/<Command>/<State>/<City>/<UserId>')
def recognize(Command, State, City, UserId):
	import time
	import re
	import pyrebase
	start = time.time()
	command_ = Command.lower()
	voice = command_.split('_')
	if 'weather' in voice:
		from geotext import GeoText
		import pandas
		import os
		word = Command.replace('_', ', ')
		state_and_capital = os.path.join(os.path.dirname(__file__), 'resources','state_and_capital.csv')
		cities_data = os.path.join(os.path.dirname(__file__), 'resources','uscitiesv1.4AB.csv')
		data = pandas.read_csv(cities_data)
		us_states = data['state_name'].unique()
		us_states.sort()
		stuff = GeoText(word)
		us_stateid = data['state_id'].unique()
		us_stateid.sort()
		state_id = 'nothing'
		state_raw= 'stuff'
		capitals = pandas.read_csv(state_and_capital)
		if stuff.cities:
			if stuff.cities[0] in us_states:
				state_data = data[data['state_name']==stuff.cities[0]]
				state_raw = stuff.cities[0]
				state_id = state_data['state_id'].head(1).values[0]
				command = word.replace(stuff.cities[0], '')
				stuff = GeoText(command)
				if stuff.cities:
					city_ = stuff.cities[0].lower()
					if any(data['city_ascii'] == city_):
						location2 = State
						thing = ((data['city_ascii'] == city_) & (data['state_id'] == state_id))
						if any(thing):
							end = time.time()
							return do_json(state_id, city, word, end, start)
    		                 # get json and return values
						elif any((data['city_ascii'] == city_) & (data['state_id'] == State)):
							end = time.time()
							return do_json(State, city_, word)
						else:
							if any(capitals['name'] == state_raw):
								city_ = capitals[capitals['name'] == state_raw]
								city1 = city_['description'].values[0]
								end = time.time()
								return do_json(_state['state_id'].values[0], city1, word, end, start)
				else:
					if any(capitals['name'] == state_raw):
						city_ = capitals[capitals['name'] == state_raw]
						city1 = city_['description'].values[0]
						end = time.time()
						return do_json(state_id, city1, word, end, start)
			else:
				city_ = stuff.cities[0]
				command = word.replace(stuff.cities[0], '')
				stuff = GeoText(command)
				if stuff.cities:
					if stuff.cities[0] in us_states:
						state_data = data[data['state_name'] == stuff.cities[0]]
						state_raw = stuff.cities[0]
						state_id = state_data['state_id'].head(1).values[0]
						if any(data['city_ascii'] == city_):
							location2 = State
							thing = ((data['city_ascii'] == city_) & (data['state_id'] == state_id))
							if any(thing):
								end = time.time()
								return do_json(state_id, city_, word, end, start)
#                           	      get json and return values
							elif any((data['city_ascii'] == city_) & (data['state_id'] == state)):
								end = time.time()
								return do_json(state_id, city_, word, end, start)
							else:
								if any(capitals['name'] == state_raw):
									city_ = capitals[capitals['name'] == state_raw]
									city1 = city_['description'].values[0]
									end = time.time()
									return do_json(state_id, city1, word)
				else:
					if any((data['city_ascii'] == city_) & (data['state_id'] == State)):
						end = time.time()
						return do_json(State, city_, word, end, start)
					else:
						data_ = data[data['city_ascii'] == city_].values[0]
						state_ = data_[2]
						end = time.time()
						return do_json(state_, city_, word, end, start)
		else:
			end = time.time()
			return do_json(State, City, word, end, start)
	elif 'appointment' in command_:
		from firebase_admin import credentials
		import firebase_admin
		from google.auth import compute_engine
		userid = UserId
		config = {
		"apiKey": "AIzaSyA8E94qwPa4Um0UMoG83rOJ_izZVQt-lGE",
		"authDomain": "personalassistant-ec554.firebaseapp.com",
		"databaseURL": "https://personalassistant-ec554.firebaseio.com",
		"storageBucket": "personalassistant-ec554.appspot.com",
		"serviceAccount": "firebaseadmin_api.json"
		}
		pyre = pyrebase.initialize_app(config)
		cred = credentials.Certificate("firebaseadmin_api.json")
		db = pyre.database()
		credentials = compute_engine.Credentials(service_account_email='my-account@personalassistant-ec554.iam.gserviceaccount.com')
		data = {"3-5-2018" : {
				"10:00": "This is an example"}
				}
		calendar = db.child("users").child(userid).child("calendar").get()
		calendar = db.child("users").child(userid).child("calendar").update(data)
		data = {}
		data['key'] = 'calendar'
		data['']
		return 'It Worked'
            
	elif 'search' in voice:
		import re
		reg_ex = re.search('search_for_(.*)', Command.lower())
		if reg_ex:
			domain = reg_ex.group(1)
			from urllib.request import urlopen
			import json
			query = domain.replace('_', '+')
			f = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyDXPStB0SkGvzwAsef7OkfjyWMjoMAyIx0&cx=001196199226615081657:fto8g4831ii&q='
			f = f + domain
			fe = urlopen(f)
			json_string = fe.read()
			parsed_json = json.loads(json_string)
			data = parsed_json['items']
			json_data = {}
			json_data['results'] = []
			json_data['key'] = 'google'
			for x in range(0,10):
				json_data['results'].append({'title': '', 'snippet': '', 'url': ''})
				json_data['results'][x]['title']= data[x]['title']
				json_data['results'][x]['snippet'] = data[x]['snippet']
				json_data['results'][x]['url'] = data[x]['link']
			to_return = json.dumps(json_data)
			return to_return
	elif 'play' in voice:
		import re
		from googleapiclient.errors import HttpError
		reg_ex = re.search('play_(.*)', Command.lower())
		if reg_ex:
			domain = reg_ex.group(1)
			query = domain.replace('_', ' ')
			import json
			try:
				return youtube_search(query, 5)
			except HttpError as e:
				return 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
	

	else:
		return Command
				
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

#    print("Request:")
    # commented out by Naresh
#    print(json.dumps(req, indent=4))

    res = processRequest(req)

#    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
	from urllib.request import urlopen
#    print ("starting processRequest...",req.get("result").get("action"))
	if req.get("queryResult").get("action") == "wundergroundWeatherForecast":
		baseurl = "http://api.wunderground.com/api/e8f0daedd86a461e/forecast10day/conditions/q/"
		parameters = req.get('queryResult').get('parameters')
		city = parameters.get('geo-city')
		state = parameters.get('geo-state-us')
		baseurl = baseurl + state + '/' + city + '.json'
		fe = urlopen(baseurl)
		json_string = fe.read()
		parsed_json = json.loads(json_string)
		data = {}
		tempf = parsed_json['current_observation']['temp_f']
		condition = parsed_json['current_observation']['weather']
		speech = "Today the weather in " + city + ": " + condition + \
    	         ", And the temperature is " + str(tempf) + " farenheit"
		data['fulfillmentText'] = speech
#	data['speech'] = speech
#	data['displayText'] = speech
		data['source'] = 'Maya-Webhook-sample'
		json_data = json.dumps(data)
		return json_data
		
	elif req.get("queryResult").get("action") == "SearchResult":
		parameters = req.get('queryResult').get('parameters')
	
		domain = parameters.get('q')
		from urllib.request import urlopen
		import json
		query = domain.replace('_', '+')
		f = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyDXPStB0SkGvzwAsef7OkfjyWMjoMAyIx0&cx=001196199226615081657:fto8g4831ii&q='
		f = f + domain
		fe = urlopen(f)
		json_string = fe.read()
		parsed_json = json.loads(json_string)
		data = parsed_json['items']
		json_data = {}
		json_data['results'] = []
		json_data['source'] = 'Maya-Webhook-google'
		for x in range(0,10):
			json_data['results'].append({'title': '', 'snippet': '', 'url': ''})
			json_data['results'][x]['title']= data[x]['title']
			json_data['results'][x]['snippet'] = data[x]['snippet']
			json_data['results'][x]['url'] = data[x]['link']
		json_data['fulfillmentText'] = data[0]['snippet']
		to_return = json.dumps(json_data)
		return to_return
	elif req.get("queryResult").get("action") == "SetAppointment":
		hey
	elif req.get("queryResult").get("action") == "CalendarSearch":
		calendarhey
	elif req.get("queryResult").get("action") == "UberEats":
		eatshey
	elif req.get("queryResult").get("action") == "SearchResult":
#    if yql_query is None:
#        return {}
#    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
#    result = urlopen(yql_url).read()
    #data = json.loads(result)
    #for some the line above gives an error and hence decoding to utf-8 might help
#    data = json.loads(result.decode('utf-8'))
#    res = makeWebhookResult(data)
#    return res


def makeYqlQuery(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    state = parameters.get('geo-state-us')
    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    print ("starting makeWebhookResult...")
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today the weather in " + location.get('city') + ": " + condition.get('text') + \
             ", And the temperature is " + condition.get('temp') + " " + units.get('temperature')

#    print("Response:")
#    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


			
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
