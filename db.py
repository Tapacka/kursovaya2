from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://vkinder:12345@localhost/vkinder")        #бд vkinder с двумя столбцами: result_ids(найденных пользователей, pkey) и id_vk(пользователя)
connection = engine.connect()

def db_check():
  db_id = []
  select_db = connection.execute('SELECT result_ids FROM vkinder').fetchall()
  for ids in select_db:                                                        
    db_id.append(ids[0])
  return db_id                                                       

def db_insert(id, id_vk):
  connection.execute(f"INSERT INTO vkinder VALUES({id}, {id_vk})")
