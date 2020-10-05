from flask import Flask
from flask import render_template, jsonify, request
from flask import send_file
from response import *
import random
from lxml import etree
from urllib.request import urlopen
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime
from pytz import timezone
from gingerit.gingerit import GingerIt
import os
import base64
from datetime import datetime

app = Flask(__name__)

def savetosheet(user_num, text, intent, chatbot_ans, data_time):

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('My First Project-359386d74e43.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('coronavirus').worksheet('live_user_data')
    sheet_data = sheet.get_all_records()
    sheet.update('A' + str(len(sheet_data)+ 2), user_num)
    sheet.update('B' + str(len(sheet_data) + 2), text)
    sheet.update('C' + str(len(sheet_data) + 2), intent)
    sheet.update('D' + str(len(sheet_data) + 2), chatbot_ans)
    sheet.update('E' + str(len(sheet_data) + 2), data_time)

def youtube_linktotitle():
    with open('app_data.json', 'r') as f:
        data = json.load(f)

    for value in range(0, len(data['app_data']['videos_link'])):
        youtube = etree.HTML(urlopen(data['app_data']['videos_link'][value]['link']).read())
        video_title = youtube.xpath("//span[@id='eow-title']/@title")
        data['app_data']['video_link'].append({'link': data['app_data']['videos_link'][value]['link'].replace('watch?v=', 'embed/'),
                                               'title': ''.join(video_title)})

    with open('app_data.json', 'w') as f:
        json.dump(data, f)
        # print(data)

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


@app.route('/chat', methods=["GET"])
def chat():
    """
    chat end point that performs NLU using rasa.ai
    and constructs response from response.py
    """
    try:
        with open('questions.json', 'r') as data:
            data = json.load(data)

        questions = (random.choices(data['questions'], k=4))
        response = requests.get("http://rasachatbot:4040/parse", params={"q": request.args.get("text")})
        response = response.json()
        intent = response.get("intent", {}).get("name", "default")
        response_text = get_random_response(intent)
        response_text = response_text.strip()
        aisa = timezone('Asia/Kolkata')
        sa_time = datetime.now(aisa)
        date_time = sa_time.strftime("%d/%m/%Y, %H:%M:%S")
        savetosheet(request.args.get("user_phone_number"), request.args.get("text"), intent, response_text, date_time)
        return jsonify({"status": "success", "response": response_text, "questions": questions})
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "response": "Sorry I am not trained to do that yet..."})


