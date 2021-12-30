import requests
from vk_api.longpoll import VkEventType
from random import randrange
from db import *


def get_message(longpoll):
  for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
      if event.to_me:
        request = event.text
        return request

def write_msg(vk, user_id, message):
  vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

def get_city_id(country, city, id_vk, token_vk):
  url = 'https://api.vk.com/method/database.getCities'
  params = {'user_ids': id_vk, 'access_token': token_vk, 'v': '5.131', 'country_id': country, 'q': city}
  res = requests.get(url, params=params).json()
  return res['response']['items'][0]['id']
  

def get_users(vk, longpoll, id_vk, token_vk):
  url = 'https://api.vk.com/method/users.get'
  fields = 'city, sex, relation, bdate, country'
  params = {'user_ids': id_vk, 'access_token': token_vk, 'v': '5.131','fields': fields}  
  res = requests.get(url, params=params).json()  
  country = res['response'][0]['country']['id']
  if 'city' not in res['response'][0]:
    write_msg(vk, id_vk, 'введите название города, в котором осуществить поиск')
    cit_y = get_message(longpoll)
    city = get_city_id(country, cit_y, id_vk, token_vk)
  else:  
    city = res['response'][0]['city']['id']
  if 'sex' not in res['response'][0]:
    write_msg(vk, id_vk, 'ваш пол(1-жен, 2-муж)')
    sex = get_message(longpoll)
  else:  
    sex = res['response'][0]['sex']
  if 'relation' not in res['response'][0]:
    write_msg(vk, id_vk, 'выберите семейное положение для поиска: 1 — не женат/не замужем; 2 — есть друг/есть подруга; 3 — помолвлен/помолвлена; 4 — женат/замужем; 5 — всё сложно; 6 — в активном поиске; 7 — влюблён/влюблена; 8 — в гражданском браке; 0 — не указано')
    relation = get_message(longpoll)
  else:  
    relation = res['response'][0]['relation']
  if 'bdate' not in res['response'][0]:
    write_msg(vk, id_vk, 'введите ваш год рождения xxxx')
    year = get_message(longpoll)
  else:  
    bdate = res['response'][0]['bdate']
    year = int(bdate[-4:-1]+bdate[-1])
  return city, sex, relation, year

def search_users(city, sex, relation, year, id_vk, token_vk):
  url = 'https://api.vk.com/method/users.search'
  params = {'access_token': token_vk, 'v': '5.131', 'count': 20, 'sex': 3-sex, 'city': city, 'status': relation, 'age_from': 2019-year, 'age_to': 2023-year, 'has_photo': 1, 'has_photo': 1}  
  res = requests.get(url, params=params).json()  
  id_list = []  
  for person in res['response']['items']:
    if person['is_closed'] == True: 
      pass
    elif person['id'] in db_check():                                              
      pass
    else:
      id_ = person['id']
      id_list.append(id_)   
  return id_list


def get_foto(id, token_vk):
  url = 'https://api.vk.com/method/photos.get'
  params = {'user_id': id, 'access_token': token_vk, 'v': '5.131','album_id': 'profile', 'extended': '1', 'photo_sizes': '1'}  
  res = requests.get(url, params=params).json()

  def sorting(photo):
    return photo['comments']['count'], photo['likes']['count']

  sorted_list = sorted(res['response']['items'], reverse=True, key=sorting)
  return sorted_list