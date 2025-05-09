import telebot
from telebot import types
import sqlite3
import random
from datetime import datetime, timedelta

bot = telebot.TeleBot('?')

row = []


@bot.message_handler(commands=['start'])
def Start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("❓ Информация об уроках", )
    markup.row(btn1)
    btn2 = types.KeyboardButton("📌 Цены за урок")
    btn3 = types.KeyboardButton("✏ Запись на урок")
    markup.row(btn2, btn3)
    btn5 = types.KeyboardButton("❌ Отменить запись на урок")
    btn6 = types.KeyboardButton("👤 Для Админа")
    markup.row(btn5, btn6)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!' + '\n' + "Рад тебя видеть",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "👤 Для Админа")
def admin_access(message):
    if message.from_user.username in ['Max1_6', 'nikit_000']:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("Вывод всех записей", callback_data="Show"))
        markup.add(types.InlineKeyboardButton("Обновление бд", callback_data="Update"))
        markup.add(types.InlineKeyboardButton("Уроки на сегодня", callback_data="Today"))
        markup.add(types.InlineKeyboardButton("Рандомный Вкид❓", callback_data="Vkid"))
        bot.reply_to(message, "Админ-панель. Выберите опцию:", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "❌Недостаточно прав❌")
        return


@bot.callback_query_handler(func=lambda call: call.data == "Vkid")
def rand_vkid(call):
    a = ["Закинуться!", "Не закидываться😥", "Закинуться через 5 минут"]
    choice = random.choice(a)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"🎉🎊Мои поздравления🎊🎉:\n\n{choice}")


@bot.callback_query_handler(func=lambda call: call.data == "Show")
def show_bd(call):
    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users;')
    row = cursor.fetchall()
    for i in row:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         f"Имя: {i[1]}\nФамилия: {i[2]}\nКласс: {i[3]}\nВозраст: {i[4]}\nЦель: {i[5]}\nЮзернейм:  @{i[6]}\nДата: {i[7]}")


@bot.callback_query_handler(func=lambda call: call.data == "Today")
def teach_today(call):
    bot.send_message(call.message.chat.id, "🔧 Данная функция находится в разработке...")


@bot.callback_query_handler(func=lambda call: call.data == "Update")
def update(call):
    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users;')
    row = cursor.fetchall()
    cursor.execute('DELETE FROM Users;')
    new_row = filter(lambda x: (datetime.now() - datetime.strptime(x[-1], '%Y-%m-%d %H:%M:%S') <= timedelta(days=7)),
                     row)
    for i in new_row:
        cursor.execute('INSERT INTO Users (name, surname, myclass, years, target, name_tg) VALUES (?, ?, ?, ?, ?, ?)',
                       (i[1], i[2], int(i[3]), int(i[4]), i[5], str(i[6])))
    connection.commit()
    connection.close()
    bot.send_message(call.message.chat.id, "База данных успешно обновлена!")


@bot.message_handler(func=lambda message: message.text == "❌ Отменить запись на урок")
def chancle(message):
    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()
    cursor.execute(F"SELECT name_tg  FROM Users")
    rows = iter(["".join(i) for i in cursor.fetchall()])
    if message.from_user.username in rows:
        cursor.execute(f"DELETE FROM Users WHERE name_tg = '{message.from_user.username}'")
        bot.send_message(message.chat.id, "Ваша запись на урок успешно отменена!")
    else:
        bot.send_message(message.chat.id, "Вы еще не записывались на урок!")
    connection.commit()
    connection.close()


