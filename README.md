# Redcollar python

Проект на Django REST Framework с использованием GeoDjango для работы с географическими точками и сообщениями пользователей.


## Описание

Проект позволяет:
- создавать географические точки с координатами
- добавлять собщения к точкам
- искать точки и сообщения в радиусе от заданной точки


## Технологии

Проект разработан с использованием:
- python 3.12.3
- django 6.0.1
- djangorestframework 3.16.1
- postgresql
- pytest
- postgis
- djangorestframework-simplejwt


## установка системных зависимостей на примере ubuntu
```
sudo apt update

# Основные библиотеки для GeoDjango (GDAL, GEOS, PROJ)
sudo apt install libgdal-dev
sudo apt install libgeos-dev
sudo apt install libproj-dev
sudo apt install gdal-bin
sudo apt install binutils

# база данных
sudo apt install -y postgresql postgresql-contrib postgis postgresql-16-postgis-3
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql -c "SELECT version();"
#должен показать версию

# Проверка, что PostGIS установлен
sudo -u postgres psql -d geodb -c "\dx"

# Проверяем, что GDAL установлен
gdalinfo --version
# Должен показать что-то вроде GDAL 3.8.x или новее
```


## Установка и запуск проекта

1. клонируем репозиторий
```bash
git clone https://github.com/dexter-67/redcollar_python.git
cd redcollar_python
```

2. создаём виртаульное окружение и активируем его

```bash
python -m venv venv
#для Linux или MacOS
source venv/bin/activate
#для Windows
venv\Scripts\activate
```

3. устанавливаем зависимости

```bash
pip install -r requiremets.txt
```

4. переменная окружения ,env и база данных
установка posgresql на linux (ubuntu/debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl status postgresql # проверка статуса posgresql
sudo -i -u postgres psql #вход в базу данных
```

для windows используется графический установщик
https://www.postgresql.org/download/windows/
запустить нужно от имени администратора

https://docs.rkeeper.ru/rk7/7.7.0/ru/ustanovka-postgresql-na-windows-29421153.html - если проверка на windows, то вот инструкция при необходимости

в консоли posgresql
```
CREATE DATABASE db;
CREATE USER user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE db TO user;
ALTER USER user WITH SUPERUSER;
```
Без прав суперпользователя PostgreSQL запрещает эти операции, и миграции завершаются ошибкой, поэтому нужны правва суперпользователя

пример .env
```
POSTGRES_DB=db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=любой_уникальный_секретный_ключ
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. применяем миграции и создаём суперпользователя
```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```
админка доступна на странице http://localhost:8000/admin
если используете не локальную машину, то ссылка следующая http://ip_adress:8000/ и так далее

6. запуск сервера
```bash
python3 manage.py runserver
```


## curl запросы
я прописал токены и id, это только пример. при запуске нужно писать свои данные
1. получение acces и refresh токена
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
        "username": "<логин_от_superuser>",
        "password": "<пароль_от_super_user>"
      }'
```
ожидаемый вывод примерно такой
```
{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2OTEwNjM1OSwiaWF0IjoxNzY4NTAxNTU5LCJqdGkiOiI3NjhkOGY4ZGUwYTU0OWY5YWM4MjE4NTZkNTI4ZGQ1OCIsInVzZXJfaWQiOiIxIn0.G_lDxJDN-FlLojpGiBSZ4ClJp5xhpj_RsKHPtrzLm7g","access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NTA1MTU5LCJpYXQiOjE3Njg1MDE1NTksImp0aSI6Ijc4MjYxZDY2M2U4MTQzZjViYWUwZWNjNzhhYjIxNDQwIiwidXNlcl9pZCI6IjEifQ.CkkwstZS6ZMZG-f1QAKGcvO-mecNLBs1AAXzYFvPaAg"}
```

2. обновление acces токена
```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
        "refresh": "refresh_token"
      }'
```

ожидаемый вывод
```
{"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY4NTA1MjQ1LCJpYXQiOjE3Njg1MDE2NDUsImp0aSI6ImZkZjBlZGE0NDY0ODQ2NWM4NmQ2ZGQzMTI2MTVmMzJkIiwidXNlcl9pZCI6IjEifQ.L5TLh-UJ_UC6b6AQFtQOiOsfASnJrfo0bCNk6kSivcs","refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2OTEwNjQ0NSwiaWF0IjoxNzY4NTAxNjQ1LCJqdGkiOiI5YmZiMzU1MTExNzU0MDY3OTAzNTJlNWVhNTQyNzUyMyIsInVzZXJfaWQiOiIxIn0.8-I4TqAyyv-OT1ZUWWNjWE0CDW8g45xi9neBEnWIsJY"}
```

3. создание точки на карте
```bash
curl -X POST http://127.0.0.1:8000/api/points/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <acces_token>" \
  -d '{                    
        "name": "Город Уфа",
        "latitude": 54.44,
        "longitude": 55.58
      }'
```

ожидаемый вывод
```
{"id":30,"name":"Город Уфа","created_at":"2026-01-15T21:33:23.465056+03:00","updated_at":"2026-01-15T21:33:23.465067+03:00","distance_km":null,"latitude":54.44,"longitude":55.58}
```

4. просмотр всех своих точек
```bash
curl -X GET http://127.0.0.1:8000/api/points/ \
  -H "Authorization: Bearer <acces_token>"
