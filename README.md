# Foodgram - Продуктовый помощник  
  
## Краткое описание:  
Сервис **Foodgram** - сайт, на котором пользователи публикуют рецепты, могут добавлять чужие рецепты в избранное и подписываться на публикации других авторов.

Пример сайта доступен по адресу http://51.250.17.249
  
## Используемые технологии в проекте :
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
  
## Инструкции по запуску:
### на локальной машине
Клонировать репозиторий и перейти в него:
```
git clone git@github.com:svv-tel/foodgram-project-react.git
```
Создайте и активируйте виртуальное окружение:
```
python3 -m venv venv
```
```commandline
source venv/bin/activate 
```
Обновите пакетный менеджер:
```commandline
python -m pip install --upgrade pip
```
Установите зависимости из файла requirements.txt:
```commandline
pip install -r requirements.txt
```
В директории backend создайте файл .env и заполните его данными по этому образцу: 
```commandline
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Выполните миграции:
```commandline
python manage.py migrate
```
Запустите проект:
```commandline
python manage.py runserver
```
### на боевом сервере
Форкнуть репозиторий:
```commandline
git clone git@github.com:svv-tel/foodgram-project-react.git
```
Зайти в Git-Settings-Secrets-Action и заполнить следующие параметры:
```commandline
DB_ENGINE - тип Базы Данных
DB_HOST - контейнер БД
DB_NAME - имя БД
DB_PORT - порт БД
DOCKER_PASSWORD - пароль к докерхаб
DOCKER_USERNAME - логин к докерхаб
HOST - адрес боевого сервера
PASSPHRASE - пароль боевого сервера, если есть
POSTGRES_PASSWORD - пароль пользователя в БД
POSTGRES_USER - пользователь в БД
SSH_KEY - приватный ключ локальной машины
SSH_USER - логин к боевому серверу
```
Для запуска проекта, выполните команду для обновления в репозитории GitHub:
```commandline
git push
```
Зайти на удаленный сервер по команде:
```commandline
ssh ваш-логин@ваш-ip
```
Обновить пакеты на сервере:
```commandline
sudo apt update
```
Установите docker.io командой:
```commandline
sudo apt install docker.io
```
Установите docker-compose командой:
```commandline
sudo apt install docker-compose
```
После успешного запуска workflow на GitHub, запустите следующие команды:

создание миграции
`sudo docker-compose exec backend python manage.py makemigrations`

запуск миграции
`sudo docker-compose exec backend python manage.py migrate`

создаем суперпользователя
`sudo docker-compose exec backend python manage.py createsuperuser`

Копируем статику `sudo docker-compose exec backend python manage.py collectstatic --no-input`

Копируем из csv файла ингредиенты `sudo docker-compose exec backend python manage.py load_ingredients`.
  
Переходим к проекту по адресу указанному в параметре HOST и регистрируем пользователя, создаем рецепты.

## автор:  
Самошкин Владимир