@app.route('/user_details', methods=["GET"])
def user_details():

    phone_number = request.args.get("phone_number")

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('My First Project-359386d74e43.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('coronavirus').worksheet('installed_details')
    sheet_data = sheet.get_all_records()

    if phone_number not in sheet.col_values(1):

        sheet.update('A' + str(len(sheet_data) + 2), phone_number)
        aisa = timezone('Asia/Kolkata')
        sa_time = datetime.now(aisa)
        date_time = sa_time.strftime("%d/%m/%Y, %H:%M:%S")
        sheet.update('B' + str(len(sheet_data) + 2), date_time)

        sheet1 = client.open('coronavirus').worksheet('apk_version')
        version_value = sheet1.cell(2, 1).value
        sheet.update('C' + str(len(sheet_data) + 2), version_value)

    return jsonify({"status": "success"})

@app.route('/user_apk_version', methods=["GET"])
def user_apk_version():
    version = request.args.get("version")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('My First Project-359386d74e43.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open('coronavirus').worksheet('apk_version')
    version_value  = sheet.cell(2, 1).value
    url_value = sheet.cell(2, 2).value

    if int(version) < int(version_value):
        return jsonify({"status": "success", "url": url_value})
    else:
        return jsonify({"status": "success", "url": None})

def get_sheet_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('My First Project-359386d74e43.json', scope)
    return gspread.authorize(creds)


@app.route('/doctor_visit', methods=["POST", "GET"])
def doctor_visit():
    try:
        files_name = []
        test_files_name = []

        client = get_sheet_client()
        if request.method == "POST":

            data = request.json

            sheet = client.open('coronavirus').worksheet('DoctorVisit')
            sheet_data = sheet.get_all_records()
            if 'images' not in data.keys():
                data['images'] = 0
            else:
                file_path = 'images/users_images'
                user_file_path = file_path + '/' + data['mobile_number']
                if not os.path.exists(user_file_path):
                    os.makedirs(user_file_path)
                if request.method == 'POST':

                    for value in range(0,len(data['images'])):
                        now_time = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + str(value)
                        string = data['images'][value]['uri'].split("base64,")[1]
                        image_file_name = user_file_path + "/"+  now_time  + ".jpg"

                        with open(image_file_name, "wb") as fh:
                            fh.write(base64.b64decode(string))
                        files_name.append(image_file_name)
                files_name = ','.join(map(str, files_name))

            if 'test_report_images' not in data.keys():
                data['test_report_images'] = 0
            else:
                file_path = 'images/users_test_report_images'
                user_file_path = file_path + '/' + data['mobile_number']
                if not os.path.exists(user_file_path):
                    os.makedirs(user_file_path)
                if request.method == 'POST':

                    for value in range(0,len(data['test_report_images'])):
                        now_time = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + str(value)
                        string = data['test_report_images'][value]['uri'].split("base64,")[1]
                        image_file_name = user_file_path + "/"+  now_time  + ".jpg"

                        with open(image_file_name, "wb") as fh:
                            fh.write(base64.b64decode(string))
                        test_files_name.append(image_file_name)
                test_files_name = ','.join(map(str, test_files_name))

            sheet.update('A' + str(len(sheet_data) + 2), data['doctor_name'])
            sheet.update('B' + str(len(sheet_data) + 2), data['visit_type'])
            sheet.update('C' + str(len(sheet_data) + 2), data['complaint'])
            sheet.update('D' + str(len(sheet_data) + 2), data['date'])
            sheet.update('E' + str(len(sheet_data) + 2), data['time'])
            sheet.update('F' + str(len(sheet_data) + 2), data['treatment_type'])
            sheet.update('G' + str(len(sheet_data) + 2), data['test_suggested'])
            sheet.update('H' + str(len(sheet_data) + 2), data['mobile_number'])
            sheet.update('I' + str(len(sheet_data) + 2), data['fees'])
            sheet.update('J' + str(len(sheet_data) + 2), files_name)
            sheet.update('K' + str(len(sheet_data) + 2), data['test_done'])
            sheet.update('L' + str(len(sheet_data) + 2), data['test_suggested_name'])
            sheet.update('M' + str(len(sheet_data) + 2), test_files_name)
            sheet.update('N' + str(len(sheet_data) + 2), data['hospital_name'])

            return jsonify({"status": "success"})
        elif request.method == "GET":
            mob_number = request.args.get("mobile_number")
            sheet = client.open('coronavirus').worksheet('DoctorVisit')
            sheet_data = sheet.get_all_records()

            for value in range(0, len(sheet_data)):
                images_list = []
                report_list = []
                images = sheet_data[value]['images'].split(",")

                for value1 in images:
                    images_dict = {}
                    with open(value1.strip(), "rb") as image_file:
                        image_code = "data:image/jpeg;base64," + base64.b64encode(image_file.read()).decode('utf-8')
                        images_dict.update({'uri': image_code})
                    images_list.append(images_dict)
                sheet_data[value]['images'] = images_list

                for value1 in images:
                    images_dict = {}
                    with open(value1.strip(), "rb") as image_file:
                        image_code = "data:image/jpeg;base64," + base64.b64encode(image_file.read()).decode('utf-8')
                        images_dict.update({'uri': image_code})
                    report_list.append(images_dict)
                sheet_data[value]['test_report_images'] = report_list

            return jsonify({"status": "success", "data": sheet_data})

    except Exception as e:
        print("error", e)
        return jsonify({"status": "failure" + str(e), "error_code": 404})


@app.route('/blood_pressure', methods=["POST", "GET"])
def blood_pressure():
    try:
        client = get_sheet_client()
        if request.method == "POST":

            data = request.json
            sheet = client.open('coronavirus').worksheet('BloodPressure')
            sheet_data = sheet.get_all_records()
            sheet.update('A' + str(len(sheet_data) + 2), data['systolic_pressure'])
            sheet.update('B' + str(len(sheet_data) + 2), data['diastolic_pressure'])
            sheet.update('C' + str(len(sheet_data) + 2), data['date'])
            sheet.update('D' + str(len(sheet_data) + 2), data['time'])
            sheet.update('E' + str(len(sheet_data) + 2), data['mobile_number'])
            sheet.update('F' + str(len(sheet_data) + 2), (data['systolic_pressure'] - data['diastolic_pressure']))

            return jsonify({"status": "success"})

        elif request.method == "GET":
            sheet = client.open('coronavirus').worksheet('BloodPressure')
            sheet_data = sheet.get_all_records()
            print(sheet_data)
            return jsonify({"status": "success", "data": sheet_data})
    except:
        return jsonify({"status": "failure", "error_code": 404})


@app.route('/blood_sugar', methods=["POST", "GET"])
def blood_sugar():
    try:
        client = get_sheet_client()

        if request.method == "POST":
            data = request.json
            sheet = client.open('coronavirus').worksheet('BloodSugar')
            sheet_data = sheet.get_all_records()

            sheet.update('A' + str(len(sheet_data) + 2), data['type_of_test'])
            sheet.update('B' + str(len(sheet_data) + 2), data['results'])
            sheet.update('C' + str(len(sheet_data) + 2), data['date'])
            sheet.update('D' + str(len(sheet_data) + 2), data['time'])
            sheet.update('E' + str(len(sheet_data) + 2), data['mobile_number'])

            return jsonify({"status": "success"})

        elif request.method == "GET":
            mob_number = request.args.get("mobile_number")
            sheet = client.open('coronavirus').worksheet('BloodSugar')
            sheet_data = sheet.get_all_records()
            return jsonify({"status": "success" ,"data": sheet_data})
    except:
        return jsonify({"status": "failure", "error_code": 404})

@app.route('/user_profile', methods=["POST", "GET"])
def user_profile():
    try:
        client = get_sheet_client()

        if request.method == "POST":
            data = request.json
            sheet = client.open('coronavirus').worksheet('UserProfile')
            sheet_data = sheet.get_all_records()

            sheet.update('A' + str(len(sheet_data) + 2), data['name'])
            sheet.update('B' + str(len(sheet_data) + 2), data['age'])
            sheet.update('C' + str(len(sheet_data) + 2), data['sex'])
            sheet.update('D' + str(len(sheet_data) + 2), data['address'])
            sheet.update('E' + str(len(sheet_data) + 2), data['weight'])
            sheet.update('F' + str(len(sheet_data) + 2), data['height'])
            sheet.update('G' + str(len(sheet_data) + 2), data['occupation'])
            sheet.update('H' + str(len(sheet_data) + 2), data['marital_status'])
            sheet.update('I' + str(len(sheet_data) + 2), data['blood_group'])
            sheet.update('J' + str(len(sheet_data) + 2), data['mobile_number'])

            return jsonify({"status": "success"})
        elif request.method == "GET":
            mob_number = request.args.get("mobile_number")
            sheet = client.open('coronavirus').worksheet('UserProfile')
            sheet_data = sheet.get_all_records()
            i = [i for i, _ in enumerate(sheet_data) if _['mobile_number'] == int(mob_number)][0]
            print(sheet_data[i])
            return jsonify({"status": "success", "data": sheet_data[i]})
    except Exception as e:
        return jsonify({"status": "failure" + str(e), "error_code": 404})

@app.route('/medical_history', methods=["POST", "GET"])
def medical_history():
    try:
        client = get_sheet_client()

        if request.method == "POST":

            data = request.json
            sheet = client.open('coronavirus').worksheet('MedicalHistory')
            sheet_data = sheet.get_all_records()

            sheet.update('A' + str(len(sheet_data) + 2), data['diabetes'])
            sheet.update('B' + str(len(sheet_data) + 2), data['blood_pressure'])
            sheet.update('C' + str(len(sheet_data) + 2), data['asthma'])
            sheet.update('D' + str(len(sheet_data) + 2), data['heat_disease'])
            sheet.update('E' + str(len(sheet_data) + 2), data['hiv'])
            sheet.update('F' + str(len(sheet_data) + 2), data['tb'])
            sheet.update('G' + str(len(sheet_data) + 2), data['any_allergy'])
            sheet.update('H' + str(len(sheet_data) + 2), data['mobile_number'])

            return jsonify({"status": "success"})
        elif request.method == "GET":
            mob_number = request.args.get("mobile_number")

            sheet = client.open('coronavirus').worksheet('MedicalHistory')
            sheet_data = sheet.get_all_records()

            return jsonify({"status": "success", "data": sheet_data})
    except:
        return jsonify({"status": "failure", "error_code": 404})

@app.route('/user_token', methods=["POST"])
def user_token():
    try:
        data = request.json
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('My First Project-359386d74e43.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('coronavirus').worksheet('apk_version')
        sheet_data = sheet.get_all_records()

        sheet.update('F' + str(len(sheet_data) + 2), data['token'])
        sheet.update('G' + str(len(sheet_data) + 2), data['user_phone_number'])

        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "failure", "error_code": 404})

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

@app.route('/notification', methods=["GET"])
def send_notification():
    # Send to single device.
    from pyfcm import FCMNotification

    push_service = FCMNotification(api_key="AAAAhwkO_zQ:APA91bGDnacCf_sbpAaRGIyCIdLDJJOKA0V4aW648zvUNtUdasgWS9EzCKSfuo-zxjgUf-C1D0U3leIXXOJzrcq-DD8eRFRKnB-ScdKamzGWZmJO7HGKYwCO5Li5A8h_580tPCiJwZXy")

    # Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

    # registration_id = "cHx6_a3oR8aSrkKvNzsBKX:APA91bGzYxURQPzEx9o9-PlIvIfPvQNkC9W6WKUjVuUyzCTUH5ew1jnpvrFLFD3MxxpLQrbvpTp5V2caZSCxtvUhQwPrbV0kPKF409hRwmsjTLv9YHoQwb6EEplUrkRYGgL2TjmqSknd"
    # message_title = "Uber update"
    # message_body = "Hi shub1, your customized news for today is ready"
    # data_message = {
    #     "Nick": "Mario",
    #     "body": "great match!",
    #     "Room": "PortugalVSDenmark",
    #     "image": "https://firebase.google.com/images/social.png"
    # }

    tokens = [  "eekNkLKRt-Y:APA91bHm7o5vS3URVIku3M3MuXH21onafpKJHf1UmldiexpQ3OMq5T2QIS45ahVOg_K-cQhlAje-bi5Y_cRHQqSC30OljZjDE2GNi28WQBf44nZp-84sGlovxRYz5ts-gbA9Tkhw7_TE", "d3lA_OHWRNM:APA91bEG3J1O4GuelOskFyxPHEiCifHGBqvcIlpmUKtlTo5JlYfe202rynrmLDdMREwr_Rb8EnzpwtkLVewVEmiHtPpsesi_QN2M4d5e9npmSjdz1bnNL8DofOitqYOopYdI8esRzMGO"          ]


    subscribed = push_service.subscribe_registration_ids_to_topic(tokens, 'test')
    # returns True if successful, raises error if unsuccessful
    # print(subscribed)
    extra_notification_kwargs = {
        'url':  'http://0.0.0.0:8080/omd_logo.png'
    }
    data = {
    "Nick" : "Mario",
    "body" : "great match!",
    "Room" : "PortugalVSDenmark"
}
    result = push_service.notify_topic_subscribers(topic_name="test", message_body="topic testing1233",data_message=data)

    # result = push_service.notify_single_device(registration_id=registration_id, message_body=message_body,
    #                                            data_message=data_message)
    # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
    #                                            message_body=message_body)

    # Send to multiple devices envfvJY9TtSCGBUwVs55Yx:APA91bHDqF3bhcF1uiAVIh8AHDHNysEnT5dfQi9FnI_RCnfMvjxhVc5G8y_ozgCiTJTxHXIbnwWPTHlZ0RYsivSjH3HZ6VPzQdW3zLjAKImlzQITmpa7ADGxR1spjfRQ-PezCdnFc2BVby passing a list of ids.
    # registration_ids = ["<device registration_id 1>", "<device registration_id 2>", ...]
    # message_title = "Uber update"
    # message_body = "Hope you're having fun this weekend, don't forget to check today's news"
    # result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title,
    #                                               message_body=message_body)

    return jsonify({"status": "success", "response": str(result)})

@app.route("/upload", methods=["GET"])
def upload():
    import base64
    def convert_and_save(b64_string):
        with open("imageToSave.jpeg", "wb") as fh:
            fh.write(base64.decodebytes(b64_string))

    data = b"/9j/4AAQSkZJRgABAQAAAQABAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAIQAABtbnRyUkdCIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAAHRyWFlaAAABZAAAABRnWFlaAAABeAAAABRiWFlaAAABjAAAABRyVFJDAAABoAAAAChnVFJDAAABoAAAAChiVFJDAAABoAAAACh3dHB0AAAByAAAABRjcHJ0AAAB3AAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAFgAAAAcAHMAUgBHAEIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFhZWiAAAAAAAABvogAAOPUAAAOQWFlaIAAAAAAAAGKZAAC3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z3BhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABYWVogAAAAAAAA9tYAAQAAAADTLW1sdWMAAAAAAAAAAQAAAAxlblVTAAAAIAAAABwARwBvAG8AZwBsAGUAIABJAG4AYwAuACAAMgAwADEANv/bAEMAAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAf/bAEMBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAf/AABEIAY8BLAMBIgACEQEDEQH/xAAeAAEAAQUBAQEBAAAAAAAAAAAABAMGBwgJBQIBCv/EAFMQAAEEAgIAAgcGAgMJDAkFAAYDBAUHAAIBCBSUCRESUlTS1BMVFiGSkxfTMVHwGDQ3QWF0d5GhIic1R1dxsrS1trfBNlNyc4GCscLWI0KX4fH/xAAaAQEAAgMBAAAAAAAAAAAAAAAAAgQBAwUG/8QAQBEAAwEAAQMCAwMIBwUJAAAAAAECAwQFERITISIxQQYUYRUyUVJTcZSVM0OBkbHT1CRjg4ShFkJEVFVkcnOy/9oADAMBAAIRAxEAPwD+/jGMYBySJPSsiMbQVp3FAATWfJa76O2d6SGOrnYlIIpUk6kRkEaktAELwila9Y7DBzfzALk4t4JuYCS1qwggLBT3kLCHhkNJLR62ev8Ao/y8ev8At/r/AMWYel+u9AEDaTZT1H1DNM5qUnpyYay1bh0i2lZkpROG5PLSKLyGWTeyJI3s6ym5A8caqLzSFiHaMnu6TLyHWRzFgDGMYAxjGAYto3/ApT3+i2vv+6cRmUsxbRv+BSnv9Ftff904jMpYAxjGAQHn98RX+fqf9lyWT8gPP74iv8/U/wCy5LJ+AMYxgDGMYAxjGAMxbcP/AKJxH+lKjf8Axrr7MpZi24fV+Eon1/0fxSo3/L/x119xgGUsZBkJJjFoeJkHKTVHndNLTZXfjjlZdXfhNBs3T49ajh04U21SbtUNFHDhXbVJBNRTbXTnwOHU/O688MElhqMU4541kpBBLeecp7pb+yrHxLjVVvE8+tRBZFeeScO01EXLN4MI+0m542xjdz5tznn37PTRuY7+3dT2TrSl3Tc5zdpPu57e5T35uON+jKvkcpyqXF46m9vFvsq08qjLj5v38deTpjlTTmbd9pfryc3HRP2OjxfbxLrbnRmxbpKu5F7trtpqp4Ng10WduNUeFNVHKqaXKLRD2nLtRBtootr5Ph56c445e7KjMapx69mLNwiqQOU99UeeUn0m22VaQ/r42doLowir15/ezxiRsldN0OfWjISOiuV1GqO2zp1zry8kXSyrySe86bqqJ8O37nZRyqmhsurw1b8qeGZpb+HZot22uqOvrZP1M8v6GfK/22sruv8A68u9RHb3+K3rfdK4eT+Fafu3K5Xd87VZYv5cLiaXMtfVcnl9s9t+/ZP08Z42PZ3lquVHan4MTFx8Q8etY5qk1R2aMF1eE9eeVHDhVxKcrOna+/Oy7t4424+0cvHKirlyrzsquqoptztz72QE/wDhR5/mEb/1iVyfmiqq6dVTqqfd1Tbpv9Lb7tv8WX8888YnLLOMs4SmM85mIiV8pmJSmUvokkhjGMwTGMYwBjGMA0tOewrTrZ1/o4+nRt5MgaIm1f2uQsEiZ87rKqQPr+cWua2U3gBcQLJAvVgWdfoR/AehtBys5pNbpijohMkR4CL8k1DbxufHtiChSGhw7EjMSwnRiVGj6VLJWUZSNwX/AFw2aEsI/AxZuPO/wvUAgZrrM5mbTRJz0xrZNByyqhlY9o1IqpKquOjqoG7crQAtIeaAMIs1grEDx41h2ypLVEtXJJuhGEkdJMktiKvDk2AZ72EdfvkJMisTkvEwBHMR73IIbUNUV1NFBJX9ZV+DkRsqssZTwgGjo3Mlarg0PrJcbkcnDRzJ5N7L2Na9p2AtzJLOftTizbCLd/anzUlkJMDImMYwBjGMA4l3JeHfeMq/s3I1nG2w4dinUS27E6pFEXU/JiWWzdiFRWG9oEcsoRKOtdSTgFaZeTRjicsnrnvT6MLXxwP0uHMb0Mn9zktHj/bTH9v7f6s0rlrBvtT0iYDVsRxzt1dadL7dPbA3QCZZPTS/X94UgP1FpJ2TKQXMC8U2rqOu3eDBQYm4l47TUhILWgvBSlMv+cpN9+yb7Lu+yb7JfNvt8kv0v2I1Uz4+VTPlSmfJpeVPv2me7Xen2fZLu32ft7G6mMYzBIYxjAMW0b/gUp7/AEW19/3SiMylmLaN/wAClPf6La//AO6cTmUsAYxjAIDz++Ir/P1P+y5LJ+QHn98RX+fqf9mSWT8AYxjAGMYwBjNTu1x/Y1fpdd1q4JnA+uVdoKuDDRg2p0juDktrmeZk6ZYNud4F1Fs6oYfZIs517c5RNMIAJSg/sG8VYBTNDNVHmw/JHvI78oDDPiZ9lTZNWW3W8KPNuU1tUl9eJLhNbaTcpey504bQ6D3RJ413YyjuIU31W43RhrolUw1m/wCtr4Ml2fbu9a7Qvf296938K7tpFPbn8TCnne0VumkuNl325VNyqSnjZK9n3lq2/DxmO+lOYTpXG5dNmbdZ28cItWrdNRZw5cq6IIIIpa87qKrLK7appJJ6a87bqb7a6a68c7c88cfnmErYmXMqLxmsTHq8x/Nk01ppOP8Abdk38XtcIaiwcx0eo32eTTRtJJsXLv29odhJxS3G0POKKK/bIZObDmiqyD4gc8z0ihumu35WQ4bxMc50TT44ViYb7RdFqropwso3fvFpGaQ1cuG+sty221R1tO4P/ROJ/wBKVG/+Nlf5Lvjl+Z230X/fqXOMv2acQ+16NP66qYfvNY2vc0+HN5fvq66fx3/U5XF83Sfqtd488eKqXdOOLW2y+G8+ZlScK9I0fasV+Hzhd1Ly3GiiXMvK7pLPNE1uEeFkmaSCLdjFt1/DNuV2sS0Yt3O6CTh2mu742X2971f2/t/9MYzVel6V5XTp9uy+imV8pmV2mZXf2mUpXySSLmHHx40enhnOcunddu7q7aSrTS6bvXW+y89dKrS2u9037jGMZA3EBP8A4Uef5hG/9Ylcn5AT/wCFHn+YRv8A1iVyfgDGMYAxjGAMYyO72daNXO7JFu4e6t1tmbd25UZNV3Wqe3LdFy8RavlWrdVXjTRZykxeKIJ87K6NXG2nCO4HPPs8XXcD9D0SXrq+MWlvQ9FOZQSTCAfexZ1Z2zpiZ58bAgu9ZWGysk/Fd1UjinaTkpeo4rsFcwvX9HT1whIwfzzhzkzrmW2DP2rcsUVF1ykcFDxaCkbHWVUKFdjI7Pqdmu4ME+jwcmSqavtjFNmCjNZjUeluQFvDumBWiLn9qTWvlxbdy5P6sE8ub9YuuJoQikiBz5dQ1Qk84DzHLrmXDJefr4dlZMUlOX0dDveZEdeu1oh9y7iIt1y5Zq+IjmKvttks84AxjGAMYxgHNT0nXX6xew9HywZWddaWSczADbgXTb9RSu4/Xrb2bPhZpDUB3e1JzwkHpoGU6vTiE/Lfjmk2xf2GFUDBxL1EClM42XYZtQUU9NzhLJzkMQtxl89kuJVsVt9ph3PNU+YlnE7D/EY2kIdl93ewi4dcSeknw9//AFU2HLTltqrursHnzvtxppvvz6/Vprttz6v6fVrxzzz6v6Pz9XH5fnl3g8/l9PvW+Jp6d8jC+No+yfllo5dT2fwtNyvalUv6r2RxOudA6T1/LiR1bjrfLp/Ny6jx07cenyMJtRorntcOVdfHnUaL5Tcp0q1v1pu0tf6L7mv/AJoKX3/6Z5t/bnn/AB/nlbWo7X1/ovqU5/P1/wC6GHu//TNdvy/tz6+MuESvcSMiGPG4yNIm76S5dcILPmkYm008Iycv1Ptt28u5W19pJqprp7CCnrU20129nXnbfW2HHamrWtoztYOdCtDgWssWpAosFUccJ1uM3icgAjaQRVRFPbrcSMJKGQOfgi4ocSUI2p4hOjUQo+Jsp3fpPBVY/wCl1G+vdM2njdRjTibXlO05a4cearKqqJtds37Os6nv3795afyPO9A4/wBhPtNxNOofZ7XDqnDx5N8TTkcXndRrOOTlnlpeNee8vznPbG2uzXa5ffuT0qttlPnnnm9HSn+RUQc7f6+dTTXn/Vzx6uPy49XGeilXdpper2rhQW/96Hyv5/t2An/bn+v8880v7ZdZQR4+iyi+aqYTUWQQYvLjzc1g5clhpggseuajZpzY1Cu5GehmLGxbdrIYJJmTjmkKHuzgddFshCRsgk9zzSHt11/hZZtAxdlBRvMJlpUGFDAJPK9llK4mA0Mv0vnN7OVdl0a3A2DV11nuIHWekCzNNgfB85AS3EdoOFr4e5j5/Kfz0l/8LH8P93+CPSR9n+kZ/m8Rr/meW/8AHdnn04J2M6qWr3jawoVm1d10EuWzDgRId02LdcajFUWae6Vkttd9Gye+qOm2qKXG2qfG3CenHPscZL4DrL/5RoLn/LyHlP8A5Wpxx/szwR+8OtMAKFrOAuym2wjQETzDWIvpaoi7j6jixSbKK9Xb2LKuiFxsIcQhPXJsGyK5e7ZLtiYHLoR+rxMjk23aQnPbrqgySfLvOzvXpohGD8gWySzm6a3QSjhWJIywPlSZ+oqS6aMx+MLQI6F5CZccpxzIiCy2EcuUpIcmWzLU+Vu33d+/4TE/9FKX0N89I6dK7Ljr+3Xav/1oy6Ngyy9uOeP4kQuv/siJTxz/AOKf+L//AH15EUAbLU454/ijH6ev/wBWKk+v/wAfztDn88t2b7g9SRrcmSI+0fXWAUC5CSiTFObu2tIrcTlIbW295iNJdHxMhtBP4nSgb33k2cpw1cMNKUtvZ2mlrW5lzDXZJdg6DhiKKD5e76gii2dJIgNgxaSsoMYkcyXkEjZkRAikVCOZpKTkSSblqVuSLiINo1Wk5KRqWzGTNqs5AylKKzPL5Efm6NfvmH8v3yyF9E6Xp+fxJr6/0myS/clou39hbD6s7L3WYa8277P2rtTTjZMeJtNkueGL1T29P98vb1bc8abJ888c8c+xvtr6/VzzxzGWpyy1f+PCWT/91FlOn+v/AHyufX/s9fH5c5kcftWsjsIWsuvjYTssMj2LmZbEleE8EYQrxJKE1luPu+XgpN1EO1XUNINnjTXl9wks1kGTvXfhBwgvz5QPdAwfTO8HDx881d6MV3+ykk2j0m32KCiCW+vG7WTeK8qc7ONOdeOUeNOdeNued9eeOOOerxvy9yeLyubxZ314nCSrlbxGXp4JryTvuk13S7+yfsjzfUl9hem9T6b0fqV8Hi9U6zTjpnC225S25tTc5ucZm3L7XUy02l3f7ywdqQsznnn/AH+yDXjn/wDbxGEXP+3awtufV/8AHGtI2br/AEX3P/8AzRM9t/0j/nLuc34ExtgPa6n0JoZkuZWQgRecn0YpiInpFCBEdYpCMixFrLrs2xPCh0ioQfhsv4FJshg4E2Ig1gSjdfHUwOxp3szRA+i6fOrVr5xCQc6TwJ6SMjkOVHKq3Cwmxz0qk7TmFJ5FoDQ4/DVSaIzL2Z3R5ipCKcpySLRoxlnkbS/KvUP/ADWn90f4eJ2P+yn2e/8ATMfov6TkfT5f1xb3FK2dx/x8zXP5+v8A3UHL7f8ASO+f7ccZU4pmzuP+PWU54/L8uR2U5/yf08nXr/Pjjj/HnlHPePpxW42SFRf2foxhFigsVGkw3YWWKkRDsOhHNqJlDqGERuSlywmeRbyjLoiuYYahJeadztTWNAMI51NhhCwj79HexdIEk/EB7S1a0QOCIlOBUZBd7LrqRMCaUr8ks4ZIU4CCHyuadSizV1TVoOnkU242IB9ICNo0uhx0jBzSDHsPqfOfz37/AL88X/jm/wBBlfZboK+XT5X7t+Uv8N/wRZril7G5+1+3s9Mh8dHPoBzzJwijTZjDzHKH3oq22ePyjlyvv4Nr7LZD7mX3+z/3My14/pvDQIuVPTVPS7I7XXTXXXjjWrIfjjjjXjjjjXjj8Q/lxxr6uOP8n9X5ZCR7VdX3BJoHN+x9Crlyh8zqrQVRuCvVSTe0JGas0bj630g9CLaT2PXxFStyQLMP1a8kLmaqWzYtGO3fARUhFSYXs51sJGcDIDvYSj55gVN3DsYfQtsAUozI2rQdiS926gXLGfXRmG7YTn4IocLx+7hJEdmoibU21jZJm5Wnt1bmb48fDV8eo43qem3xOK7761NV528XV9nKU937L2NPC+yPRen8zn87iRz8duorjrkTHVupzklxs3nmscp5czkmm6vx/Ov4vZ9yv+C7n/5bY/8A/i2I/wDyLMeWeKW40G4xV9bcTKIbWJULbRsrWrNpqk8eWwFNI6R4VaFCau6kPILtZZJttty2eKstGj3RVmuulvkWL7Idd5yPIZaFvql5eLEouDmyuSjLRB37AZhScuLa/GpcheNZxVvCxZCeAB2Ewb+SUbNJYuCi0bYKuJkbmWTLzxq7+td5vo0OBrrpy0pZ1HwtmxI6B2oJFEy9ghdesT+INGUeKkDqSeDUfrYVPkm8ukmrBrxVhADh4qvEm0HxLVvvWv6vH/hOJ+H+4/BHU/JXE/adQ/m/Vv8AWk/8GXR/y2xn9X+CuJ//ACT/AG/044DLp4549d2RXPH9XNUxX5/n/kJuOf8AJ+X/ANczTjH3rX9XjfwfE/yB+SuL+06j/N+rf638F/cjDXAhc/H9NzQ23/tVXH//AGleuVeBS5OP6bggdv8Anqxt/wDaYcZmDGY+9a/q8f8Ag+J/kD8lcVf1nUf5v1b/AFv4IwskMXDxIuuP4rjfO3DJhzzvtV3H+615XkvZ09nU41449jnXfn2uPz29vnjn8teM9HUauHj1eu1Bfb+v2qt34/6J5r/5ZlThJPhXdfjX1KqJppb7evb800dld09fZ9fs8ezsurz6+OONufa9W3PPHGvHFTH3rT9Xj/T/AMJxPp/wf7/0/Ufkri/tOo/zjq34fL/bfb5I5UVx287BlJqcAs6HxUhND96q13CM6YYwVoSjGn3V39iaIhr+t6CMjWlZiuIVIl6x2JLFIqItbdXZwriETBCGyZtsZRAhCgfSCSpE1jEIqDsjYzlQetzNKrpmoqnGLHYvbyKDKA6/19PQZP2yg2g5Y11xFfl58Mjs7KRyIWCxHEndMjVspJRELIdM9a8ANU9ktQYP1S3MP4h7pcDMLwnsf+J4e/jnbThl7PJh4zXV3+JuePvrxOvDjxv2vHG+fbCvwOKWj3EWEiMavE6zWkUswG4ZmrGaEhCxLiLSPUbsk92Ws+WRcYUTWrblPWUIo5jNvuF5No3dJvvOn6vH/hOL/kmfyXxf2nUf5v1b8P8A3v4L+45GXn6SWyaQruGMn9fycy/Ja1IbAF9+BMTYAJJyH9NrK7hmzWPKULtkjWPiQGEBR8KK5InqkenZGRsSFmayErJZj5kzgctRHfCQlJemWSiJZEQd9PlnFdmUvSgojCOgCRJevQXXVsTcQ17Quz0fEbZL+0lKjwgNSwa1uEeclDqQtqrqygx+elY/oVxVla/bEi+4EILqmCMI1KNnI9FutZ1kNRm0MOx0im5bKpuIyCjFHDSJjNtfu+P0eyO7RskrJP8Adz6bYFCGam6zMOFmiqkrIzqirYfiUFVJuYnIwnl5jdRJppvtKyhJCwxDIyHPPLt7ORMZLOVlX7Bq4Sx940/Vw/heN/lD8l8b9p1H+b9W+n/OnO+6O6pRRgG1MC6WGnbyWLLwEomJgwJF9w1UqO1l6WiCInbL3OxNWIcbWTLVoEOikUAziIr0stcMjzVxHxciznXtv2P3HuwUiQzicpywYzQvPev4HN/fguACUOKzF191wXqByFT9lVX2Qv77lOGOpNLWmy+4BchEpcQhORhaxBCwZhtFxnRNSnKiWcunq1WVwq8fETgveu1AgZ3dOyx1ypy6KHLjaM5VXInPKqvK82rvtJLcqqcqOdud9ueZ7Wsa2ZbxarKvQdmpBskY6FUaicC33iI9sRR5e3YRe6LDTaPZIFkVFlCLVpyigkRRrCa0T1kmbdynOOXrncaTPH8oubnvxeN27y1S79sk+3dfRp/ijXt0fib4bYXp1BZ7ZaZX26t1Pv46Q4rt5cupb8X7eU1P6U13T5wdyqHKuwHTSKDQimmdvkhMNGOtJQr2TBGKfXGzbEAiSL6/9kkTewpyDmBlTrK/nWiqhLVyBFcQswmHpNU4qVlQrBwsl1XzzoiJj4GJi4OJb+Fi4aOZRMa1+1XX8NHxzZJmzb/buVFnK32LdFNP7Vwsqup7Ptqqbqc7bc+jmnbWt9ddrUq9dL0pSu0qrp0+y7t9u7+rbfzbb7t3OHxc+DxONw8XdZcXDLj5vSvLRxlCiXdJSnXZLv4zMr5TMylKYxjNZZGMYwBnzvpwppvpzzzxxvrtpzzx/Txxtxzxzzx6/wAvX6ufyz6xhPs+6+a90YaVJy13VJpr9Ka7Nf2owoI0QJBpDHkkbJETh9G8u+UEnzuMUa7+LZOWCn22jeIarbeyi63209hdP1Kcac7e1rxtrtqf2r9H/FdgiQms1rYtjbnzwNssHFBl4ZwYMFjURc9HzPXg/Zs7DDaufdiYkM/CxBzayVTDVrQ1fTN9BgPZXEeNHMWxOofo3jL3UOp8/qu08jqPK15e8ZTjOmrTpZRV3MJpL4VWltfjTOL0H7OdD+zHD06f0DpvG6VwteRfL04/Fmpzvk6Z5ZXs1VU/Os8cob79u0T7GgDf0d9axcexghq2LtFRiHGaPhIWAh3dSuOUiDrpM9eJuorPLCufqKasG4bPElutgfHsim9TC0ONYImPoDRhpDTseyhZL30fFbTDqcXI7SukibSA0mBjsY/fVYyZAFcxgB2srATAxbeAqeFkH8QGBPbw/iIWZOnxmbyW4pXsiYFhTJsCx4Zb7Yyids1UddbyRrXpqBQV+2nu3n3YkkBPJuHo3d1RcCJnrsqhIys3MVSTDaf2EoV1HjgqpeSNx7OW4YKuzBQkmJKwJo0xFr6N6nEQ8PHGZ3a7ciBL2szsoNWQ52qeeK2lyXGRdpCKyypyPE9TzlTSaROp3GvKN+4JKtHQ7AsJqDWFoqDmRmIlm/QjGAczpz0YVeyMUcwY7f1+1lEFc3NEQnGVPBdVK+j6GnyFj2qjZow65MoDrAg1pa3Jdn2yJ2892LD0WnZQoQrWqGxVcM42YHiNg1HvotKLIbUnbUPLFvCwnM6YFBMoHz85XEMIx8KWj3pDRiTr6OUAauDDHgRSivSYdgNGT98XvrARXgasXUOVtx0j4MeluMA18qHrsPVGEHQciUTJg8suXUnzg2lgqjQUsJZxWvQ+s1JqcSoqoahEZub5GQeBbaTs0JyM0i1ZsR5CQSDR8UGR+5QelxgBmtp2IkJ5y72YrsNkpJzHrNvsXCiCm+3GjWLZqfa8bN9ONNvtfY4453450555451y9jL/AB+p8/icXlcLjcrXHi81KeXhDSjdJOUrTTb7JtezXzOH1D7N9C6p1PpnWOodM4vL6p0anfS+brNPfhU7Vt40qSTdyq90/dGr031YHym1H1llVkWSRRes7JGgjVcghViFf11YstVfFKPbFEJKKq+NtZUkVrSRNBr7vLrOKw3VGxCp3+FeX7UPdCmD2Po4a9a2BZ9qOLtvyVsKxG1RoxJVJK0bzJ1o7oVPsQtT82LqMqMZJmxGGz3ZQuKVSC/ErmljKXGAVlYbsvGY4gHybojjKB3DmkaejErk6gC0alb97GxsbYQZeoVY6osvQIpN2Ox7AadvVSfawSaAoBgSGkKJznc6xDOtKyI5WRpUJsANrI9j6yULYsulzXLFQdHgijbWl7ar+0bfaSZi+MHdmjUmvVksK2e2KL77X9loyKJE3dVbEUEyBba7jWrNCTityQEl3DCNCoY0lDCPhpJGc3VxgHMIE9GqOqy0MQ3Zatgn+4X2j7g9g6+AIl0EwFcjMb2mJO9kRLivi4at4Cz5JOaqfuzINjBSWsCTfRlgVuGSdfzg7AJl8aeZFh+gAfFp7crXJZ71/KSK8mdTbCuengFO2msuKVWJrNLLlqp6sADslg37aoBNckGOd2Y2dxuu1e2FEllRQ4hXYzvxjAObMz6MquJ7coWkr37FLOLDB6yrO0t039Htmdg17SBnZZ9SYapAtqLSGa1HqqJrZMnY1G0bCVUhJovG7Yz4KUUNtVdngzreMg1+Wp2AhyooWmbgW2flIe/haqVGm81+BqSrpKXhiVtWjS4mn2QzRAqlsPOrUfBjuQlJ2UkBl4+biS4rsRjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxzz6vz55444/wAfrznPU/etKQE7+P7liokdEAsVT7E0uuIouVJKx+pppOHQvTE/xHz8ylISVrWA+rOTIPww2j4FowirPqAcXRRLZOaZtbfH4PJ5ee2nHz9RYVhFzL73V8nT0sYzhfFdXff2leyTb+RX25OOF5xrah6rWpb/ADVOMed1VfKUl9X820l7s6MYzn0j3Mn4exj2AMKUuKNludaFFKwoZOJq5/bRLYNjb3pMT+jEghbRkqgXg24DV6x2+npK2GI8NjooUIyckzJmzgezIlC2Tc96UGVFLJ1AVnaXF19ggyFSsUKbnUeFw1a9jT4EihwwFa5tIZjyGfigoYRHZKQF7V3h1CdPYgaTBFFp+FlLHI6TyuLn6u7xjLy4k+otp0lrm8f7znpCy860ynPutNcpvP1JrPOtKlpa8udhtSjP1KtrZ+LioaeGnp1Nefiot17zFuaUtVahPubg4zm5X/Zu6RgP2sa856trEaz913h10rqpaPpt9Wp2XWJUFv2iE8TKR/cfaqXrSOh3lf0qfWLLwhUqIt49vpxExpvMTcZGRBpkJDvnW0s+EIgSru3jmenhkyLyocE4oEfkdcwdb2HM1TYqr6Cd2HHyVtSASei5ZATMJ1ib3zNLqQjB9Cx8tGH1VPD6enROoRekxkt4y10wvfJucVrktPUnz3nFqU8tYnRystNM7zyu7lyoz1HiUpdaelVxOk532eji3Kl+Ob0Xd+cNym6maVXMp9zeHGa6UndxHa1gdlgybq4iAmNEW5FVtCT8zKBj9qctJGrgGweZJs3GS8jkI91wiZNJpJCUYRiHIeTBP2qyZvofhwPsXnP3w042npaqVfp46fBpGk+G+Ub5tXnVQ289IbSpuW3NdqTStZaxtC0zbct3PxTUPvF1FfDSTXapa917/NewxjGaTYMYxgDGMYAxjGAMYxgDGMYAxjGAMYxgDGMYAxjGAMYxgDGMYAxjGAMYxgDGMYBZ1iBrexQA4r53OEYw1Og8lDnJIHSKUOXD7cnhXsKtNi0su0foxZFFJvdn0LIrMXqTKSbtnO7VxqlyltqYXejq6qTusj+Cq1GqLWnK6sCryJ1RIVWteOCMaPfw3IJrzWzcGfJup8EMAsOsCup/RJGTGC0dR24XeD8wTwE7vJjLnG6hzeGkuLytuOvN6NZW4VW5U+VJe1uUl4eSfg+9R4023o14vH3ffbGNH2Up3PdqVXl2l/OU3+d49vJdlXdJI0oU6Wtn7+SLyDsJe5Jbqk5XpILXA/0pWMJwCXreHskaiuRkcFabHa1fR02J29ZAoUxZkEFbWUhip6o14jZltFy8fnykqgjKPBNgeNKSw22dGFinsyVm+wxySzxVaZ8SWSXyUgkGDAYLNdXJOVSyjNjBjEQwYstm7RFrxqj7e+W8ZnfqHL5Ofo7aq8/LOlCyyhSsc3llEennLjLOHSjGHOU1V2oV3VPGfE4+V+pnDm/j+J3pTb0ryuq8raq6fz0rvbSU+XiklrBL9VAp+ERAjGE5lASQtd9o9ggw2afg+WIRWwrfL7WJzPlrFFAhOgszAOY26rDB2USUB86owFZhB41fJnMTEGjGwLH6RRNsArWvjq+LpnYFeE5gyvR5F0CtoU8IFc6WQ5CzhlKN3FayOx1YhewsKf0wPVwXpw7aCdyEvIFoiGFQ5u9jJR1TnZ3Ok7t6Rre8aXnlppGulVpVTd51cp6XWqhNRO1VrMrRuiFcHi0ql5LxqJzqVVzNRKSlNTST7TMw215OEobc+xikGqhiBHt0HMaTEkhpdpWLnE2LSuo9vADhQN1yJVa4kRddhAMCPVIiFQIO4mGJDPEDRvJQ272CThtJOSbucrYxlPTS9aV6V5UozzT7JfBjnGWa9kl8OcTPf5vt3pum27EROc+MLtPlddu7fxXTun7t9u9U32+S79kkvYYxjIEzUdt2eIeLQJKxnaMKxZYJDQ2yTcqmzyqUhcXro0ITwfZlr54kYqLKtYzatS+Sl2aCG71nHMEVuUttnaSeZinr2pIVhXBIT3BV44PNBYaOXc9OHotEwrQLM5XiCEC5zKv5VuwbjBVN8/dA3PLONIqck+OWMY6cudeU+Lcjq3mIfsfZl1SD+ETDymiKbrhq32dudZdnL1qd32WED+URWZJRjeDXjLQgU450lKuHSrllNaPWLBu2ZuZDk0D1saCXVknP2UkO2Gg87gdLqe6mOFpp5DQEl0/6597a3H+rkNPE0aFOtl2Um7Ijkh0taJgT7YuBiwaM4t8WRykSzz1GXC6Zz/RqPT4al9I49zhpt478jnUp5Ke3M15EY3x5jXRruo8V7ylFUcXXlczi+aardv75pL0iO+eXH7em1nhGdaTq7ie6Tff5Pu0jrut2O6+twZlZy941GhXEjP8AInHnatjCKYi+KtV3TbYXZkO0vxFOSPVyxet9oJF1vKars3SPLThRurrplGAn4Iqg4YnF5qKIxoii2E4PkMDItJeDnYWVapPouYh5aPWcMJOLkmS6DxhIMnC7R41WScN1VEVNN+eXZt1DvkyL2V3LqQUSYuOy5Nc8xT4jfthg0G1FZzquBdbGa0XbYzWrObc2rF8Vuzn2qygbFDKI/YVi17vNO2zpAxeb7UBWbWoamGARtAthlVk4J52VhWZ4SWc1aEZsXTxwUqIHpfCDRGTJviQjlX/EhJj8Mpx4rw6Ea0aoII60Ofw+m4cXLXi8y9+TekLXHz49xx1U6vXGrip01vC4zS5WWT4vJnVvN5vNLS1xeRzNdqjbjrLKYbnRzrNaNOPC1NJzC0VW3jdetk4Sry8m5zJjGM4x0BjGMAYxjAGeVOyyMDCTE45TVWbw0VISy6KPs8LKoxzRZ4qml7e2mn2u+iO2qft766+3zx7W2vHr549XPALIpxOixLCNN0U3czATMU1Uc7b6N9HEhHOWiG6+6SaymqOqq2uyuyaSu+unG3Oie+3HGvM81L0zVvtDuFb79u0ul5Pv9Pbv7kb8lFufzlNeP/y7Pt/1NU6t7ljh7J1JHFFbHNUtLzpqevSsicwlq5eik2FjMYCzc4zfvRo4mJocIo6AP4afcNiAfjoP7rQk+UiJWRZLR2uYY/sl14lg2VsWKvWn5MAg5WKgpk1j7ID3orFzc9pFqQMO/n20wrFtZSdTnIRSEYLOtHcunMxKkck50kmWy/PSJ9HWbClQr1sNlUXJSFidBCjqrZMzYVl2nY/8PrIcBkZFQ5DQjg3aEUmKVUYzjqbb2tXkO6BRp9FBlMyo2JRsgIyEZJXat1StZ+2ly15WInvYWxBVDvWSne6fYoxPFoiuIe7GaCld3BvWw1L1DOjMzbku4HFUoAwgrQCSc+r+x4ESYFfL2H9VyuF9nddL043LrPP1ZiMcryzXguT4OmubytdI9TF1M2t95zrBcnWYw5URhxc+T1WFMacdXXg6q7jS35ekq7KuPjEV437teEOp09KW9MarToQNWzVhmyH5IPskDKo4sHp8tFn44XQE2yJBUUkouGKCSBdRj9yhLwQ3MTcNFT0sw3cMYeSlo1jILt3T5skrrBPd9KUD5A6dl06Nx1fjpb1tFQ6wY84GX0PYiXZNsPO4AohlX7qFiNRQXjSLQsIZiOIJ7T+H0ROmDRJRvH+BXxdCUV21FOKlLto6k7EsKFr7udXx03lT9WuIrXnsReVe2lXxN99131qj4YpmoseAeIu0pZlU4K5JzeWclbaOd7v5VzvZYL0pvCuaOWEGrysiM1iWvo2JCIjtSoliR+ZlulTulZI/i3JAsBvHsQ1LF6zl2YXKcD0lsrq/jHM9HwnGztFtDj9O6HD1fK5saxWmWOM58vOKTXV4w31WijuoXAl7Tpvx4z0z2rSYThOM68vqVKVlxqipmrt1hbl/7K7iOzrs29n4uc9HU1Ew6abVdFG93Uy7sRWomts1u4tZHZ0mrWqBuNKniarGJaT75HYS0ktp7hdlAyEfOPUOWH2zSGfsZRxokxdt11MoZz5FKBvQc7EwJVHMK1GqjbXRa9ombSJPCAjjCxmbiVqxw1MCVQHtYE+1KXGmQnEavaRXUdzhwnZGi9hFM0OyklZTsWFug2cPn4cbC8FxdvWjTjZ66P1M9KjZ1pNxSySnJvwWk5O9LjO49S1o6zjpcXXbWdXtn6bnaoheFwqhTLVLzflfu3LtTM1UvwTlKqYxjKJZGMYwBlnG8+TDkQg/FQWUsKRUkEWy0JEzY1AuW7Pdu6VUk93hTKRMcoggsi3bbtknOzzfd4mokjuiivuneOfnPHPPr9X9XPH9v9v/APeTzqYuKqJ0maTrO3ai0n7zTyvPRJ/J+FzX6KT9yNpuaU1UNp9qlS6T+jSqalv98tfgao1H2fcWqJUmeb1dLgopfioovX7sxPKzayktDltWmtpMnrCBYlL2SlpZpFCbRB+KRaTkiSaTDwhSYrQImTvY+bz3g6Y8a+1/dada+dfB8SOvOt4Vpt9ow9hZTZ6jxqS88rtU027jdZdHhRJDRuvstsnwipzrjoG6zHgzUvo7wN/KiSsx1KkQR3ZDhm/mFI2ZSGOqlt0ZIcBKy8C3cyW6xaeREiz4nGg3woOt5J2tshJItYh7IovrSa1lz0q+/pARdcdcOmph16Nfuh5LL8yJyQp9WtW0sK+LgmHjRnjakzHl5IS3MJL+qUgPYhV/Gyf3V6LkY9BrTlaTbyznTdcbDi73MvPJ9TrJ1fKnma1W88Xg5qvKZmub6ni1KzfJz16mpylwqpxk9NNsk2q0XEVpTi8ZSyrbkU12pueO58k27WwUx2Aokf8AwNzO3RVMNrZzCNlq33lLCE2Oh9EzK8S1h5UN3cyyWpLFyzufgGkZIw3Lxm/dzsK1aLrLyrBNxl3OPavQ62WAWAiD+NGLIjFujPXrqVZY1HdlbgoQZcytNxlmx5I4frBFYkzmxgAzZWfJx7P77i4OcHtYnjRGDdomUsuN9g+OPVxxx/Vxxx/X/tyh1PidP4qwXB5dcx3Wy10bxUdp9P03GcW9s33rTOltEq/SW2NVGnjna4e/K2ev3njrjqVn4T8bpt+Xn3qkopdlNJw+8+Ti0qnu/wBxjGckvDGMYAxjGAMYxgDPnb2vZ29jnXjb1c+zztrztrxt6ufVzzrxtpzzxxz6vXxxtrzzx+Xr4/p4+sYBF9h78Q18mr9dn59m8/8AXtf6/wC81f8Am+OyXjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAIvsPfiGvk1frsew9+Ia+TV+uyVjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAZ8768b67ac888cbcc68867babern8ufVtpzrtrz6v6NtduNtefz45454z6xgEXwaXvuvPPfqMeDS9915579RkrGARfBpe+6889+ox4NL33Xnnv1GSsYBF8Gl77rzz36jHg0vfdeee/UZKxgEXwaXvuvPPfqMeDS9915579RkrGARfBpe+6889+ox4NL33Xnnv1GSsYBF8Gl77rzz36jHg0vfdeee/UZKxgEXwaXvuvPPfqMeDS9915579RkrGARfBpe+6889+ox4NL33Xnnv1GSsYBF8Gl77rzz36jHg0vfdeee/UZKxgEXwaXvuvPPfqMeDS9915579RkrGARfBpe+6889+ox4NL33Xnnv1GSsYBF8Gl77rzz36jHg0vfdeee/UZKxgEXwaXvuvPPfqMeDS9915579RkrGARfBpe+6889+ox4NL33Xnnv1GSsYBF8Gl77rzz36jHg0vfdeee/UZKxgEXwaXvuvPPfqMeDS9915579RkrGARfBpe+6889+ox4NL33Xnnv1GSsYBF8Gl77rzz36jHg0vfdeee/UZKxgDGMYBpVXvfvrlYLe+ir8ZjQXStAG8dXU12KOrUoWIpwtMFJuUEiKJHnjC3Jc6FdhE5ilAp05ucEqlqbSz2KlahWskPkmpPvsaSXJUIaTwYQX2pXAqaEw4TGA2IEhwMwZQQiQWz0kTEpg4CTlGstLDgnHqJviabYNHEZAs99HUo6aobcb86HHnWvsuPglNa1BEUIdGFa92u1/Y2aG7EN5CtWEwA3xMdxJASixK5kOt3YA3q03YNuwQfGHEpXIMME70e1sINibTXCpWdGrM1Tp30dfbio4vosJs1+sz+OomjfRw1HfpK6JpojhDuJ6YwqaU1B/wXs3rdYaZSS1+YOj0/6r9gaouLpkewhbaMI/uEPNoigB4ZtIDqFX/crrza6FcTla2KMGVe2iPGs0N2jHlIcwDtJIMsKqav1DXrOeJIg42LSkyt8biBppFhsnFePQ2iSKYHp0mrqJN8hJdh6AcV+MWwheVPLVYbT8aKBllJWYFqABcUzM+sKQ40MGOk3sOz8/LFLdcajIaKkXci/n0VYdq2VkU923HGezvRcX9bw91TDy7jrusL9fEiYELoaVKzIribOrRb0o/oye4kY+dwclTbKNRkC2iel9rD5bX8pzLQUPYZQDiCJgXB8qSHY1d94UHZnXPtKZ9v4EDBLxbFdtdjJ+u6MkBjslLjcLBW10u6OgJNZ8tP0F1I7UyALckeb9ObWBoOETrVw2suu+1By2hLCcWNNuqdPAO20HOQpNCxBINy8WQDpBFx83AT8HINJaFnIWWaIv4uXh5Vgq4YycXJMXCD2PkGS67R40WScN1lEVNN+fUzTL0cVfGdS+jz6HVVY48+ErDrLpl1er48FJT7H7yGTMMpAGGygfkfDKuG/joacjX0c7+wXWR+3bKfZKqaezvzubgDGMYAxjGAMYxgDGMYAxjGAMYxgDGMYAxjGAM1C9ICE2fYnRztyIUe9sGPvKU66XArRzuqrAJqusFK6YwEnJapeBc3ESQRmIeQVsJiOJcpKEDKElm+60MTaPRuQlmDnb3NYO695F3WLqJ2X7Hg4kOHRFQdF2rczcUKyOTFoWZa1gDTps/aLSsQPkj7ldRlBras2GjJmnJuuUmC03BJONpZoBp6Rw/asH7RdtrOHpKynECQwTQB62CpO2ue3anjbAt0N6YVqEWy8EASyWABA0iH22On7yxwZOrU7lqqGGex1+StxxdXXxBDbO4nVbGoRbh8nBAfdY/DAqh7h5VYpdqLCcQdqzo8O9N+KAGqwmDvsbHLR1lGUfWNlBy5RJOw12hYcPepteRHBRfYiEO7szva/YOzRS8a5qwZr6FioKWdEk6REthzLLlc+Bxkt6qAbxSoI0LnZt/GONpztG/0QlrLj4WYdGVGTFdta2VEbgDr5F4w3fpXXY32vs3seZBC9KdYoh7JzdlBdJ2kAJ7oV5Xryz7umYaDfndzbWgHBg/JDo41n66lHcn/ABVFrjq6QGUycD+yegYGlqztgXrp1BvpK/rhnuvNa1EENpUJujtHTz6++yJ3alb3JcxSWLzLo9nV+v0I9GKi3bmdXkHYCZrKlD3tt1pAxMjeDsrUhBhJ/UvbEaahDJ+Ydl7gGRNdYYsDasje6qzNrO6dCPouzcAkWQSys+2UnYp2gO/SKrsDESLi64XXadkjMDE1PX2/AhZeeibuC/SqsdeOvzm0BcS5YFlc92XXYN518JFuyUZVli9QpCpV4+VhZeseJrZ/WFyiRtxNVxHSUVpbc9P3F1lAkQlAyPpCIbdPqaIzUvqeuieyIgbH7CnA6BkDqCDZaQnhGGL145DYkixecl42GlZoeYzHjG0NLSUPEv5GPTbu3cYwXWUapAclwuqe9sYTj7pGyzt4muS9XTYCZPS++pQLDFi30hnYK3/SKVcWSVsRbMjssbFOjRxVHX7r8ZX6LQLCeegUQTdfq36/kK7wdF+2eMYAxjGAMYxgDGMYAxjPzbbXTXbffbXXTXjnbbbbnjXXXXjj187bbc+rjjjjj8+eeeeOOOPz5wD9xkXxzL4xr5hL58eOZfGNfMJfPgErGRfHMvjGvmEvnx45l8Y18wl8+ASsZF8cy+Ma+YS+fHjmXxjXzCXz4BKxkXxzL4xr5hL58eOZfGNfMJfPgErGRfHMvjGvmEvnx45l8Y18wl8+ASsZF8cy+Ma+YS+fHjmXxjXzCXz4BKxkXxzL4xr5hL58eOZfGNfMJfPgErGRfHMvjGvmEvnx45l8Y18wl8+ASsZF8cy+Ma+YS+fHjmXxjXzCXz4BKxkXxzL4xr5hL58eOZfGNfMJfPgErGRfHMvjGvmEvnx45l8Y18wl8+ASs8ArFBc7FyQHOBuAMgoygJgUMA8rh44iFysXIo5zEEA2SD8u2eRM7ATsS8dxcxDyjR1HScc6csnrZdsuqlt6vjmXxjXzCXz48cy+Ma+YS+fAMRkXXLr0XlDQ4LKIponNY82jbKYGBDV4RNFLKxodtXLOIPmhBJQbmWbGsWzp+pGkcVIu9J1k1q2ukGz9JIJGtYy+4oDB4KIWH4QNFIeBcFcydrwkUOxEdELG5GbvrNITJWNZs0WShVO2RKSVgzJDuhtLyhvIPit88Xnnbh+pcPjmXxjXzCXz48cy+Ma+YS+fAMYy1C0ZPEDwtnKYqeaKpEjijGQJpauhCSIHxdBSVPzEGUvJp5DrSTkjhpfr1QUrFTazneTjpKjqffM3SLmtAtWFyg0ZtGDZFmxat2TNvpwm3atEEmzZBPjnnnjRFBHXRJLTjnnnnjXTTXXjnnnn1fnnz45l8Y18wl8+PHMvjGvmEvnwCVjIvjmXxjXzCXz48cy+Ma+YS+fAJWMi+OZfGNfMJfPjxzL4xr5hL58AlYyL45l8Y18wl8+PHMvjGvmEvnwCVjIvjmXxjXzCXz48cy+Ma+YS+fAJWMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMZYNn2tV1JBMzZdz2SA1HXA74H8QWBZxiOgQTBfekg1iI3iYKiqRiYKM5kZV8yjGPD1+h4uQeNWTf7Ry4RS3Av7GWJF2jWk2azlbw1ghcrYQyo/RIgeOJ4V6WQTiJha+JZdrLj7d6pKx7uIG7bqchl2rpqk4i4K061mJBJvHHgo5l/FHL1pIwINBMSuCsCgnUh3RCkPjx4LzUyvAsYSsSZ/MIR0dKOXS8bHjd20sRSL1FLduwgbiqiZeKIxtjhrmaAyrjMVzF6UoPOIZnO29WUS+JHcrHjcfIHQw1kSSRgrMC6Wmo4dj1ZPV5OyMVclkV1UkhHxSDt40s4/CQBZHQsLIGJkKLm/aKZj7YteXRU7UUeDmhg0KHNiCKA45E1AiUsxMnbzisxrFrD6lbwc3YOkym62jtweGlSzVxzARzyQRAy1jMdQlv1QSb6pQFlgcyvtMSg7y2jSyCeOkiKDMiOuZsecNUX27htPw1hhxeBS8I4TSlIw2FCYUetUJ6Alo9pkXAGMYwBjGMAYxjAGMYwDlOa+lgBwoJsKxnHVPtdKA4HcnYWnWhdov1MFRE5X6t2oaUjcRiMGlk9rgYNhYyPtMLdCoNXNmkFedhriTfLlFO0qeBgVaZGAZFiPST1WQXKjWUHUt6yYDvdte9eXXZhCNqZKi420rc6z1V2lqqGesndvN75+7z4KucCE4eea0c6ho2xpT7iKHo/E7syF5JkPRxVfzyHuxO277reeFTnugRvCoIn64SIywD7+9j/7qPs1R8w9JKtJEB+viuyWAo2HTCtmgH2DAhoJgGQbd0NLPi6bJ/VBfR4U4BDuw4xMrXmE1ewnXPss6k5uXCd5N5YPWSgOvnXMIZrfdADERqYxPhnW0ImjOOaRrZ+9LZgueD0sMwb2FHoADVFb0ukatatNy6NI2xCdYbm6s2teFOFE8O169P8AtZOS/YLoNR3T5z15jxa7JzgVGuw0x3FbQjEc7ND9HHA/OE9eylpM6dHIoxdcZ/a+klgpSZ5rgf6pdrCPsXHPrPhzDrHFJdZ9bOAp+qoXrScTMGTm8n2XjutyziaqPtpS1wDcoMXySDbsXnX4hJzkRc8bvVitks/RFUmjqFR8heHZebFaVp9xRvV0MfkFNs4TqqBwtu9W7yptKqJAfpCELy2c692R04oiZrIh7DE94ypG3G30Zebi44+Xdt82Hpno8A0/Z7O8XNkW3al2OuLZc2FZ9ju62azFtkFtjnWcDfFJoNVfWdaVzCSwjWXUSiq4EGVVhNbjP3CMSE4WD5ZYBJPmkgB5/VPvpXHbksIRkLre3wZklTFK9kqxL7LZVsyHL667dhJCxmNUXHWTQJs46MIOBIU6zln7sRusUqG1xxnMDmhLXkQ/evGMdvHmnHWzpDVHVt7Xr6vyCwphWtenHXHpDBamMqNyCbuqOsKpqsAkEtxCCY9svYUvseS/BfKs9mA2/wBW0b9yiY/yi65ebj4AxjGAMYxgDPNmVZdCIlVx9jGyk+jGvlYONmZV1BREjLptVd41jKzjKGInsNGu3vCDd9KtB+ddRzVRV23hpRVHRkv6WMA55Bt09trV672GSQunXKqLoC73tyvSObmB+3bzquvQipzaejpaRhwUalafsS/yjeKg0Bpi3QJ+v6U0/llrASiov7kQqQlwuOd7OwBd1a6ldihcVoecGrf7JVzSVhm/EwcMUyQOM+6gj1cE7Lqun09ZOTA17mr2UmLrcV7bVvOT/qpPuIKjbHHbeMI40mRzc6W6rx/4DJw+v7pvSmZ8guc4vWPs6syEI0MhkzsObnZYnj24+cV8b1AbhblmTz0K0Dbgq6y4OO1cxZayao2WIhJyN+ZGdL6ujKQBaL1nz95DBt+DPZ+TL3cqO/jWwLyi+zOnb0xNzFRqKtRFr/Fi+l54sORoDEAgRimRTLjNWwFbjbMaix8DbrGMYAxjGAMYxgDGMYAzAnauj/7pvq92R62/if8ABH90JQdw0f8AjP7l/En4R/ixXhEBfif8O/e0B9//AHB9/wD3r9y/fsL96+E8D97Rv2/jEc95qD6QVK0t+iPc9SjlrDSupn1U7DP6f0qXmf8A4muLUY1EYOq5bgWgppuVODDczShNhpiN8ffEhNaMWDRNzy53ZuAMQmHRwjkbk7HXBAWDHcOeynqByODQeW9XTkXqA2D+oVT2j+HZiu7ZZDet3NAGgLInwq+tK6YWwqQFlIV+6NoGsuv7dgdZjJ6HuZ/YBsdBt1BAW5UrPsGG0/urSz0mkq9KbnievDsXMSxd7a7GLsdtW9iU+dFTwabw4S1OxexA8F2eiLmqpIxtPCHZKaMJzslQTGJ27T7h4jYkvAOeKkE77EK+TtxyQdPSwK1tqYDWcYO2dR/FPz/YBUhMy1xOdc2Upsa1rMSKXYgJD4JhiPqQcdkhGtO1xEvXfZc9shjDjc0KhPY9W14CLIO3BJyfR5VTMIQnSBv4MVhp7Sno6zL/AOq43Bei9axJNua9TgYQHQy8tuQNzmPXouFBgmDKaPVKNiIau6VoGj3LXni4GNZU3WaCXM+VCoeeRcZHjd5EEUSEwLGzZfNXSB8b1lQlkH4fY7SGLqemMNu/R/pD5OIE9SWYiHLVhcrfsPV0abixLakfCWrC+jvM/RzCzMveyFoDpie1tG1vNCRzLQjswh7FIjEbIOH1spomTdwK6dSpd6QGjrBpMEBoS5uwC/X+I7b0cXnNtjFm8gPYJCz5Xpc56TksiS11pJxM67q6dvgECr07RHAcuURlfdcPSHH8AFqutZ7d32Hokblw2mqxD54hNy6ZFAkeG5ErsyTUmrEJ3EHHIRexCczKrOP3liya4acSRBJ8sGWr+UcunWjRsmrqjoBpg59GsAqFDyeSsQt3TKHnSyesVV5Gj/M6Ym3Sbuxbff4ZPfGRTKHgIQiuXsLc5lKXU1jBZMXdQDriHrMcrTjhBw06T4xgDGMYAxjGAMYxgDGM/NuedddueNdt+eOOeeNdfZ42254455414532119e3P5ce1trr6+ePa2449fPAH7jIviFfgXX62X1mPEK/Auv1svrMAlYyL4hX4F1+tl9ZjxCvwLr9bL6zAJWMi+IV+BdfrZfWY8Qr8C6/Wy+swCVjIviFfgXX62X1mPEK/Auv1svrMAlYyL4hX4F1+tl9ZjxCvwLr9bL6zAJWMi+IV+BdfrZfWY8Qr8C6/Wy+swCVjIviFfgXX62X1mPEK/Auv1svrMAlYyL4hX4F1+tl9ZjxCvwLr9bL6zAJWMi+IV+BdfrZfWY8Qr8C6/Wy+swCVjIviFfgXX62X1mPEK/Auv1svrMAlYyL4hX4F1+tl9ZjxCvwLr9bL6zAJWMi+IV+BdfrZfWY8Qr8C6/Wy+swCVjIviFfgXX62X1mPEK/Auv1svrMAlYyL4hX4F1+tl9ZjxCvwLr9bL6zAJWMi+IV+BdfrZfWY8Qr8C6/Wy+swCVjIviFfgXX62X1mPEK/Auv1svrMAlYyL4hX4F1+tl9ZjxCvwLr9bL6zAJWMi+IV+BdfrZfWY8Qr8C6/Wy+swCVjGMAYxjAGMYwBjGMAYx/wCWMAYxjAGMYwBjGMAYxjAGMYwBjGMAYxjAGMZr/wBrL7bdWetd79kX4SQ2HE0RUlh29NiYu/H4yYlIKuRGYMJnRB8SycXHNk046Gc7rqp7vpDVHjfaNh5h7wjHOANgMZohr34rJh2K7GUiXtmQMOdaAA1ODiwyMg2RcbMarrHrdctpEegk2g3CTarhsA7ZVElEnahUrMT5vD28MLgkHGgcGUHdyNewt6SRjzXLLrsMR5hJ1i6MBZ8TXqgxAZAyApKno27gufIR2sS0sgIcYdXMwi6wMmFeki1mzte2ciVCtQDretSm0ANy8ZpEL9qrFNq+DZ0Mo6DKzwupNlc7oYY3TDjQyCw56dQAzRchYj+zg6vbkFwmzhFWyLSlCRTr87KQccou1hFSuiK22odXRlYkD6QViSkdaxUHVEjIs7Sn42nh1kmV6MTnnsxNdInXpB4itHI7OjMMKM6+d9emDtmta8jYkfJsbUUjg53WScA4fnEUB0YxnMIc9JPGvp6FgSyqFgxYflqJGbucOiudkEB6e7T9zLf6E9bZajOP4aMFLxrSz78pIpIErAKNaO1ZUCS1vbsZAETgpkQsb6e4AxjGAMYxgDGMYAxjGAfz7mfpO+1dNBNwX6ax3Xy264jJj0x0XXtDVxWx/XdugEF6MU67FQw1bFuW3PX9Z0EXVSVoUIMVtaBAMUKAbCVv9kqVaRXCzR+nCz+T7E7g98A44J+t4PO9T72vCAMutC3FkAlUaBEFLjV91t2pMZ6nADrtcHpCAhlZfYirorrYOXsVxGvc8JlOOrN1a2TD1ZOO6yi2lz9JOv8A1Ko7rW4Ppmtw2HTN7Psa6LIO7Nkx8T4swnd3dflpdjJkVmzSEHYSYmQgNObeLI+uoGYWf7DYzwwZLvZSV1kZqSuD+5c6zfwilOv39zrRX8BZx8pJzVI/wjAP4RTEkqRoGCshKVt+H/wZIPlS1q1KFHbuFVcbkTZvN7KcyaKbnUDhcS99O5AyRWNc0D2H6wEVYlvTf0EJdX6ZD1vuIbqoOKfSI91bD682ZeisOUdmRI7bDjYbYnhyqElrsNIOB/aiA8gmxmXpayyS+9pK47mdtyLszI9ZCE06vL7UnaF+Rl33LBUPa7aAs2v6RqH0eV5Po2rq617OEz+pDLSO7omFRTk6Q2DerCPMKvROdArfh5I1S16HXl1MpK/40VamIpHRUyFFNIkI0bC0IKR51Ew9E9iab7PDtcsCWRHZd4wrEnsyh662Ow5hw1ZzkREp8M1YmdZQk9EZFAqRpiqokPgavqKsK3g69iSaBAYYCARUPigeDNZliRGUMHx49ExzQZii0gjI2dJo6FRZNJ6Zj2MpKou3zRBdMDhV1l9JP3ku9U6CJpr1/hCiVGfR4G1H2tJ0E+gwmfBe8pF2UhW1iLVKA+kLv8mJAr7kpIdNa6ZGtq9cbZlI4lfxZ/UYFrxBz8niDtp3a7u2x0g7gBEYfddqjLq26XemPnrWsdpTFvNZG6tem3ZK9eoDDnqVGNO0UTIUiVQUBXEec2eWlhlf21VGd3ULpGDhEwkXOr3+h8O66dfK7UdrV/RNNgyshIxku/VDqwCRlR7LQhKWGcNKO94WDY7OZGJMD05K4x6tzu5YEpoWTrVVKUI5h08jmvWnrlZIq3BbFoCkz4IaFpcfNQ40qoFKRVsd2A7K354atx6cgX0QiWmz88OXpcRps9ZgkeGZW5mXj1Yil93gHG67O/8Ad9Rn3cqu6Zbij6yq+vs0J2UYXQ7u0mmnXmlPR1ejrtO17IkG/Ybvt0voqphOvrG7WBSxroD3iFtd4F0oSD/XA8Myu+78F9ufRl3VNdgnnd+2ZXSSjWRx2T68Gg6Ivp92RMwGHsb0Tfo0bOcB8G9coMktYpiQms9IKcsYyJayMxKS05vGtn0s89ve+eomjyp62kiem6qI5FnaIzeLOQnq8EZh61uoKGYkLDbgbOpCHcLoWiJB0BBCYzYCSmpZAjMLEwMVLtIuNZtUfeBKzrerYteDrGvgiuYV1zBbOYcEFIEQi3OwuGC9cDPK8ePsI9otyO14DhQHBcqI7cxAYHi4vH+Hgx+JYtAL3xjGAMivnraNZPJF4pyk0YNXD10rwmqrym2ao7rrqcJIaKrK86JJ7bcJopKK7+r2U9N9+eNeZWMA/nJ6nQGw2JyfUi1rwsMptznrZ6Pm4GV2x3peu59jV73is65AztexChCBuQ9iXFgdYB05tjroVWjMK9QWkFvcYM6r2Pm4IortCeoee6iejTLiMy6iC7stJigpIxi3u19Wyq5gUSVgy42vTHbS8Kh0rZta8/LzJfeI1UqAQlVoV2CsJWKtDsEGh8DdNpCgTYZ2TB0FsUj1v68NgqxK1b0LTCFc2+REJfbIAjVwOmE2gWluzLcrKLEFdIPWCNiIm3jY7chmyVhJyc1swZ7STpzy2R50yjAQECJwMILC0JEDQwNREbADg5ARrOGgYCBhmaMdEQkJERyLaPioiKj2zdjGxrFugzYs0EWrVFJBLTTUD18YxgDGMYAxjGAMYxgDMGdmkaBf9e7mH+1JGFCvXE1rgsry6ZixTxKrwzWurFh3QMTRs7YKk8LbiTacjSBaESmWZHCSbR1IIbRUk0kuWq2uc8107g0nKdlepPaTrlBzbAZmr/66XbScOSSrdy7ix+UtStCYFj5uSas+eHbqPinc8i/eN2vPDhds3USR54U21wCykKG6xEHYG2iUdLiFG+nLirD+6AwQ7KWo30juHC1ctq9KTGhYuzNwEW1sSA6tjwByTLV3EPbIrsPsOv15WZFiWyoqasQwq/oOcf3VF1G1gipAOzNfW5RvaQhme1By4qauQgkEgINuwSmB9S2uKt69P3g5UwVoeyQrD12UNZCAcEctJNyCVnpWR2wUB1ebBKDNZKJlmRALVMPIRElrvxwyeV4aWETLTfKm7N+ju6b/AI0Yv4JPRvoppMQenO7yP+1RftuQRn6Hv8edX7aoGXstVq6kPR+0d0Eq37SScTgLNMOrlX9qQml7yt8XUF4dJ6QPCTtK8PJOtW6ZVBgBzVVa2KEmL49GxiaFAN9OwkZ0zKljmgOw9vBg4R9lUKxgJQGd9iHFF24YjLsmTGKyr8RmgI6rm4dwkvsBiTw8QIQc8rEnRMY2aH7NZlialQ4/seN62dDSRKuCuPNHhV/GMeJa4qAu57l3iUO7Rn5inLCgJ89rMpXvGRemfZ5t12ZWMLN+zYpIyPZ4eoUZmBaJtONrQMTjYfN0j1ybEd9WLahTNvXwuZVn1PFGY5Dy04MS2hX1gui+LmjJmZmRt5EPHsBKTloCqbsWRepwBPHwRELnMRPhpE+gnnOeg/RMk1NWJ0KLX1n1lOC3RedQmqyDR+o0gl8D62f0quuie4bGBLYiZ32N9ezXZY1rns9MSRmPMpyCmR8vj+ZSU3IG+zcDfAT6EdXgyRreWig43kZGqm4+xGXJnfF/2LtLxgQRSZjV0PZmlgWgTJXTB0caTcyb9eIO4tDuI67G8vKGVHMq/JpB3KrbjYxgDGMYAxjGAMYxgDGM/OeOeeOeOOfVz/i5/Pn/AF8cc8c88f1+rnj/AJ+MA/cZT9Svvp/tbfzsepX30/2tv52AVMZT9Svvp/tbfzsepX30/wBrb+dgFTGU/Ur76f7W387HqV99P9rb+dgFTGU/Ur76f7W387HqV99P9rb+dgFTGU/Ur76f7W387HqV99P9rb+dgFTGU/Ur76f7W387HqV99P8Aa2/nYBUxlP1K++n+1t/Ox6lffT/a2/nYBUxlP1K++n+1t/Ox6lffT/a2/nYBUxlP1K++n+1t/Ox6lffT/a2/nYBUxlP1K++n+1t/Ox6lffT/AGtv52AVMZT9Svvp/tbfzsepX30/2tv52AVMZT9Svvp/tbfzsepX30/2tv52AVMZT9Svvp/tbfzsepX30/2tv52AVMZT9Svvp/tbfzsepX30/wBrb+dgFTGU/Ur76f7W387HqV99P9rb+dgFTGU/Ur76f7W387HqV99P9rb+dgFTGU/Ur76f7W387HqV99P9rb+dgFTGU/Ur76f7W387HqV99P8Aa2/nYBUxjGAMZiQAvGubQNbWAgd+SzMxS05EjJ5Lq15YsNX3BJKtXjlcfCrWnRSMq+05sWVYOoixoqrTAyf1YTJ6idkoChOsjEKZbwBjLMibGr+ffjsZAmwpOPy6AJCsVbQ8/FyihIMh0qOwRXPwfgXS+spEDk0Wi8TNyDLZZtGyJBEM3aiS79umpeeAMYxgDGMYAxjGAMYxgDGYsmrypgdbGrydtavIlvW5sH1mfbvjCBb8h1k2EgDua/rwiTUf8KRR2do2bW+wWHu9EiIq3PwpKBjZBYpg031zAp8C2gKxZzWxkLWAFzfjuIctC5+LJxuU2i5J5DSibCahnT2OdKxkxHyETIpIuN1GEowex7vVF41XRTAu3GMYAxjGAMYxgDGMYAxjNPvSEWXYFK9Du6F0VUSciNk051T7C2wCEfERCT3MSX1vUheZjLvaIJY6XgJBBKchGGz1nLRMizdsfFNdm+ii6bluBuDjOO0h24uQL7y9uRCbOx0gDa1BOYamOtE9YFIVk/KjguC+j6PXCYiWs0AKWs6Z9i+xd3Xr15ibpJbgZUzHHIbGVozqzYxiHxfJ/RbZJmJ2pddXEvpB79asqo6tFFiXB+BKY61F9tUa2pZr1rlhu4IKEh+qJu1lSrtAPPbvlnwdO1vYMAfSDowEeswEEEdJT7aMA7D4zj+dWpcVOdfJWQv3uZP0jt17oCtt+zHYCZa9Oihu97BXvagBMp1wN2SSAtIUoKWVVAZBu6oDpGxqBr2siWD7dUdcJqNyr8cdxjnWqP72WXpLgj6d7oAiozrXcywtSerWW693EAQfVUK9HCSX1ZPpXhaQGqoiS83jhHvhALdW0bLjG0N09leOE62U67xdvP0HzYD+hXGfzoU93n7AlBlRMZA9pQy82E1I9f1qaixAx6nnfPdIcvDvtfVW9qYY7LqhBGwkd276NboYP0je1tjfSCYAROo7RmSmYuCfu+mp4IVd/wBF+AMYxgDGMYAxjGAMYxgHG6waD7HAtJV+JVBVUe5mZTvb26syx2zvaXO45pUZ+d9xi2p5iVrcS7e9T4axW5ksd1FGRkKa2aRD1YEZMPWYX1tGkFZ/xCqfCNbdfu+MYj0ElbTg7lsk0COuno6QDs0NGFxPVENzkOj5Qc7Nn8BfwD25GmqJQIyFglJ12kCLLojshAd6IkLp4HDzFdxB7mFLd/8AGAfzlGXTnujOVZ09qithW5ayDgmGMa97DR1f9hkaXld0V/SsejHPpMrgyeu7hGC3257p5U/b+cDzIKmmZtDhj8mDWSw2dWTECJHmIyq6zKd7BmrWzdbUmulLm2e1BrVFTCvaRmHGyaxL1M6aEQzZUBKFXYesSiHpmqrYj/SAw7EN3NGsNQVn2hTt4wVfgVa1cFXdTPdPLSNQAEsmGTHLFChI+HkZeGn0YI0HIcphkp0ckm0yPTacZOM3zLSXgZhm0loWS1Q4eRcm1bP2KyDpBJXQDUz0ZM4Uk/o2/R8EpzMEBCbEXSDqhOmM+WSEjLFM4Uy9DAL8hmCWVmFnEtJkEnLOHb2ZkJRdeReyK7ly+WVdKq77bwYxgDGMYAxjGAMs+w0z9UAOUqndB7G01A4mTrV7YbCalQBmf7wr3UNdHMWNyUMRSQe3IuY1YmYQEvFTTyF0et4qSYvlEHSV4YwDg3QXT3sl13KpUklaejJQPA+/lf8AY1VuAWsKn1j3/GG/Q7nrBeN1EmsmCUKOSZtpeFgTfZm1VnkKKGVhlg5aD6vK5mSV3WjWwujnQ+uT+sKEm4WzBF0CFJV2h72XKmJyEqMzMpDifYPvF2JvivEpl8HThKM/fjivrIF3s2yiJ+XbxUs5eRe79wuzV353IxgDGMYAxjGAMYxgDGMYAzAXaXsBEdU+u9xdkiQEP7IEqPAiGzjYXrDgFUN9gUNj1p01nYZtYx1XAu/4FBZlLFEhGKFjWZk42IdsBiOnyRxFQMln3LBtasAa7qusmmLPg/xPWlugJjWFhjf3nMQv4hBj4ekRQtg/vgekImfifvaAlpBh95wcrGTDDxHioyQZvUkHKYFstrjQ/iJY9fS9eWTB6V+jUDpiY7RECUjdiM7llZkeiZALiq8JjOw2EWIksBKw1hSlkAtfRw0gzdF/Dl/XzKQL2mFi/vRTIGoquZsykSHtr7J6DjTMvUBwsPlH1e02eXnaNn7TZgbwOg1T9ZhdR3AoRlxykKPpbmr52eBYEwBiGui432t5F4T7+kibVqslOy8YMQ0lIN5CRb7uosOlp6bH2WySDtNumi0kSeeUc8Iop7SreRVYS2z6PTQapavteg3UGCg3Q5XlGilIxL1VRV2j10VmeuK6+u1T2FSDdvu+oyTr97q2iK1tQ7ihVBNxpoEkEw0sQL/D9lDYqYQgH1bXdmlqZuBtRxi7Wa2DJJ9a1YGMdFVUi+xWn2eu4tooTSDWp9ZAfMGUkHkgZJzx2PjEVLEnA49gWgLDnRtPRga4xLVvpN6LthPozrFV/wBgRqQ9ICRXEPU7Fm9W7jzgR5petbAtmWmLdf8AM47gg6HPAav3BDTe8bLkklbQ4RjxsERktX6ZKWjm8sdXodEHhHZkdDaNTYsCwSvZ+ZTeyPOj0OrOZsIgCIbSJ3ebwrHSDlrVPXWr2PjmkjIcTvDaVePmkVCoR2sVd+jz6dVOeC1m15TTQZOQx/UsqPzrUzsVyohKUX1usnqHVcnIsZAvdxc/Ii3XG2zur/HkDKUdzkXJRUsRrS5KJCE1AgboYxjAGMYwBjGMAYxjAGMZ+ba676867667a7cc8ba7ccba7cc8ernjnjn18c8c8c88c8c8ernjn1c4B+4yL4Fl8G18ul8mPAsvg2vl0vkwCVjIvgWXwbXy6XyY8Cy+Da+XS+TAJWMi+BZfBtfLpfJjwLL4Nr5dL5MAlYyL4Fl8G18ul8mPAsvg2vl0vkwCVjIvgWXwbXy6XyY8Cy+Da+XS+TAJWMi+BZfBtfLpfJjwLL4Nr5dL5MAlYyL4Fl8G18ul8mPAsvg2vl0vkwCVjIvgWXwbXy6XyY8Cy+Da+XS+TAJWMi+BZfBtfLpfJjwLL4Nr5dL5MAlYyL4Fl8G18ul8mPAsvg2vl0vkwCVjIvgWXwbXy6XyY8Cy+Da+XS+TAJWMi+BZfBtfLpfJjwLL4Nr5dL5MAlYyL4Fl8G18ul8mPAsvg2vl0vkwCVjIvgWXwbXy6XyY8Cy+Da+XS+TAJWMi+BZfBtfLpfJjwLL4Nr5dL5MAlYyL4Fl8G18ul8mPAsvg2vl0vkwCVjIvgWXwbXy6XyY8Cy+Da+XS+TAJWMi+BZfBtfLpfJjwLL4Nr5dL5MAlYxjAGM54156QcSI9LWMTsNm69qWEuyXoGiHSIj2JLL9vuwwB9ZUPbUXEdcmvW6JnXCoq9qg2JYRlSxd2DlVasGC8/taPpZYJKxqJzNKd2urcVKg0VxbsNO62UFBNhBJAFw5SfA02KWmqq1pt5rYoRAkAEwkL2kG7mH6/DsoSMSO/J5q6gadiTeZauGKYG1GM51RXpNutzsdqGyygiRp2oLXA7FLUyS+W5VUxnBvg++etnXiCQUB50OVjHYdP2F2TE4absJ0cRESJyUkGoJsSKNJCWar7MWveXq/tAik7zY75JyaWFKVVCg7mubSa3AifD7JGZKR8jo1yFJXIGKBgs5Znp1IGIJAxIPWb+Os4tfw1fSDIlXA2zxll1vYgVb1dgVs1sQMy2urPCxewwEqjtHKceTBZrBsSQWIGOjxBq80ZzMHJMZFto6bN3OqDnThdBJXjZPW9MAYxjAGMYwBjGMAYzmwOekbHrRjrSSo2r5awiiL7Px3VHr4yniZCuxHsMXyXX4b7Ec2myMpmBfrC/XqOr94cHmlnwY1Yz2xKdrtxaNAiV0/j+qhU22v623mz7FVUjY7cXlAt+wsO7KiLRaVesZTaFsbrxddhdfbPaRMzH86oEAr/ABFrAoVCyRRlCvyMRUhJyUGxiTkHY7GAZ4xjGAMYxgDGMYAxjGAMYzXjtAHTJvVDuIG6zG7ZJEiEadwQuabxTsOj3e0ojHuTqfEyGWhBmxVa1in8jYApXhFJxMaUHg2KNEigAk9I6xhADYfGcdhfpxZ9Gz9gPevEDYwToV11WdGV4SSxR1wtksqurpCl+rXXWFKGBJYYDC23HHPV2Sq4mvMirEhvO/KhtePhzGeavbDtq7RQL6/5GddQdxO3rBJKy6g9WNxuEoW4BEG++nsGLwlvEEwO9OmdBV4bwEHUs+oJh4Hz1i5roik12JU3r2uq+oCYraLPH84WA9NgdQ8Zyxm+myo7W7sLEqWr21NKGrSo6f68pXGCVmioQGjm162vq++z062rw2BICwGZZaAXSVrk1SzrDrnLWFfPWUwTblIcKWyN2a1wc+9H0bQbQIajFaxFoDddcuE0gS5HdThWlp9XhP0Xpv0pGuhNhTFWwcwHj4Yd9ip1n2JIBYOq3brWOaERYUQwe1MmrEUkwO3+M4ig/o97aHicamIuYdji6pL1gPoeZ0GgANZUefg3pDOwXdnvZvXYUE2OVJVgAd1wG70etcLBBBZZJm+q8YhRXsqd2MjC7lBN26wBjGMAYxjAGMYwBjGMA0AO+otwqV+ADVL9hR4CIgntJ2H7Gyex7Vh0eVdY0RfRJ2OK0avsmtK97C0XLmMACz17wk6xRm7FeCBCQ1nET8mBNplYckAbXmrPRi2rT2vTOMCu2bSGiOq9QdPaeIp6AqAuCrLtgQ6uijMRJACamwPsKMVsVU3bLFnJu4WvuzNQ9pZzr/MWlepFS1gDpSdBU/VPYXGAcdiP0VhEYJ9aW8/2HhdW3WGVmWwlpD0q+ZrkANz6RLoH3uFIUiXe3HJ6fiuJi+jCdREJZGtmUQRP7PUseNChZuGa16VeldvVW8Km7Cm/cDrK6mDe7LJN7lepwy9RV7YoGG1rZHVrpTWc+FzwsZ90OoEnPl5DaPo+aUIwew4Ox20VCNC4wr0zB46DktbtD+u+MA1S6HU+Y9eujnTOgrETjUrAo/ql13p86Shn3EpDpGNaVCHhZOnFSeqSHEjG6TcI+1YvuEUuHbXhJxwknwpxprtbjGAMYxgDGMYAy1jkQirCCTABnXRAyhDgWIBCZeiZOQhBU0iiWJdwsg6GjMRk4UsESBu0erKwxOMTESQwEjo2lYWTYSTRs6SunGAcyY70c/NeSZYWUfbqYYYN+x1TX/SSJuDSti11U7avesAz1AIK8egTKyQdUohiyj+LJG4aUgSSvVwVQvD1WDCYa1kzYkm13Vii3/XWnW1dTRi1PyiTsi97jOC2NGVQqBlrE7HXvZPYixvwmHOiQzkBQJYnVpEMaDjcwams7CCLOFjZ4zLZls+IpLYjGAMYxgDGMYAxjGAMYxgDNQfSA2tZlC9HO3l709LDMNZFH9bLuuIUdl4w6L4LeUrCtSY3bs3MK1IhnZRV8pB6tGrtw/dMo9wsm9fQs41QViXe32MA5+7doIWO7tm1G6dlqXI3MOJCWk7Q8qRAoFM1PNF8xT6Ffxir1VwR2AfW0eQpNahq+hG6UWPNhST60DC4bX7w1b2xcGh3b7vZ2voGt+1D6KsCiUzGne4pHU4sSly9aUiDbDI16JMc7tBQmoldVm8x8s0MuyC8AJWeyjziUtDmiCe0pyt3gfKCUSWg3fPGAc/uxPbMhq7stR9VCrCSnhFq2HC/siyG6psw7K4EQuk2UpCiZJwTRMI1qqp65ZlzS2Lkt2yrGOI6RHa965T0EOBxK8M9n0Bzx6zekl7T2qdejAqoz1rPYmtUoVR7qzERXFpCLOUHb06Hdm+4fSnakpQvgPwIWIzQbS8hz2Xnwsrcagt0gTkFHYVqIFCqcf8A0H4wBjGMAYxjAGMYwBjGMAZ87bcaa7b7e16tdedufZ12329XHHr59nTTjbfbn+rXXXnbnn8uOOefyz6xgEXxiXuOvIvfp8eMS9x15F79PkrGARfGJe468i9+nx4xL3HXkXv0+SsYBF8Yl7jryL36fHjEvcdeRe/T5KxgEXxiXuOvIvfp8eMS9x15F79PkrGARfGJe468i9+nx4xL3HXkXv0+SsYBF8Yl7jryL36fHjEvcdeRe/T5KxgEXxiXuOvIvfp8eMS9x15F79PkrGARfGJe468i9+nx4xL3HXkXv0+SsYBF8Yl7jryL36fHjEvcdeRe/T5KxgEXxiXuOvIvfp8eMS9x15F79PkrGARfGJe468i9+nx4xL3HXkXv0+SsYBF8Yl7jryL36fHjEvcdeRe/T5KxgEXxiXuOvIvfp8eMS9x15F79PkrGARfGJe468i9+nx4xL3HXkXv0+SsYBF8Yl7jryL36fHjEvcdeRe/T5KxgEXxiXuOvIvfp8eMS9x15F79PkrGARfGJe468i9+nx4xL3HXkXv0+SsYBF8Yl7jryL36fHjEvcdeRe/T5KxgH/9k="

    convert_and_save(data)


    for f in request.files.getlist('photo'):
        f.save(os.path.join('/static/users_images', f.filename))
    return 'Upload completed.'

app.config["DEBUG"] = True

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
