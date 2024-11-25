# Foodgram

Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект состоит из следующих страниц: 
- главная,
- страница рецепта,
- страница пользователя,
- страница подписок,
- избранное,
- список покупок,
- создание и редактирование рецепта.

#### Главная

Содержимое главной — список первых шести рецептов, отсортированных по дате публикации «от новых к старым». Остальные рецепты доступны на следующих страницах.

#### Страница рецепта

Здесь — полное описание рецепта. У авторизованных пользователей есть возможность добавить рецепт в избранное и список покупок, а также подписаться на автора рецепта.

#### Страница пользователя

На странице — имя пользователя, все рецепты, опубликованные пользователем и возможность подписаться на пользователя.

#### Страница подписок

Только у владельца аккаунта есть возможность просмотреть свою страницу подписок. Подписаться на публикации могут только авторизованные пользователи.

Сценарий поведения пользователя:

1. Пользователь переходит на страницу другого пользователя или на страницу рецепта и подписывается на публикации автора кликом по кнопке «Подписаться на автора».
2. Пользователь переходит на страницу «Мои подписки» и просматривает список рецептов, опубликованных теми авторами, на которых он подписался. Записи сортируются по дате публикации — от новых к старым.
3. При необходимости пользователь может отказаться от подписки на автора. Тогда ему нужно перейти на страницу автора или на страницу его рецепта и нажать кнопку «Отписаться от автора».

#### Избранное

Добавлять рецепты в избранное может только авторизованный пользователь. Сам список избранного может просмотреть только его владелец.

Сценарий поведения пользователя:

1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в избранное».
2. Пользователь переходит на страницу «Список избранного» и просматривает свой список избранных рецептов.
3. При необходимости пользователь может удалить рецепт из избранного.

#### Список покупок

Работа со списком покупок доступна только авторизованным пользователям. Доступ к своему списку покупок есть только у владельца аккаунта.

Сценарий поведения пользователя:

1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в покупки».
2. Пользователь переходит на страницу «Список покупок», там доступны все добавленные в список рецепты. Пользователь нажимает кнопку «Скачать список» и получает файл с перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок».
3. При необходимости пользователь может удалить рецепт из списка покупок.

#### Создание и редактирование рецепта

Доступ к этой странице есть только у авторизованных пользователей. Все поля на ней обязательны для заполнения.

Сценарий поведения пользователя:

1. Пользователь заполняет все обязательные поля.
2. Пользователь нажимает кнопку «Создать рецепт».

Также пользователю доступна возможность отредактировать любой рецепт, который он создал.

#### Фильтрация по тегам

Тег (от англ. tag, «метка», «бирка», «ярлык») — метка, которая классифицирует данные и помогает облегчить процесс поиска нужной информации в веб-приложении.
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация проводится по нескольким тегам в комбинации «или»: если выбрано несколько тегов — в результате будут показаны рецепты, которые отмечены хотя бы одним из этих тегов.
При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. Такой же принцип соблюдается при фильтрации списка избранного.

#### Система регистрации и авторизации

В проекте доступна система регистрации и авторизации пользователей.

Обязательные поля для пользователя:
- логин,
- пароль,
- email,
- имя,
- фамилия.

Уровни доступа пользователей:
- гость (неавторизованный пользователь),
- авторизованный пользователь,
- администратор.

## Стэк технологий
- Python 3.7
- Django 2.2.16
- Django Rest Framework 3.12.4
- Docker
- PostgreSQL


## Запуск проекта на Linux
### Установка Docker
Выполните команды:
```sh
sudo apt update
sudo apt install curl
url -fSL https://get.docker.com -o get-docker.sh 
sudo sh ./get-docker.sh
```
Для сборки так же требуется утилита Docker Compose:
```sh
sudo apt install docker-compose-plugin 
```
Официальная документация по установке: https://docs.docker.com/engine/install/ubuntu/

### Сборка проекта
- Клонируйте репозиторий и настройте параметры окружения
- Соберите образы и отправьте их в Docker Hub
- Скопируйте файл docker-compose.production.yml в корневую папку проекта
- Запустите оркестр с помощью docker compose

### Полезные команды Docker
Аутентификация в Docker Hub:
```sh
docker login -u username 
```
Сборка образа:
```sh
docker build -t image_name . 
```
Отправка образов в Docker Hub:
```sh
docker push username/image_name:latest
```
Запуск всех описанных в docker-compose.yml контейнеров:
```sh
docker compose up
```
Запуск всех описанных в docker-compose.yml контейнеров в фоновом режиме:
```sh
docker compose up -d
```
Остановка всех контейнеров:
```sh
docker compose stop
```
Остановка и удаление всех контейнеров:
```sh
docker compose down
```
Остановка и удаление всех контейнеров и volume:
```sh
docker compose down -v
```
Если файл называется не docker-compose.yml, то в каждой команде после compose нужно
указывать параметр -f имя_файла.

## Над проектом работал:
- [Дмитрий Латыпов](https://github.com/deviator2004)

