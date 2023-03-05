import re
import mysql.connector
# from mysql.connector import errorcode
import telebot
from telebot import types
bot = telebot.TeleBot('6116709046:AAGyX2UF_4fgLIVUQndbfrW4Ca2af-Xus7U')  # Токен для управления бота
admin_list = [892133524, 493498734, 1017204373, 1247695547]  # Димас, Некит, Элис, Мадиярочка
admins = {892133524: "Дмитрий", 493498734: "Никита", 1017204373: "Алиса", 1247695547: "Мадияр"}  # Знает имена админов


allowed_domains = ["gmail.com", "mail.ru", "yahoo.com"]    # список доменных зон, которые будем проверять
# словари
last_click_time = {}
last_message_time = {}
user_data = {}


# Подключение к базе данных
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="libshopdb"
)
# Создание курсора
mycursor = mydb.cursor()    # используется для выбора из базы данных некоторого подмножества хранимой в ней информации.
# Первое состояние диалога
SELECTING, SAVING = range(2)


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
        bot.send_message(message.chat.id, f"Здравствуйте, {name}! Я бот, который может вам помочь. "
                                                                f"Для начала зарегистрируйтесь /register",
                         reply_markup=keyboard)
        print("Пользователь зашел")


@bot.message_handler(commands=['add'])  # Команда добавления заказов
def handle_add_order(message):
    print("Введите ID заказа")
    # запрашиваем id заказа
    bot.send_message(message.chat.id, 'Введите ID заказа')
    # ждем ответа от пользователя и сохраняем его в переменную order_id
    bot.register_next_step_handler(message, lambda m: handle_order_id(m, message))


def handle_order_id(message, prev_message):
    order_id = message.text
    # запрашиваем дату заказа
    bot.send_message(prev_message.chat.id, 'Введите дату заказа в формате YYYY-MM-DD')
    # ждем ответа от пользователя и сохраняем его в переменную date
    bot.register_next_step_handler(message, lambda m: handle_order_date(m, prev_message, order_id))


def handle_order_date(message, prev_message, order_id):
    date = message.text
    # запрашиваем id пользователя
    bot.send_message(prev_message.chat.id, 'Введите ID пользователя')
    # ждем ответа от пользователя и сохраняем его в переменную user_id
    bot.register_next_step_handler(message, lambda m: handle_user_id(m, prev_message, order_id, date))


def handle_user_id(message, prev_message, order_id, date):
    user_id = message.text
    # запрашиваем имя пользователя
    bot.send_message(prev_message.chat.id, 'Введите имя пользователя')
    # ждем ответа от пользователя и сохраняем его в переменную name
    bot.register_next_step_handler(message, lambda m: handle_user_name(m, prev_message, order_id, date, user_id))


def handle_user_name(message, prev_message, order_id, date, user_id):
    name = message.text
    # запрашиваем фамилию пользователя
    bot.send_message(prev_message.chat.id, 'Введите фамилию пользователя')
    # ждем ответа от пользователя и сохраняем его в переменную surname
    bot.register_next_step_handler(message, lambda m: handle_user_surname(m, prev_message, order_id, date, user_id, name))


def handle_user_surname(message, prev_message, order_id, date, user_id, name):
    surname = message.text
    # запрашиваем тип доставки
    bot.send_message(prev_message.chat.id, 'Введите тип доставки')
    # ждем ответа от пользователя и сохраняем его в переменную delivery_type
    bot.register_next_step_handler(message,
                                   lambda m: handle_delivery_type(m, prev_message, order_id, date, user_id, name,
                                                                  surname))


def handle_delivery_type(message, prev_message, order_id, date, user_id, name, surname):
    delivery_type = message.text
    # запрашиваем тип оплаты
    bot.send_message(message.chat.id, 'Введите тип оплаты')
    # ждем ответа от пользователя и сохраняем его в словаре user_data
    bot.register_next_step_handler(message, handle_payment_type, prev_message, order_id, date, user_id, name, surname, delivery_type)


def handle_payment_type(message, prev_message, order_id, date, user_id, name, surname, delivery_type):
    payment_type = message.text
    # запрашиваем сумму заказа
    bot.send_message(message.chat.id, 'Введите сумму заказа')
    # ждем ответа от пользователя и сохраняем его в словаре user_data
    bot.register_next_step_handler(message, handle_order_amount, prev_message, order_id, date, user_id, name, surname, delivery_type, payment_type)


