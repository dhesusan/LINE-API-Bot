from django.shortcuts import render
from django.http import (
    HttpResponseForbidden,
    HttpResponse
)
from django.views.decorators.csrf import csrf_exempt

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    LocationMessage,
    MessageEvent,
    TextMessage,
    TextSendMessage,
    TemplateSendMessage,
    CarouselColumn,
    CarouselTemplate,
    URITemplateAction
)
import os
import requests
import datetime

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
RAKUTEN_APPLICATION_ID = os.environ["RAKUTEN_APPLICATION_ID"]
VACANT_HOTEL_SEARCH_URL = os.environ["VACANT_HOTEL_SEARCH_URL"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    body = request.body.decode('utf-8')
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        HttpResponseForbidden()
    return HttpResponse('OK', status=200)


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=event.message.text))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    result = search_vacant_hotel(event)

    try:
        if 'error' in result:
            if result['error'] == 'not_found':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='空室があるホテルが存在しませんでした。')
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='現在使用出来ません。')
                )
        else:
            hotels = result['hotels']
            columns = [
                CarouselColumn(
                    thumbnail_image_url=hotel[0]['hotelBasicInfo']['hotelimageUrl'],
                    title=hotel[0]['hotelBasicInfo']['hotelName'][:40],
                    text=hotel[0]['hotelBasicInfo']['hotelSpecial'][:60],
                    actions=[
                        URITemplateAction(
                            label='詳細を見る',
                            uri=hotel[0]['hotelBasicInfo']['hotelInformationUrl']
                        )
                    ]
                )
                for hotel in hotels
            ]
            messages = TemplateSendMessage(
                alt_text='template',
                template=CarouselTemplate(columns=columns),
            )
            line_bot_api.reply_message(
                event.reply_token,
                messages
            )
            
    except Exception as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='時間をおいて再度お試しください。')
        )


def search_vacant_hotel(event):
    checkin_date = datetime.date.today()
    checkout_date = checkin_date + datetime.timedelta(days=1)
    
    item_parameters = {
        'applicationId': RAKUTEN_APPLICATION_ID,
        'format': 'json',
        'formatVersion': 2,
        'latitude': event.message.latitude,
        'longitude': event.message.longitude,
        'datumType': 1,
        'checkinDate': checkin_date,
        'checkoutDate': checkout_date,
        'searchRadius': 1,
        'hits': 3,
        'elements': 'hotelImageUrl,hotelName,hotelSpecial,hotelInformationUrl'
    }
    r = requests.get(VACANT_HOTEL_SEARCH_URL, params=item_parameters)
    return r.json()

