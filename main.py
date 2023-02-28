import sqlite3
import telebot
from telebot import types
bot = telebot.TeleBot('6116709046:AAGyX2UF_4fgLIVUQndbfrW4Ca2af-Xus7U')  # Токен для управления бота
admin_list = [892133524, 493498734, 1017204373, 1247695547]  # Димас, Некит, Элис, Мадиярочка
admins = {892133524: "Дмитрий", 493498734: "Никита", 1017204373: "Алиса", 1247695547: "Мадияр"}  # Знает имена админов

# время задержки в секундах
delay = 10

# словари
last_click_time = {}
last_message_time = {}
user_data = {}

# Подключение к БД


conn = sqlite3.connect('C:\\SqlLite\\Database', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(user_id: int, user_name: str, user_surname: str, username: str):  # Добавление данных в БД
    cursor.execute('INSERT INTO users (user_id, user_name, user_surname, username) VALUES (?, ?, ?, ?)',
                   (user_id, user_name, user_surname, username))
    conn.commit()
    # Подключение к БД


def is_admin(user_id):
    return user_id in admin_list  # Проверяет, является ли user_id администратором.


@bot.message_handler(commands=['start'])
def start_message(message):
    if is_admin(message.from_user.id):
        name = admins.get(message.from_user.id)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создаем клавиатуру и добавляем в нее кнопки
        menu = types.KeyboardButton('Меню')
        keyboard.add(menu)
        bot.send_message(message.chat.id, "Здравствуйте, {}! Мой любимый админ снова со мной.".format(name),
                         reply_markup=keyboard)
        print("Welcome, {}! You are an admin.".format(name))
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        menu = types.KeyboardButton('Меню')
        keyboard.add(menu)
        name = message.from_user.first_name
        bot.send_message(message.chat.id, f"Здравствуйте, {name}! Я бот, который может вам помочь.",
                         reply_markup=keyboard)
        print("Пользователь зашел")

@bot.message_handler(commands=['add'])  # Команда добавления товаров
def handle_add_order(message):
    # запрашиваем id заказа
    bot.send_message(message.chat.id, 'Введите id заказа')
    # ждем ответа от пользователя и сохраняем его в словаре user_data
    bot.register_next_step_handler(message, handle_order_id)

def handle_order_id(message):
    user_data['id'] = message.text
    # запрашиваем название заказа
    bot.send_message(message.chat.id, 'Введите название заказа')
    # ждем ответа от пользователя и сохраняем его в словаре user_data
    bot.register_next_step_handler(message, handle_order_name)

def handle_order_name(message):
    user_data['name'] = message.text
    # запрашиваем номер заказа
    bot.send_message(message.chat.id, 'Введите номер заказа')
    # ждем ответа от пользователя и сохраняем его в словаре user_data
    bot.register_next_step_handler(message, handle_order_tracking)

def handle_order_tracking(message):
    user_data['tracking'] = message.text
    # запрашиваем локацию заказа
    bot.send_message(message.chat.id, 'Введите локацию заказа')
    # ждем ответа от пользователя и сохраняем его в словаре user_data
    bot.register_next_step_handler(message, handle_order_location)

def handle_order_location(message):
    user_data['location'] = message.text
    # добавляем заказ в таблицу orders
    add_order(user_data['id'], user_data['name'], user_data['tracking'], user_data['location'])
    # сообщаем пользователю, что заказ успешно добавлен
    bot.send_message(message.chat.id, 'Заказ успешно добавлен')

# функция для добавления заказа в таблицу orders
def add_order(id, name, tracking, location):
    # conn = sqlite3.connect('C:\\SqlLite\\Database')  # подключаемся к базе данных
    # cursor = conn.cursor()  # создаем курсор для выполнения операций с базой данных
    # используем команду INSERT для добавления новой строки в таблицу orders
    cursor.execute('INSERT INTO orders (id, name, tracking, location) VALUES (?, ?, ?, ?)',
                   (id, name, tracking, location))
    pass
    conn.commit()
    print("Добавлено в БД")
# А вот тут конец админки


@bot.message_handler(content_types=['text'])  # При вводе определенного сообщения боту будет осуществлятся некая команда
def bot_message(message):
    if message.chat.type == 'private':  # Проверка на то, что сообщение было отправлено в личном чате
        if message.text == 'Меню':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Перейти на сайт⏩')
            item2 = types.KeyboardButton('Отслеживание заказа⏩')
            item3 = types.KeyboardButton('О Боте⏩')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Вот что я умею:', reply_markup=markup)

        if message.text == 'Перейти на сайт⏩':
            bot.send_message(message.chat.id, "По ссылке вы можете перейти на наш сайт📚" 'http://surl.li/ewhrr')
        elif message.text == 'Отслеживание заказа⏩':
            bot.send_message(message.chat.id, "Пожалуйста введите код отслеживания:")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад⏪')
            markup.add(back)

            @bot.message_handler(content_types=['text'])
            def handle_text(message):
                if message.text == 'Назад⏪':
                    # обработка кнопки "Назад"
                    return
                # обработка кода отслеживания
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM orders WHERE tracking=?", (message.text,))
                row = cursor.fetchone()
                if row:
                    order_info = f"ID: {row[0]}\nНазвание: {row[1]}\nНомер: {row[2]}\nСтатус: {row[3]}"
                    bot.reply_to(message, order_info, reply_markup=markup)
                    keyboard = types.InlineKeyboardMarkup()
                    button = types.InlineKeyboardButton('Да', callback_data='button_pressed')
                    keyboard.add(button)
                    bot.send_message(message.chat.id, 'Отследить еще заказ?', reply_markup=keyboard)
                else:
                    print("Номер не найден")
                    bot.send_message(message.chat.id, " Номер не найден", reply_markup=markup)
            bot.register_next_step_handler(message, handle_text)

        elif message.text == 'О Боте⏩':  # Бот информирует пользователя на что он способен
            if message.text == 'О Боте⏩':
                bot.send_message(message.chat.id, """Добро пожаловать в онлайн книжный магазин!📚 
Я умею:

Показывать каталог книг с подробными описаниями и изображениями;✅

Помогать выбрать книгу по жанру, автору или тематике;✅

Принимать заказы и осуществлять оплату;✅

Отслеживать статус заказа и предоставлять отчет о доставке.✅

Не стесняйтесь задавать мне вопросы, я всегда готов помочь!
По всем вопросам: @dmitriyk97""")

        # Кнопка возвращающая начальные кнопки
        elif message.text == 'Назад⏪':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Перейти на сайт⏩')
            item2 = types.KeyboardButton('Отслеживание заказа⏩')
            item3 = types.KeyboardButton('О Боте⏩')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Назад⏪', reply_markup=markup)

    if message.text.lower() == 'меню':
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        user_surname = message.from_user.last_name
        username = message.from_user.username

        cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы в базе данных!')
            print("Пользователь попытался снова зарегистрироваться в бд")
        else:
            cursor.execute('INSERT INTO users (user_id, user_name, user_surname, username) VALUES (?, ?, ?, ?)',
                           (user_id, user_name, user_surname, username))
            conn.commit()
            bot.send_message(message.chat.id, 'Вы были успешно зарегистрированы в базе данных!')
            print("Пользователь зарегистрировался")


@bot.callback_query_handler(func=lambda call: call.data == 'button_pressed')
def handle_button_press(call):
    # отправляем сообщение с запросом кода отслеживания
    bot.send_message(call.message.chat.id, 'Пожалуйста, введите код отслеживания:')

    @bot.message_handler(func=lambda message: True)
    def handle_text(message):
        if message.text == 'Назад⏪':
            # обработка кнопки "Назад"
            return
        # обработка кода отслеживания
        cursor.execute("SELECT * FROM orders WHERE tracking=?", (message.text,))
        row = cursor.fetchone()
        if row:
            order_info = f"ID: {row[0]}\nНазвание: {row[1]}\nНомер: {row[2]}\nСтатус: {row[3]}"
            bot.reply_to(message, order_info)
            keyboard = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton('Отследить еще заказ', callback_data='button_pressed')
            keyboard.add(button)
            bot.send_message(message.chat.id, 'Отследить еще заказ?', reply_markup=keyboard)

        else:
            print("Номер не найден")
            bot.send_message(message.chat.id, " Номер не найден")

    bot.register_next_step_handler(call.message, handle_text)
# cursor.close()
# conn.close()
print("Bot in work...")
# запуск бота и непрерывная работа
bot.polling(none_stop=True)