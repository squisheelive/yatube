# Yatube Социальная сеть
##### В Yatube пользователи могут создавать и комментировать публикации, а также подписываться на других авторов.

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/squisheelive/yatube.git
```
```
cd api_final_yatube
```
Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python manage.py migrate
```
Собрать статику:
```
python manage.py collectstatic
```

Запустить проект:

```
python manage.py runserver
```

