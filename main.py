from db import *
from api_vk import *
import vk_api
from vk_api.longpoll import VkLongPoll

id_vk = int(input('введите id пользователя: '))
token_vk = input('введите токен пользователя: ')
token_group = input('введите токен сообщества: ')

vk = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk)
    

tuple_ = get_users(vk, longpoll, id_vk, token_vk)
city_ = tuple_[0]
sex_ = tuple_[1]
relation_ = tuple_[2]
year_ = tuple_[3]


id_list = search_users(city_, sex_, relation_, year_, id_vk, token_vk)
write_msg(vk, id_vk, 'для выдачи след результата введите 1, для завершения 2')

for id in id_list:
  href = f'vk.com/id{id}'
  photo_3 = get_foto(id, token_vk)[0:3]  
  write_msg(vk, id_vk, href)
  db_insert(id, id_vk)
  for photo_2 in photo_3:
    photo = photo_2['sizes'][-1]['url']    
    write_msg(vk, id_vk, photo)
  write_msg(vk, id_vk, 'для выдачи след результата введите 1, для завершения 2')
  answer = get_message(longpoll)
  if answer == '1':
    pass
  else:
    break
print('отправка фото завершена')
