import json
import requests
import traceback

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponse
from django.views import generic
from django.utils.decorators import method_decorator
from hello.models import Question, Answer

import re
import datetime
import pickle

from urllib.request import urlopen
from xml.etree import ElementTree as etree

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier

from hello.text_preprocessing import data_clean

FB_MESSENGER_ACCESS_TOKEN = "Your token"
api_key = 'Your key'

with open('gettingstarted/staticfiles/wiki_links.json', 'r') as f:
    wiki_links = json.load(f)

with open('gettingstarted/staticfiles/tf_idf.pkl', 'rb') as file:
    tf_idf = pickle.load(file)

with open('gettingstarted/staticfiles/clfSGDC.pkl', 'rb') as file:
    clfSGDC = pickle.load(file)

# на запрос 'меню' отдаем кнопочные функции с погодой и курсом
def get_menu(sender):
    payload = json.dumps({"recipient":{
                            "id":sender
                          },
                          "message":{
                            "attachment":{
                              "type":"template",
                              "payload":{
                                "template_type":"button",
                                "text":"Что вы желаете?",
                                "buttons":[
                                  {
                                    "type":"postback",
                                    "title":"Узнать погоду",
                                    "payload":"weather"
                                  },
                                  {
                                    "type":"postback",
                                    "title":"Узнать курс валют",
                                    "payload":"currency"
                                  }
                                ]
                              }
                            }
                          }
                        })
    send_message(sender, payload)

# на запрос по теме «Data Science» отдаем ссылку на википедию
def get_wiki(words, sender):
    # подаем получившийся вектор на вход классификатору, для определения темы
    predict = clfSGDC.predict(words)
    payload = json.dumps({"recipient":{
                            "id":sender
                          },
                          "message":{
                            "attachment":{
                              "type":"template",
                              "payload":{
                                "template_type":"button",
                                "text":"По теме {} рекомендую почитать:".format(predict[0]),
                                "buttons":[
                                  {
                                   "type":"web_url",
                                    "url": wiki_links[predict[0]],
                                    "title":"Википедия",
                                    "webview_height_ratio": "compact"
                                  }
                                ]
                              }
                            }
                          }
                        })
    send_message(sender, payload)

# отдаем пользователю информацию о погоде
def get_weather(sender, **kwargs):
    latitude = kwargs.pop('latitude', None)
    longitude = kwargs.pop('longitude', None)
    city_name = kwargs.pop('city_name', None)

    if latitude and longitude:
          query = 'lat={}&lon={}'.format(latitude, longitude)
    elif city_name:
          query = 'q={}'.format(city_name.title())

    url = 'http://api.openweathermap.org/data/2.5/weather?' \
            '{}&appid={}&units={}&lang={}'.format(query,
                                                  api_key,
                                                  'metric',
                                                  'ru')
    r = requests.get(url)
    response = r.json()
    print(response)
    # если пришел ответ, что данные не найдены отправить сообщение
    # о необходимости проверки реквизитов запроса
    if 'cod' in response:
          if response['cod'] != 200:
              bad_payload = json.dumps({'recipient': {'id': sender}, \
                'message': {'text': "Проверьте правильность указания города"}})
              send_message(sender, bad_payload)

    description = response["weather"][0]['description']
    weather = response['main']
    city = response['name']

    text_res = 'Город: {}, \n' \
               'Описание погоды: {} \n' \
               'Температура: {} °C \n' \
               'Давление: {} мм рт. ст. \n' \
               'Влажность: {} %'.format(city, description, weather['temp'],
                                       weather['pressure'],weather['humidity'])
    payload = json.dumps({'recipient': {'id': sender},
                          'message': {'text': text_res}})
    send_message(sender, payload)

# отдаем пользователю информацию о курсе валют
def get_currency(sender, date):
    with urlopen("http://www.cbr.ru/scripts/XML_daily.asp?date_req={}".format(date),
                  timeout=10) as r:
      usd = etree.parse(r).findtext('.//Valute[@ID="R01235"]/Value')
    with urlopen("http://www.cbr.ru/scripts/XML_daily.asp?date_req={}".format(date),
                  timeout=10) as r:
      eur = etree.parse(r).findtext('.//Valute[@ID="R01239"]/Value')

    text_res = 'На {} курс:\n' \
                     'Доллар США: {}\n руб.' \
                     'Евро: {}\n руб.'.format(date, usd, eur)

    payload = json.dumps({'recipient': {'id': sender},
                          'message': {'text': text_res}})
    send_message(sender, payload)


def location_quick_reply(sender):
    return json.dumps({
        "recipient": {
            "id": sender
        },
        "message": {
            "text": "Укажите город, в котором Вы хотите узнать погоду:",
            "quick_replies": [
                               {
                    "content_type": "location"
                },
                               {
                    "content_type":"text",
                    "title":"Указать город",
                    "payload":"weather_city"
                }
            ]
        }
    })

