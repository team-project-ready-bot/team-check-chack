# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 16:41:22 2019

@author: Onedas
"""

import json
import requests
from flask import Flask, request, Response
import pickle
import pandas as pd
import os
import random
#%%global variables
API_KEY = '802793995:AAFRHgKU_nBygmJj7occh5SXsBZu9sBFpNE'
#API_KEY = '717912330:AAGxY2_sPeb-VziZpNEYkbmiEBq7BrUSU1k' # for test

#%% URL
SEND_MESSAGE_URL = 'https://api.telegram.org/bot{token}/sendMessage'.format(token=API_KEY)
SEND_IMAGE_URL = 'https://api.telegram.org/bot{token}/sendPhoto'.format(token=API_KEY)
EDIT_MESSAGE_URL = 'https://api.telegram.org/bot{token}/editMessageText'.format(token=API_KEY)
SEND_CONTACT_URL = 'https://api.telegram.org/bot{token}/sendContact'.format(token=API_KEY)

# %% data load # intent_finder
intent_finder = pickle.load(open('intent_finder.pickle','rb'))
hello_finder = pickle.load(open('hello_finder.pickle','rb'))

DB_file = 'ds120FAQ.xlsx'
df = pd.read_excel(DB_file)
first_say = '''안녕하십니까?'다산이의 그것이 알고싶다'의 다알입니다.\n저 다알은 서울시민 분들의 일상생활의 궁금증을 해결하고자\n노력하고 있습니다.\n궁금한점이 있으신 시민여러분들의 질문을 기다리겠습니다.'''
hello_say = ['안녕하십니까? 질문할 것이 있으십니까?','혹시 질문할 것이 있으신가요?']
answer_say = "조금전 다산이의 '답변을 찾지 못했어요.'라는 답변을 들었습니다.\n참으로 안타까운 답변이 아닐 수 없습니다.\n\n그런데 이 질문은 다산FAQ에 엄연히 존재하였습니다.\n그래서 말입니다 우리는 다산FAQ를 활용해서 {}과 가장 비슷한 FAQ의 질문을 찾아보았습니다."
slice_nums = list(map(len,answer_say.split('{}')))
##
# %% function of backend
def text2hello_question(text):
    return hello_finder.predict(text)[0]

def text2Qnums(text):
    return intent_finder.find_answer(text)

def Qnum2Q(Qnum):
    s=''
    s+='[{}]Q{} : '.format(df.loc[Qnum][0],Qnum)+ df.loc[Qnum][1]
    
    return s        

def Qnum2A(Qnum):
    s=''
    s+='A : '+ df.loc[Qnum][2]
    return s

#print(Qnum2Q(282))
#print(Qnum2A(284))
#print(intent_finder.find_answer('주정차 위반'))
#print(text2Qnums('강남구'))
#print(text2hello_question('하이'))
#print(intent_finder.big_filter.word_dict)
# %% function of telegram
app = Flask(__name__)

def parse_message(data):
    '''응답data 로부터 chat_id 와 text, user_name을 추출.'''
    chat_id = None
    msg = None
    user_name = None
    inline_data = None    
    
    if 'callback_query' in data:
        data=data['callback_query']
        inline_data = data['data']
        msg = data['message']['text'][slice_nums[0]:-slice_nums[1]]
    else:
        msg=data['message']['text']
    
    message_id = data['message']["message_id"]
    chat_id = data['message']['chat']['id']
    
    return chat_id, msg, inline_data, message_id   #https://core.telegram.org/bots/api#keyboardbutton


def send_message(chat_id, text):
    params = {'chat_id':chat_id, 'text': text}
    requests.post(SEND_MESSAGE_URL, json=params)

def send_message_keyboard(chat_id, text):
    keyboard = {'keyboard' : [[{'text': 'A'},{'text': 'B'}],
                              [{'text': 'C'},{'text': 'D'}]],
                'one_time_keyboard':True}
    
    params = {'chat_id':chat_id, 'text' : text, 'reply_markup':keyboard}
    requests.post(SEND_MESSAGE_URL, json=params)

def send_message_inlinekeyboard(chat_id,text,page=0):
    answer_nums = text2Qnums(text)
    text1 = Qnum2Q(answer_nums[0+3*page])
    text2 = Qnum2Q(answer_nums[1+3*page])
    text3 = Qnum2Q(answer_nums[2+3*page])
    InlineKeyboard = {'inline_keyboard' : [[{'text':text1, 'callback_data':answer_nums[0+3*page]}],
                                           [{'text':text2, 'callback_data':answer_nums[1+3*page]}],
                                           [{'text':text3, 'callback_data':answer_nums[2+3*page]}],
                                           [{'text':'<<','callback_data':'{}page'.format((page-1)%3)},{'text':'{} page'.format(page+1),'callback_data':'test'.format(page)},{'text':'>>','callback_data':'{}page'.format((page+1)%3)},{'text':'전화연결','callback_data':'call_dasan'}]]}
                                            
    params = {'chat_id':chat_id, 'text' : answer_say.format(text), 'reply_markup':InlineKeyboard}
    requests.post(SEND_MESSAGE_URL,json=params)

def edit_message_inlinekeyboard(chat_id, text, message_id, page):
    answer_nums = text2Qnums(text)
    text1 = Qnum2Q(answer_nums[0+3*page])
    text2 = Qnum2Q(answer_nums[1+3*page])
    text3 = Qnum2Q(answer_nums[2+3*page])
    InlineKeyboard = {'inline_keyboard' : [[{'text':text1, 'callback_data':answer_nums[0+3*page]}],
                                           [{'text':text2, 'callback_data':answer_nums[1+3*page]}],
                                           [{'text':text3, 'callback_data':answer_nums[2+3*page]}],
                                           [{'text':'<<','callback_data':'{}page'.format((page-1)%3)},{'text':'{} page'.format(page+1),'callback_data':'test'.format(page)},{'text':'>>','callback_data':'{}page'.format((page+1)%3)},{'text':'전화연결','callback_data':'call_dasan'}]]}
                                            
    params = {'chat_id':chat_id,'message_id': message_id ,'text' : answer_say.format(text), 'reply_markup':InlineKeyboard}
    requests.post(EDIT_MESSAGE_URL,json=params)

def send_contact(chat_id,number,name):
    params = {'chat_id':chat_id, 'phone_number':number,'first_name':name }
    requests.post(SEND_CONTACT_URL, json=params)
# %% main
# 경로 설정, URL 설정
@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        message = request.get_json()
        with open('message.txt','w') as f:
            json.dump(message,f,indent=4)
        
        chat_id, msg, inline_data, message_id = parse_message(message)
        print(msg, inline_data)
        if msg=='/start':
            send_message(chat_id,first_say)
            
        elif inline_data == None: # inline 버튼을 안눌렀을 때
            intent =  text2hello_question(msg)
            
            if intent == 'hello':
                send_message(chat_id,random.choice(hello_say))
                
            elif intent == 'Question':
                send_message_inlinekeyboard(chat_id,msg)
        
        else: # inline 버튼을 눌렀을 때
            if inline_data == '0page':
                edit_message_inlinekeyboard(chat_id, msg, message_id, 0)
            elif inline_data =='1page':
                edit_message_inlinekeyboard(chat_id, msg, message_id, 1)
            elif inline_data =='2page': 
                edit_message_inlinekeyboard(chat_id, msg, message_id, 2)
            elif inline_data =='test':
                pass
            elif inline_data =='call_dasan':
                print('hi')
                send_contact(chat_id,'02-120','다산')
            else:     
                send_message(chat_id,Qnum2Q(int(inline_data))+'\n'+Qnum2A(int(inline_data)))
                inline_data =None
                
        return Response('ok', status=200)
        
    else:
        return 'Hello World!'


if __name__ == '__main__':
#    app.run(port=5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