```

ожидаемый вывод
```
{"count":2,"next":null,"previous":null,"results":[{"id":30,"name":"Город Уфа","created_at":"2026-01-15T21:33:23.465056+03:00","updated_at":"2026-01-15T21:33:23.465067+03:00","distance_km":null,"latitude":54.44,"longitude":55.58},{"id":29,"name":"Новая Эйфелева башня","created_at":"2026-01-15T19:58:19.311081+03:00","updated_at":"2026-01-15T20:02:11.545608+03:00","distance_km":null,"latitude":48.8584,"longitude":2.2945}]}
```

5. получение одной точки
```bash
curl -X GET http://127.0.0.1:8000/api/points/'id'/ \
  -H "Authorization: Bearer <acces_token>"
```

ожидаемый вывод
```
{"id":29,"name":"Новая Эйфелева башня","created_at":"2026-01-15T19:58:19.311081+03:00","updated_at":"2026-01-15T20:02:11.545608+03:00","distance_km":null,"latitude":48.8584,"longitude":2.2945}
```

6. обновление точки
```bash
curl -X PATCH http://127.0.0.1:8000/api/points/'id'/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <acces_token>" \
  -d '{
        "name": "Новая Эйфелева башня"
      }'
```

ожидаемый вывод
```
{"id":29,"name":"Новая Эйфелева башня","created_at":"2026-01-15T19:58:19.311081+03:00","updated_at":"2026-01-15T21:40:48.511264+03:00","distance_km":null,"latitude":48.8584,"longitude":2.2945}
```


7. удаление точки
```bash
curl -X DELETE http://127.0.0.1:8000/api/points/id/ \
  -H "Authorization: Bearer <acces_token>"
```

ожидается статус код 204


8. поиск точек по радиусу
если не указать радиус по умолчанию радиус будет равен 10 км
```bash
curl -X GET "http://127.0.0.1:8000/api/points/search/?latitude=54.44&longitude=55.58&radius=5" \
  -H "Authorization: Bearer <acces_token>"
```

ожидаемый вывод
```
{"count":1,"next":null,"previous":null,"results":[{"id":30,"name":"Город Уфа","created_at":"2026-01-15T21:33:23.465056+03:00","updated_at":"2026-01-15T21:33:23.465067+03:00","distance_km":0.0,"latitude":54.44,"longitude":55.58}]}
```


9. пример с несколькими точками
```bash
curl -X GET "http://127.0.0.1:8000/api/points/search/?latitude=48.8584&longitude=2.2945&radius=500" \
  -H "Authorization: Bearer <acces_token>"
```

ожидаемый вывод
```
{"count":1,"next":null,"previous":null,"results":[{"id":30,"name":"Город Уфа","created_at":"2026-01-15T21:33:23.465056+03:00","updated_at":"2026-01-15T21:33:23.465067+03:00","distance_km":146.12,"latitude":54.44,"longitude":55.58}]}
```

10. создание сообщения для точки
```bash
curl -X POST http://127.0.0.1:8000/api/points/messages/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <acces_token>" \
  -d '{
        "point_id": 30,
        "text": "это столица республики Башкортостан"
      }'
```

ожидаемый вывод
```
{"id":5,"point":{"id":30,"name":"Город Уфа","latitude":54.44,"longitude":55.58},"text":"это сталица республики Башкортостан","created_at":"2026-01-15T22:46:09.409835+03:00","updated_at":"2026-01-15T22:46:09.409848+03:00","point_distance_km":null}
```

если указан несуществующий id точки, то вернётся ошибка 400 bad request
сообщения можно создавать и к своим и к чужим точкам


11. поиск сообщений по радиусу
```bash
curl -X GET "http://127.0.0.1:8000/api/messages/search/?latitude=54.44&longitude=55.58&radius=5" \
  -H "Authorization: Bearer <acces_token>"
```

ожидаемый вывод
```
{"count":1,"next":null,"previous":null,"results":[{"id":5,"point":{"id":30,"name":"Город Уфа","latitude":54.44,"longitude":55.58},"text":"это сталица республики Башкортостан","created_at":"2026-01-15T22:46:09.409835+03:00","updated_at":"2026-01-15T22:46:09.409848+03:00","point_distance_km":0.0}]}
```

поле point_distance_km показывает расстояние от центра поиска до точки
если указаны не все параметры, некорректные данные или отрицательный радиус, то вернётся ошибка 400 bad request


12. удаление сообщения
```bash
curl -X DELETE "http://127.0.0.1:8000/api/messages/'id'/" \
  -H "Authorization: Bearer <acces_token>"

```

ожидается статус код 204
при попытке удалить несуществующее сообщение - 404
при попытке удалить чужое сообщение - 403 (удалять можно только свои сообщения!)

13. get запрос без авторизации
```bash
curl -X GET http://127.0.0.1:8000/api/points/
```

ожидаемый вывод
```
{"detail":"Учетные данные не были предоставлены."}
```

14. post запрос без авторизации
```bash
curl -X POST http://127.0.0.1:8000/api/points/ \
  -H "Content-Type: application/json" \
  -d '{
    "x": 10,
    "y": 20
  }'

```

ожидаемый вывод
```
{"detail":"Учетные данные не были предоставлены."}
```


## тесты
чтобы зайти внутрь работающего контейнера нужно выполнить команду (одну из них)
```bash
docker exec -it redcollar_pyton-web-1 bash
docker-compose exec web bash
```
```bash
pytest
```
