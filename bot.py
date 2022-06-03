from telegram.ext import Updater
from telegram import Update
from telegram import InputMediaPhoto, InputMediaVideo
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler,MessageHandler,Filters
from db.db import Database
from instagram.inst import Inst
from bs4 import BeautifulSoup
import os.path as pt
import requests

db = Database()
ig = Inst()
token = db.getCreds(cred='token')
updater = Updater(token= token, use_context=True)
dispatcher = updater.dispatcher

def getHBphotos(url:str) -> dict:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    html = requests.get(url, headers=headers)
    html.encoding = 'utf-8'
    items = []

    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'lxml')
        slider = soup.find_all('div', class_='carousel-cell-image-wrapper annotation-container fixed-ratio-3-2')
        for slide in slider:
            photo = slide.find('source')['data-srcset']
            media = {
                'type' : 'photo',
                'link' : photo
            }
            items.append(media)
        result = {
                'ok' : 'true',
                'items' : items
            }
    else:
        result = {
            'ok' : 'false',
            'text' : html.status_code
        }      

    return result  

def msgHndlr(update: Update, context: CallbackContext) :
    url = update.message.text
    messId = update.message.message_id
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=messId)
    if 'https://www.instagram.com/p/' in url:
        media = ig.getMedia(url)
        items = []
        for item in media['items'] :
            if item['type'] == 'photo' :
                med = InputMediaPhoto(media=item['link'])
            elif item['type'] == 'video' :
                med = InputMediaVideo(media=item['link'])
            items.append(med)
        context.bot.send_media_group(chat_id=update.effective_chat.id,media = items)
        if media['text'] != '' :
            context.bot.send_message(chat_id=update.effective_chat.id, text=media['text'])
    elif 'https://hypebeast.com/' in url :
        media = getHBphotos(url)
        items = []
        for item in media['items'] :
            if item['type'] == 'photo' :
                med = InputMediaPhoto(media=item['link'])
            elif item['type'] == 'video' :
                med = InputMediaVideo(media=item['link'])
            items.append(med)
        context.bot.send_media_group(chat_id=update.effective_chat.id,media = items)
    else:
        userInfo = ig.getUserInfo(url)
        db.createNewProfile(userInfo)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Аккаунт добавлен')

def start(update: Update, context: CallbackContext) :
    context.bot.send_message(chat_id=update.effective_chat.id, text='Чтобы получить контент из поста Инстаграм, просто пришли мне ссылку на пост')

if __name__ == '__main__' :
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    post_handler = MessageHandler(Filters.text & (~Filters.command), msgHndlr)
    dispatcher.add_handler(post_handler)

    updater.start_polling()