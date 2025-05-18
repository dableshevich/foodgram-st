# Foodgram
Автор проекта: Даблешевич Даниил
## Описание проекта
Задание: Вам предстоит поработать с проектом «Фудграм» — сайтом, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=ffffff"/> <img src="https://img.shields.io/badge/REACT-61DAFB?style=for-the-badge&logo=REACT&logoColor=000000"/> <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=ffffff"/> <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=PostgreSQL&logoColor=ffffff"/> <img src="https://img.shields.io/badge/NGINX-009639?style=for-the-badge&logo=Nginx&logoColor=ffffff"/> <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=ffffff"/> <img src="https://img.shields.io/badge/Git Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=ffffff"/>

## Запуск проекта локально (только Backend)

Склонируйте репозиторий себе на компьютер и перейдите в папку backend:
``` bash
git clone https://github.com/dableshevich/foodgram-st.git
cd foodgram-st/backend/
```

Выполните миграции:
``` BASH
python manage.py migrate
```
Создайте администратора:
``` BASH
python manage.py createsuperuser
```

### Загрузите в базу данных собранные зарание данные
В проекте имеются файлы для начального заполнения базы данных, на ваш выбор выполните одну из следующих команд:
1) Загрузить тестовые данные( пользователи, рецепты и ингредиенты):
``` BASH
python manage.py loaddata collected_data.json
```
2) Загрузить только список ингредиентов:
``` BASH
python manage.py load_ingredients
```
---
Теперь можно запускать проект:
``` BASH
python manage.py runserver
```
## Полный запуск проекта
Для полного запуска сайта вам необходимо установить Docker. Сделать это можно, используя инструкции и официального сайта:
- Для [Windows или MacOS](https://www.docker.com/products/docker-desktop/)
- Для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно нужно установить [Docker Compose](https://docs.docker.com/compose/install/)


Склонируйте репозиторий себе на компьютер и перейдите в корневую папку проекта:
``` bash
git clone https://github.com/dableshevich/foodgram-st.git
cd foodgram-st/
```

В корневой папке вам нужно создать `.env` файл (в директории лежит `.env.example` файл, для примера)
``` python
DB_ENGINE=django.db.backends.postgres # Data Base
POSTGRES_USER=postgres # Username of database owner
POSTGRES_PASSWORD=postgres # Password of database owner
POSTGRES_DB=postgres # Name of database
DB_HOST=postgres # Name of docker postgres container
DB_PORT=5432 # Port of database (default=5432)
DJANGO_SECRET_KEY="..." # Your secret key
```

Перейдите в папку с инфраструктурой и выполните сборку проекта с помощью docker-compose
``` bash
cd infra/
sudo docker compose up --build
```

Откройте в текущей директории ещё один терминал и выполните в нём следующие команды:
1) Выполнение миграций
``` bash
sudo docker compose exec backend python3 manage.py migrate
```
2) Заполнение базы данных (выберите одно из двух)
    - Полный набор тестовых данных:
    ``` BASH
    sudo docker compose exec backend python3 manage.py loaddata collected_data.json              
    ```
    - Только список ингредиентов:
    ``` BASH
    sudo docker compose exec backend python3 manage.py load_ingredients
    ```

3) Соберите статические файлы backend'а и скопируйте их в директорию `/collected_static/statis/`
``` BASH
sudo docker compose exec backend python3 manage.py collectstatic
```
``` BASH
sudo docker compose exec backend cp -r static/. /collected_static/static/
```
---
Всё, проект успешно запущен, чтобы попасть на сайт, нужно перейти по ссылке [http://localhost/](http://localhost/)