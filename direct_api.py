from packages_list import *

def get_random_response(intent):
    return random.choice(response[intent])

@app.route('/all',  methods=["GET"])
def get_live_updates():
    response = requests.get("https://corona.lmao.ninja/v2/all").json()
    return jsonify({"status": "success", "response": response})


@app.route('/countries',  methods=["GET"])
def get_countries_updates():
    response = requests.get("https://corona.lmao.ninja/v2/countries").json()

    with open('country.json') as f:
        data = json.load(f)
    india_data = json.loads(requests.get('https://api.covid19india.org/data.json').text)['statewise'][0]
    for name in range(0, len(response)):
        val = response[name]['country']
        for value1 in range(0, len(data['country_data'])):
            for key, value in data['country_data'][value1].items():
                if val == value:
                    code = data['country_data'][value1]['char code 2']
                    response[name].update({'char': code})

        if val == 'India':

            response[name]['cases'] = india_data['confirmed']
            response[name]['active'] = india_data['active']
            response[name]['deaths'] = india_data['deaths']
            response[name]['recovered'] = india_data['recovered']
    # print(response)
    response = sorted(response, key=lambda i: int(i['cases']), reverse=True)
    return jsonify({"status": "success", "response": response})


@app.route('/country',  methods=["GET"])
def get_countries_specfic_updates():
    country = request.args.get("text", type= str)
    url = 'https://corona.lmao.ninja/v2/countries/' + str(country)
    response = requests.get(url).json()
    india_data = json.loads(requests.get('https://api.covid19india.org/data.json').text)['statewise'][0]
    if country == 'india' or country == 'India':
        response['cases'] = india_data['confirmed']
        response['active'] = india_data['active']
        response['deaths'] = india_data['deaths']
        response['recovered'] = india_data['recovered']
        response['todayCases'] = india_data['deltaconfirmed']
        response['todayDeaths'] = india_data['deltadeaths']

    return jsonify({"status": "success", "response": response})

@app.route('/data', methods=["GET"])
def get_static_data():

    # youtube_linktotitle()
    with open('app_data.json', 'r') as data:
        data = json.load(data)
    return jsonify({"status": "success", "response": data})

def get_sheet_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('My First Project-359386d74e43.json', scope)
    return gspread.authorize(creds)


@app.route('/omd_logo.png')
def get_image():

    filename = 'images/omd_logo.png'
    return send_file(filename, mimetype='image/png')

@app.route('/cities', methods=["GET"])
def cities():
    # cities_data = json.loads(requests.get('https://api.covid19india.org/v3/min/data.min.json').text)
    # states = cities_data.keys()
    with open('cities.json', 'r') as f:
        cities_data = json.load(f)
    print(cities_data)
    states = cities_data.keys()

    data = []
    for value in states:
        try:

            for value1 in cities_data[value]['districts'].keys():
                temp1 = {"cityName":value1,
                        "Total":cities_data[value]['districts'][value1]['total'],
                         }
                data.append(temp1)

        except KeyError:
            pass

    return jsonify({"status": "success", "response": data})

def convert_time_zone(utc):
    from datetime import datetime
    from dateutil import tz

    # METHOD 1: Hardcode zones:
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Kolkata')

    utc = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%SZ')

    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    central = utc.astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')

    import timeago, datetime

    now = datetime.datetime.now()

    return timeago.format(central, now)

@app.route('/news', methods=["GET"])
def news():
    news_keywords = ["health", "corona virus", "fitness", "fitness and health", "5 health related fitness components",
                     "what are health related fitness", "womens health and fitness", "health and fitness blogs", "health and fitness club",
                     "health work fitness", "health and fitness news", "health and fitness books", "health and fitness websites",
                     "article on health fitness", "pinnacle health and fitness", "health and fitness facts", "health and fitness planner"]

    everything_news_api = "http://newsapi.org/v2/everything?q=" + random.choice(news_keywords) + "&apiKey=34af9c54ce82442d8980bb970fc8df90&pageSize=100"
    data = requests.get(everything_news_api).json()['articles']
    top_headings_news_api = "https://newsapi.org/v2/top-headlines?country=in&apiKey=34af9c54ce82442d8980bb970fc8df90"

    for value in requests.get(top_headings_news_api).json()['articles']:
        data.append(value)

    data = sorted(data, key=lambda k: k["publishedAt"], reverse=True)

    new_data = []
    for value in range(0,len(data)):
        temp = {
            "publishedAt":convert_time_zone(data[value]['publishedAt']),
            "title": data[value]['title'],
            "description": data[value]['description'],
            "url": data[value]['url'],
            "urlToImage": data[value]['urlToImage']

        }
        new_data.append(temp)

    return jsonify({"status": "success", "response":new_data[:10]})


@app.route('/states', methods=["GET"])
def states():

    cities_data_api = json.loads(requests.get('https://api.covid19india.org/state_district_wise.json').text)

    states_data = json.loads(requests.get('https://api.covid19india.org/data.json').text)['statewise'][1:]
    data = {'states': []}

    # print(cities_data_api[states_data[0]['state']]['districtData']['Pune']['confirmed'])
    for value in range(0, len(states_data)):
        try:
            cities_values = list(cities_data_api[states_data[value]['state']]['districtData'].keys())
            temp = states_data[value]
            temp1 = {}
            data1 = []
            for value1 in cities_values:
                temp1 = {'districName': value1, 'confirmed': cities_data_api[states_data[value]['state']]['districtData'][value1]['confirmed']}
                data1.append(temp1)
            data1 = sorted(data1, key=lambda i: i['confirmed'], reverse=True)

            temp.update({'districtData': data1})

            data['states'].append(temp)
        except KeyError:
            pass

    return jsonify({"status": "success", "response": data})


@app.route('/dictionary', methods=["GET"])
def medical_dictonary():
    from spellchecker import SpellChecker

    spell = SpellChecker()

    try:
        parser = GingerIt()
        query = request.args.get("query")

        word = parser.parse(query)['result'].lower()
        key = 'd006be83-b7c9-433c-8714-6c887bc0045c'
        if query == word:
            url = 'https://dictionaryapi.com/api/v3/references/medical/json/' + word + '?key=' + key
            data = json.loads(requests.get(url).text)[0]['def'][0]['sseq'][0][0][1]['dt'][0][1][4:]
            word = (json.loads(requests.get(url).text)[0]['meta']['id'][:-2])
            return jsonify({"status": "success", "response": {"word": word, "meaning": data}, "do_you_mean": None})
        else:
            misspelled = spell.unknown([query])
            correct_word = list(misspelled)[0]
            url = 'https://dictionaryapi.com/api/v3/references/medical/json/' + correct_word + '?key=' + key
            data = json.loads(requests.get(url).text)
            if 'def' in data[0]:
                meaning  = data[0]['def'][0]['sseq'][0][0][1]['dt'][0][1]
                word = (json.loads(requests.get(url).text)[0]['meta']['id'])
                return jsonify({"status": "success", "response": {"word": word, "meaning":meaning}, "do_you_mean": None})
            else:
                return jsonify({"status": "success", "response": None, "do_you_mean":data})

    except:

        return jsonify({"status": "failure", "response": None})