@bot.message_handler(func=lambda message: message.text == "✏ Запись на урок")
def write_lesson(message):
    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name      VARCHAR(30),
        surname   VARCHAR(30),
        myclass     INTEGER,
        years     INTEGER,
        target    VARCHAR(300),
        name_tg   VARCHAR(100),
        mydatatime DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DateTime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            lesson_date DATE,
            lesson_time TIME,
            FOREIGN KEY (student_id) REFERENCES Users (id) ON DELETE CASCADE
        )
    ''')

    connection.commit()
    connection.close()

    bot.send_message(message.chat.id, "Введите своё имя")
    bot.register_next_step_handler(message, process_name)


def process_name(message):
    user_name = message.text  # Тут находится имя из прошлой функции
    if user_name == "❓ Информация об уроках":
        info_teach(message)
        return
    elif user_name == "📌 Цены за урок":
        price(message)
        return
    elif user_name == "✏ Запись на урок":
        write_lesson(message)
        return
    elif user_name == "❌ Отменить запись на урок":
        chancle(message)
        return
    elif user_name == "👤 Для Админа":
        pass
    row.append(user_name)
    bot.send_message(message.chat.id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, process_surname, user_name)


def process_surname(message, user_name):
    user_surname = message.text
    if user_surname == "❓ Информация об уроках":
        info_teach(message)
        return
    elif user_surname == "📌 Цены за урок":
        price(message)
        return
    elif user_surname == "✏ Запись на урок":
        write_lesson(message)
        return
    elif user_surname == "❌ Отменить запись на урок":
        chancle(message)
        return
    elif user_surname == "👤 Для Админа":
        pass
    row.append(user_surname)
    bot.send_message(message.chat.id, "В каком вы классе?")
    bot.register_next_step_handler(message, teach_class, user_name, user_surname)


def teach_class(message, user_name, user_surname):
    user_class = message.text
    if user_class == "❓ Информация об уроках":
        info_teach(message)
        return
    elif user_class == "📌 Цены за урок":
        price(message)
        return
    elif user_class == "✏ Запись на урок":
        write_lesson(message)
        return
    elif user_class == "❌ Отменить запись на урок":
        chancle(message)
        return
    elif user_class == "👤 Для Админа":
        pass
    row.append(user_class)
    bot.send_message(message.chat.id, "Сколько тебе лет?")
    bot.register_next_step_handler(message, how_old, teach_class, user_name, user_surname)


def how_old(message, user_name, user_surname, user_class):
    old = message.text
    if old == "❓ Информация об уроках":
        info_teach(message)
        return
    elif old == "📌 Цены за урок":
        price(message)
        return
    elif old == "✏ Запись на урок":
        write_lesson(message)
        return
    elif old == "❌ Отменить запись на урок":
        chancle(message)
        return
    elif old == "👤 Для Админа":
        pass
    row.append(old)
    bot.send_message(message.chat.id, "Распиши то, какие номера или темы ты хотел(а) бы разобрать на уроке:")
    bot.register_next_step_handler(message, targets, how_old, teach_class, user_name, user_surname)


def targets(message, user_name, user_surname, user_class, old):
    targ = message.text
    if targ == "❓ Информация об уроках":
        info_teach(message)
        return
    elif targ == "📌 Цены за урок":
        price(message)
        return
    elif targ == "✏ Запись на урок":
        write_lesson(message)
        return
    elif targ == "❌ Отменить запись на урок":
        chancle(message)
        return
    elif targ == "👤 Для Админа":
        pass
    connection = sqlite3.connect('Students.db')
    cursor = connection.cursor()
    row.append(targ)
    a, b, c, d, e = row
    cursor.execute('INSERT INTO Users (name, surname, myclass, years, target, name_tg) VALUES (?, ?, ?, ?, ?, ?)',
                   (a, b, int(c), int(d), e, str(message.from_user.username)))
    connection.commit()
    connection.close()
    row.clear()
    bot.send_message(message.chat.id, "Вы успешно записались на урок!" + '\n' + "Позже преподаватель свяжется с вами")


@bot.message_handler(func=lambda message: message.text == "📌 Цены за урок")
def price(message):
    bot.send_message(message.chat.id, "Стоимость:\n" \
                                      "▪️ЕГЭ (профильная математика)\n" \
                                      "   1500р - 1 час (60 мин)\n" \
                                      "   2000р - 1,5 часа (90 мин)\n" \
                                      "▪️ОГЭ/ЕГЭ (базовая математика)\n" \
                                      "   1200р - 1 час\n" \
                                      "   1600р - 1,5 часа\n\n" \
                                      "Оплата производится на карту по номеру телефона\n" \
                                      "Способы оплаты:\n" \
                                      "1) после каждого урока\n" \
                                      "2) на неделю вперед\n" \
                                      "3) на месяц вперед")


@bot.message_handler(func=lambda message: message.text == "❓ Информация об уроках")
def info_teach(message):
    bot.send_message(message.chat.id, "Про уроки:\n" \
                                      "▪️Discord (для звонков)\n" \
                                      "▪️Онлайн доска  miro  (для того чтобы решать задачи, рисовать)\n" \
                                      "▪️Телеграм (для обсуждения различных вопросов таких как решение задач, возможные переносы уроков и т.д.)\n\n" \
                                      "Начало урока:\n" \
                                      "В назначенное время созваниваемся по дискорду, я кидаю ссылку на доску в чат, либо можно пользоваться одной и той же доской постоянно.\n" \
                                      "Основная часть урока:\n" \
                                      "Уроки бывают разного вида\n" \
                                      "▪️Новая теория + практика по ней\n" \
                                      "▪️Повторение старого, доказательства нужных для ЕГЭ теорем\n" \
                                      "▪️Разбор конкретных задач по просьбе ученика\n" \
                                      "▪️Сугубо практика по решению конкретных типов задач, например неравенств с применением рационализации или параметры решающиеся через хОа, применение различных теорем с попутным объяснением применяемых в решении фактов.\n" \
                                      "▪️и другие \n\n" \
                                      "Конец урока:\n" \
                                      "▪️Подводим итоги\n" \
                                      "▪️Обсуждаем то, что вызвало сложности\n" \
                                      "▪️Я рассказываю, чем будем заниматься на следующем уроке.")


@bot.message_handler(content_types=['photo'])
def answer(message):
    bot.reply_to(message, "Бот не умеет распознавать фото!")


@bot.message_handler()
def info(message):
    bot.send_message(message.chat.id, "Введена не корректная команда")


bot.polling(none_stop=True)