def handle_order_amount(message, prev_message, order_id, date, user_id, name, surname, delivery_type, payment_type):
    order_amount = message.text
    # добавляем заказ в таблицу orders
    add_order(order_id, date, user_id, name, surname, delivery_type, payment_type, order_amount)
    # сообщаем пользователю, что заказ успешно добавлен
    bot.send_message(message.chat.id, 'Заказ успешно добавлен')


def add_order(order_id, date, user_id, name, surname, delivery_type, payment_type, order_amount):
    # Подключение к базе данных
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="libshopdb"
    )
    mycursor = mydb.cursor()
    # используем команду INSERT для добавления новой строки в таблицу orders
    sql = "INSERT INTO orders (OrderID, Date, UserID, Name, Surname, DeliveryTypeID, PaymentTypeID, OrderAmount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (order_id, date, user_id, name, surname, delivery_type, payment_type, order_amount)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "запись добавлена в таблицу orders")


# обработчик команды "/orders"
@bot.message_handler(commands=['orders'])
def orders(message):
    user_id = message.from_user.id

    # запрос в базу данных на получение заказов пользователя
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM orders WHERE UserID = %s", (user_id,))
    rows = cursor.fetchall()

    # обрабатываем результат запроса
    if len(rows) == 0:
        bot.reply_to(message, "У вас нет заказов.")
    else:
        orders_list = "Ваши заказы:\n\n"
        for row in rows:
            order_id = row[0]
            order_date = row[1]
            order_name = row[2]
            order_surname = row[3]
            order_delivery = row[4]
            order_payment = row[5]
            order_amount = row[6]
            order_info = f"Номер заказа: {order_id}\nДата заказа: {order_date}\nИмя: {order_name}\nФамилия: {order_surname}\nТип доставки: {order_delivery}\nТип оплаты: {order_payment}\nСумма заказа: {order_amount}\n\n"
            orders_list += order_info
        bot.reply_to(message, orders_list)
    cursor.close()
# А вот тут конец админки


# функция обработки команды /register
@bot.message_handler(commands=['register'])
def register_user(message):
    user_id = message.chat.id
    user_data[user_id] = {}
    bot.reply_to(message, "Введите свое имя:")
    bot.register_next_step_handler(message, get_user_name)

def get_user_name(message):
    user_id = message.chat.id
    user_name = message.text
    if 3 <= len(user_name) <= 10:
        user_data[user_id]['user_name'] = user_name
        bot.reply_to(message, "Введите номер телефона:")
        bot.register_next_step_handler(message, get_phone_number_step2)
    elif len(user_name) < 3:
        bot.reply_to(message, "Имя не может содержать менее 3 символов. Введите корректное имя:")
        bot.register_next_step_handler(message, get_user_name)
    else:
        bot.reply_to(message, "Имя не может содержать более 10 символов. Введите корректное имя:")
        bot.register_next_step_handler(message, get_user_name)


def get_phone_number_step2(message):
    user_id = message.chat.id
    phone_number = message.text
    if re.match(r'^\+?\d{1,12}$', phone_number):
        user_data[user_id]['phone_number'] = phone_number
        bot.reply_to(message, "Введите пароль:")
        bot.register_next_step_handler(message, get_user_password)
    else:
        bot.reply_to(message, "Введите корректный номер телефона (только цифры и символ плюс, до 12 символов)")
        bot.register_next_step_handler(message, get_phone_number_step2)


def get_user_password(message):
    user_id = message.chat.id
    user_data[user_id]['password'] = message.text
    bot.reply_to(message, "Введите адрес электронной почты:")
    bot.register_next_step_handler(message, get_user_email)


