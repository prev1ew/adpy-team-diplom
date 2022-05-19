# Командный проект по курсу «Профессиональная работа с Python»

## VKinder

### Краткое описание
Программа бот, которая была написала для командного проекта. Программа подключается к группе в ВК и от имени группы обрабатывает входящие сообщения. В текущий момент бот настроен таким образом, чтобы искать людей под человека (который обращается).

### Перед использованием
Ввести свои настройки в settings.py

### Более детально об функционале 
- поиск людей под пользователя, который обращается (под поиском имеется ввиду вывод информации в формате "Имя" "Фамилия" "Ссылка" "3 фотки с максимальным кол-вом лайков")
- возможность добавить людей в избранное (сохраняет людей в базу данных)
- возможность посмотреть список людей (которые добавлены в избранное)

Бот работает через библиотеку vk_api

Более детально о том как настроить группу в ВК и получить токен показано в '[group_settings.md](https://github.com/prev1ew/adpy-team-diplom/blob/main/group_settings.md)'

### Первоначальные требования по задаче (требования для получения "зачета" на обучающей платформе)
Необходимо разработать программу-бота, которая должна выполнять следующие действия:
- Используя информацию (возраст, пол, город) о пользователе, который общается с пользователем в ВК, сделать поиск других людей (других пользователей ВК) для знакомств.
- У тех людей, которые подошли под критерии поиска, получить три самые популярные фотографии в профиле. Популярность определяется по количеству лайков.
- Выводить в чат с ботом информацию о пользователе в формате:
```
Имя Фамилия
ссылка на профиль
три фотографии в виде attachment(https://dev.vk.com/method/messages.send)
```
- Должна быть возможность перейти к следующему человеку с помощью команды или кнопки.
- Сохранить пользователя в список избранных.
- Вывести список избранных людей.
