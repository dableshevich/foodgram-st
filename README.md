# Foodgram project
Клонируйте репозиторий
``` bash
git clone https://github.com/dableshevich/foodgram-st.git
```

Перейдите в директорию с инвраструктурой проекта
``` bash
cd /foodgram-st/infra/
```

Выполните сборку проекта с помощью docker-compose
``` bash
sudo docker compose up --build
```

Откройте в текущей директории ещё один терминал и выполните в нём следующие команды
``` bash
    sudo docker compose exec backend python3 manage.py migrate && \
    sudo docker compose exec backend python3 manage.py loaddata collected_data.json && \                                                                 
    sudo docker compose exec backend python3 manage.py collectstatic && \
    sudo docker compose exec backend cp -r static/. /collected_static/static/
```