def currency_quick_reply(sender):
    return json.dumps({
        "recipient": {
            "id": sender
        },
        "message": {
            "text": "На какую дату Вас интересует курс?",
            "quick_replies": [
                               {
                    "content_type":"text",
                    "title":"Курс на сегодня",
                    "payload":"currency_now"
                },
                               {
                    "content_type":"text",
                    "title":"Курс на другой день",
                    "payload":"currency_another_day"
                }
            ]
        }
    })

city_format = 'Что бы получить информацию о погоде в конкретном городе –' +\
              'отправьте запрос в формате Погода ГОРОД. ' +\
               'Например: Погода Москва'

date_format = 'Что бы получить информацию о курсе на конкретную дату –' +\
              'отправьте запрос в формате Курс дд.мм.гггг. ' +\
              'Например: Курс 27.06.2017'


def send_text(sender, text):
    return json.dumps({
        "recipient": {
            "id": sender
        },
        "message": {
            "text": text
        }
    })

def send_message(sender, payload):
    post_message_url = \
    'https://graph.facebook.com/v2.9/me/messages?access_token={}'.format(FB_MESSENGER_ACCESS_TOKEN)
    requests.post(post_message_url,
                  headers={"Content-Type": "application/json"},
                  data=payload)
    #записываем ответ в БД
    Answer.objects.create(sender=sender, data=payload)


class chatbot(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET.get('hub.verify_token') == "FB_MESSENGER_VERIFY_TOKEN" :
            return HttpResponse(self.request.GET.get('hub.challenge'))
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            sender = data['entry'][0]['messaging'][0]['sender']['id']
            print(data)
            #записываем запрос пользователя в БД
            Question.objects.create(sender=sender, data=data)


            # действия при получении сведений об обратной передачи
            if 'postback' in data['entry'][0]['messaging'][0]:
                payload = data['entry'][0]['messaging'][0]['postback']['payload']
                # Кнопка «Начать»
                if payload == 'GET_STARTED_PAYLOAD':
                    get_menu(sender)
                # ответ на the location button
                if payload == 'weather':
                    payload = location_quick_reply(sender)
                    send_message(sender, payload)
                # ответ на the currency button
                if payload == 'currency':
                    payload = currency_quick_reply(sender)
                    send_message(sender, payload)


            # ответ при нажатии кнопок меню
            elif 'quick_reply' in data['entry'][0]['messaging'][0]['message']:
                qr = data['entry'][0]['messaging'][0]['message']['quick_reply']['payload']
                # пользователь нажал кнопку "Указать город"
                if qr == 'weather_city':
                    message = send_text(sender, city_format)
                    send_message(sender, message)
                # пользователь нажал кнопку "Курс на сегодня"
                if qr == 'currency_now':
                    get_currency(sender,
                               date=datetime.date.today().strftime('%d.%m.%Y'))
                # пользователь нажал кнопку "Курс на другой день"
                if qr == 'currency_another_day':
                    message = send_text(sender, date_format)
                    send_message(sender, message)


            # действия при получении сведений о координатах для погоды
            elif 'attachments' in data['entry'][0]['messaging'][0]['message']:
                attach = data['entry'][0]['messaging'][0]['message']['attachments'][0]
                if 'payload' in attach:
                    if 'coordinates' in attach['payload']:
                        location = attach['payload']['coordinates']
                        latitude = location['lat']
                        longitude = location['long']
                        get_weather(sender, latitude=latitude,
                                                           longitude=longitude)


            # обработка текстовых сообщений
            elif 'message' in data['entry'][0]['messaging'][0]:
                message = data['entry'][0]['messaging'][0]['message']['text'].lower()
                X_test=tf_idf.transform([" ".join([i for i in
                                     data_clean(message, tf_idf.stop_words)])])
                if message == "меню":
                    get_menu(sender)

                # для сообщений с погодой
                elif message.startswith('погода'):
                    # проверяем, что запрос отправлен в правильном формате
                    if len(re.findall(r'\s.+', message)) > 0:
                        city = re.findall(r'\s.+', message)[0].strip()
                        get_weather(sender, city_name=city)
                    else:
                        message = send_text(sender, city_format)
                        send_message(sender, message)

                # для сообщений с курсом
                elif message.startswith('курс'):
                    # проверяем, что запрос отправлен в правильном формате
                    if len(re.findall(r'\d\d\.\d\d\.\d\d\d\d', message)) > 0:
                        date = re.findall(r'\d\d\.\d\d\.\d\d\d\d', message)[0]
                        get_currency(sender, date=date)
                    else:
                        message = send_text(sender, date_format)
                        send_message(sender, message)

                # Проверяем если в сообщении есть слова относящиеся
                # к теме «Data Science», то вызываем метод для классификации
                # и отправки пользователю ссылки на википедию,
                # иначе отправляем сообщение, что у нас знаний
                # для ответ на данный запрос
                elif len(set(tf_idf.inverse_transform(X_test)[0]) &
                                             set(tf_idf.vocabulary_.keys()))>0:
                    get_wiki(X_test, sender)

                else:
                    message = send_text(sender, 'Извините у меня нет знаний'+\
                      ' для ответа на этот вопрос')
                    send_message(sender, message)

            else:
              return None


        except Exception as e:
            print(traceback.format_exc())

        return HttpResponse()