def get_user_email(message):
    user_id = message.chat.id
    user_data[user_id]['email'] = message.text

    # проверяем, что Email на английском языке
    if not re.match(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', user_data[user_id]['email']):
        bot.reply_to(message, "Введите корректный адрес электронной почты на английском языке, например, example@gmail.com")
        bot.register_next_step_handler(message, get_user_email)
        return

    # проверяем, что Email содержит допустимый домен
    valid_domains = ['gmail.com', 'mail.ru']
    if not any(domain in user_data[user_id]['email'] for domain in valid_domains):
        bot.reply_to(message, "Введите адрес электронной почты с допустимым доменом: @gmail.com или @mail.ru")
        bot.register_next_step_handler(message, get_user_email)
        return

    # создаем inline клавиатуру с двумя кнопками "Да" и "Нет"
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton(text='Да', callback_data='yes')
    no_button = types.InlineKeyboardButton(text='Нет', callback_data='no')
    markup.row(yes_button, no_button)

    # задаем вопрос "Все верно?" с помощью inline клавиатуры
    bot.reply_to(message, "Все верно?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.message.chat.id
    # если пользователь ответил "Да", то добавляем информацию в базу данных
    if call.data == "yes":
        user_name = user_data[user_id]['user_name']
        phone_number = user_data[user_id]['phone_number']
        password = user_data[user_id]['password']
        email = user_data[user_id]['email']
        try:
            mycursor.execute(
                "INSERT INTO users (UserID, PhoneNumber, Password, UserName, Email, RoleID) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, phone_number, password, user_name, email, 2))
            mydb.commit()
            bot.reply_to(call.message, "Вы успешно зарегистрированы!")
        except mysql.connector.Error as err:
            bot.reply_to(call.message, "Произошла ошибка при регистрации: Вы уже зарегистрированы")
    # если пользователь ответил "Нет", то начинаем регистрацию заново
    elif call.data == "no":
        bot.reply_to(call.message, "Введите свое имя:")
        user_data[user_id] = {}
        bot.register_next_step_handler(call.message, get_user_name)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == 'Меню':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('Перейти на сайт⏩')
            item2 = types.KeyboardButton('Отслеживание заказа⏩')
            item3 = types.KeyboardButton('О Боте⏩')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Вот что я умею:', reply_markup=markup)

        elif message.text == 'Перейти на сайт⏩':
            bot.send_message(message.chat.id, "По ссылке вы можете перейти на наш сайт📚" 'http://surl.li/ewhrr')

        elif message.text == 'Отслеживание заказа⏩':
            bot.send_message(message.chat.id, "Пожалуйста введите код отслеживания:")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton('Назад⏪')
            markup.add(back)
            bot.register_next_step_handler(message, handle_tracking_code, markup)

        elif message.text == 'О Боте⏩':
            print("О Боте")
            bot.send_message(message.chat.id, """Добро пожаловать в онлайн книжный магазин!📚 
Я умею:

Показывать каталог книг с подробными описаниями и изображениями;✅

Помогать выбрать книгу по жанру, автору или тематике;✅

Принимать заказы и осуществлять оплату;✅

Отслеживать статус заказа и предоставлять отчет о доставке.✅

Не стесняйтесь задавать мне вопросы, я всегда готов помочь!
По всем вопросам: @dmitriyk97""")


def handle_tracking_code(message, markup):

    # получаем номер заказа из сообщения
    order_id = int(message.text)
    # выполняем запрос к базе данных для получения информации о заказе
    mycursor.execute('SELECT * FROM orders WHERE OrderID = %s', (order_id,))
    result = mycursor.fetchone()
    # если заказ не найден, отправляем сообщение об ошибке
    if result is None:
        bot.send_message(message.chat.id, f'Заказ с номером {order_id} не найден')
        return
        # формируем сообщение с информацией о заказе
    order_info = f"Номер заказа: {result[0]}\nДата заказа: {result[1]}\nID пользователя: {result[2]}\nИмя пользователя: {result[3]} {result[4]}\nТип доставки: {result[5]}\nТип оплаты: {result[6]}\nСумма заказа: {result[7]}"
    # отправляем сообщение с информацией о заказе и кнопкой отслеживания
    # добавляем Inline кнопку
    markupInline = types.InlineKeyboardMarkup()
    track_button = types.InlineKeyboardButton(text="Отслеживание заказа⏩", callback_data=f"track_{order_id}")
    markupInline.add(track_button)
    markup = get_yes_no_keyboard()
    bot.send_message(message.chat.id, order_info, reply_markup=markup)


def get_yes_no_keyboard():  # Нужно, что бы после отправки соо можно было отправить еще или выйти в меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_btn = types.KeyboardButton('Отслеживание заказа⏩')
    no_btn = types.KeyboardButton('Меню')
    markup.add(yes_btn, no_btn)
    return markup


print("Bot in work...")
# запуск бота и непрерывная работа
bot.polling(none_stop=True)
