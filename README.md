Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

```
sudo docker compose exec backend python3 manage.py migrate && \
sudo docker compose exec backend python3 manage.py load_ingredients && \
sudo docker compose exec backend python3 manage.py collectstatic && \
sudo docker compose exec backend cp -r static/. /collected_static/static/
```