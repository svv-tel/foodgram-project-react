# Foodgram - Продуктовый помощник  
  
## краткое описание:  
Сервис **Foodgram** - сайт, на котором пользователи публикуют рецепты, могут добавлять чужие рецепты в избранное и подписываться на публикации других авторов.  
  
## технологии в проекте :
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
  
## инструкции по запуску:
После успешного workflow, запустить следующие команды:

`sudo docker-compose exec backend python manage.py makemigrations` и
создаем миграции.

`sudo docker-compose exec backend python manage.py migrate` и
запускаем миграции.

`sudo docker-compose exec backend python manage.py createsuperuser` и
создаем суперпользователя. 

Копируем статику `sudo docker-compose exec backend python manage.py collectstatic --no-input`.


Копируем из csv файла ингредиенты `sudo docker-compose exec backend python manage.py load_ingredients`.
  

## автор:  
Самошкин Владимир