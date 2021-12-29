import requests
import sqlalchemy
from sqlalchemy import create_engine
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

id_vk = int(input('введите id пользователя'))
token_vk = input('введите токен пользователя')
token_group = input('введите токен сообщества')

vk = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk)

engine = create_engine("postgresql+psycopg2://vkinder:12345@localhost/vkinder")
connection = engine.connect()



def get_message():
  for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
      if event.to_me:
        request = event.text
        return request

def write_msg(user_id, message):
  vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

def get_city_id(country, city):
  url = 'https://api.vk.com/method/database.getCities'
  params = {'user_ids': id_vk, 'access_token': token_vk, 'v': '5.131', 'country_id': country, 'q': city}
  res = requests.get(url, params=params).json()
  return res['response']['items'][0]['id']
  

def get_users():
  url = 'https://api.vk.com/method/users.get'
  fields = 'city, sex, relation, bdate, country'
  params = {'user_ids': id_vk, 'access_token': token_vk, 'v': '5.131','fields': fields}  
  res = requests.get(url, params=params).json()  
  country = res['response'][0]['country']['id']
  if 'city' not in res['response'][0]:
    write_msg(id_vk, 'введите название города, в котором осуществить поиск')
    cit_y = get_message()
    city = get_city_id(country, cit_y)
  else:  
    city = res['response'][0]['city']['id']
  if 'sex' not in res['response'][0]:
    write_msg(id_vk, 'ваш пол(1-жен, 2-муж)')
    sex = get_message()
  else:  
    sex = res['response'][0]['sex']
  if 'relation' not in res['response'][0]:
    write_msg(id_vk, 'выберите семейное положение для поиска: 1 — не женат/не замужем; 2 — есть друг/есть подруга; 3 — помолвлен/помолвлена; 4 — женат/замужем; 5 — всё сложно; 6 — в активном поиске; 7 — влюблён/влюблена; 8 — в гражданском браке; 0 — не указано')
    relation = get_message()
  else:  
    relation = res['response'][0]['relation']
  if 'bdate' not in res['response'][0]:
    write_msg(id_vk, 'введите ваш год рождения xxxx')
    year = get_message()
  else:  
    bdate = res['response'][0]['bdate']
    year = int(bdate[-4:-1]+bdate[-1])
  return city, sex, relation, year        

tuple_ = get_users()
city_ = tuple_[0]
sex_ = tuple_[1]
relation_ = tuple_[2]
year_ = tuple_[3]


def search_users(city, sex, relation, year):
  url = 'https://api.vk.com/method/users.search'
  params = {'access_token': token_vk, 'v': '5.131', 'count': 20, 'sex': 3-sex, 'city': city, 'status': relation, 'age_from': 2019-year, 'age_to': 2023-year, 'has_photo': 1, 'has_photo': 1}  
  res = requests.get(url, params=params).json()  
  id_list = []
  db_id = []
  #select_db = connection.execute('SELECT result_ids FROM vkinder').fetchall() #проверка бд
  #for ids in select_db:                                                        #проверка бд
  #  db_id.append(ids[0])                                                      #проверка бд
  for person in res['response']['items']:
    if person['is_closed'] == True: 
      pass
    #elif person['id'] in db_id:                                              #проверка бд  
    #  pass
    else: 
      id_ = person['id']
      id_list.append(id_)
      #connection.execute(f"INSERT INTO vkinder VALUES({id_}, {id_vk})")    #запись в бд
  return id_list


def get_foto(id):
  url = 'https://api.vk.com/method/photos.get'
  params = {'user_id': id, 'access_token': token_vk, 'v': '5.131','album_id': 'profile', 'extended': '1', 'photo_sizes': '1'}  
  res = requests.get(url, params=params).json()

  def sorting(photo):
    return photo['comments']['count'], photo['likes']['count']

  sorted_list = sorted(res['response']['items'], reverse=True, key=sorting)
  return sorted_list


id_list = search_users(city_, sex_, relation_, year_)
for id in id_list:
  href = f'vk.com/id{id}'
  photo_3 = get_foto(id)[0:3]
  print('отправка фото')
  write_msg(id_vk, href)
  for photo_2 in photo_3:
    photo = photo_2['sizes'][-1]['url']    
    write_msg(id_vk, photo)
print('отправка фото завершена')
