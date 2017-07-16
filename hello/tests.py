from django.test import TestCase
from hello.models import Question, Answer
import unittest
import json
from urllib.request import urlopen
import hello.views

# Create your tests here.


class DbTestCase(TestCase):
    def setUp(self):
        Answer.objects.create(sender=675805359, data={
            "recipient": {
                "id": 675805359
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

        Answer.objects.create(sender=675805359, data={
            "recipient": {
                "id": 675805359
            },
            "message": {
                "text": "Please share your location:",
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

        Question.objects.create(sender=675805359, data={
            "recipient": {
                "id": 675805359
            },
            "message": {
                "text": "Please share your location:",
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


class PayloadTest(unittest.TestCase):

    def test_location_quick_reply(self):
        self.assertEquals(json.dumps({
        "recipient": {
            "id": 1611923252172409
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
    }),
    hello.views.location_quick_reply(1611923252172409))

    def test_currency_quick_reply(self):
        self.assertEquals(json.dumps({
        "recipient": {
            "id": 1611923252172409
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
    }),
    hello.views.currency_quick_reply(1611923252172409))

    def test_currency_quick_reply(self):
        self.assertEquals(json.dumps({
        "recipient": {
            "id": 1611923252172409
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
    }),
    hello.views.currency_quick_reply(1611923252172409))


def check_txt(txt):
    return {
        "object": "page",
        "entry": [
            {
                "messaging": [
                    {
                        "sender": {
                            "id": "1611923252172409"
                        },
                        "message": {
                            "text": txt
                        }
                    }
                ]
            }
        ]
    }


class SimpleTest(unittest.TestCase):
    def test_msg(self):
        for msg in ('погода', 'меню', 'погода Пермь', 'курс 15.05.2017', 'how draw pie chart', 'how make banana bread'):
            response = urlopen("https://gorgeous-cuyahoga-valley-38558.herokuapp.com/fb_bot/", json.dumps(check_txt(msg)).encode())
            self.assertEqual(response.status, 200)
            print(msg, response.getcode())

if __name__ == '__main__':
  unittest.main()
