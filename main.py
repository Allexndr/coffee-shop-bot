import telebot
from telebot import types
import json
from collections import defaultdict
import os

TOKEN = '8462219705:AAFbVLXSdQNu_2oPmsO_dO1mmgXrEt4kYmM'
bot = telebot.TeleBot(TOKEN)

# Cart storage file
CART_FILE = 'cart_data.json'

# Load cart from file
def load_cart():
    if os.path.exists(CART_FILE):
        try:
            with open(CART_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return defaultdict(list, {int(k): v for k, v in data.items()})
        except (json.JSONDecodeError, ValueError):
            pass
    return defaultdict(list)

# Save cart to file
def save_cart(cart_data):
    with open(CART_FILE, 'w', encoding='utf-8') as f:
        json.dump(dict(cart_data), f, ensure_ascii=False, indent=2)

# Shopping cart storage
cart = load_cart()
user_state = {}

# Product catalog with images and prices
PRODUCTS = {
    'drinks': [
        {'id': 'latte', 'name': 'Латте', 'price': 350, 'description': 'Классический латте с нежной пенкой', 'emoji': '☕', 'image': 'content/latte.jpg'},
        {'id': 'cappuccino', 'name': 'Капучино', 'price': 320, 'description': 'Итальянский капучино', 'emoji': '☕', 'image': 'content/cappuccino.jpg'},
        {'id': 'americano', 'name': 'Американо', 'price': 250, 'description': 'Крепкий черный кофе', 'emoji': '☕', 'image': 'content/americano.jpg'},
        {'id': 'espresso', 'name': 'Эспрессо', 'price': 200, 'description': 'Классический эспрессо', 'emoji': '☕', 'image': 'content/espresso.jpg'},
        {'id': 'mocha', 'name': 'Мокко', 'price': 380, 'description': 'Кофе с шоколадом', 'emoji': '☕', 'image': 'content/mocha.jpg'},
    ],
    'breakfast': [
        {'id': 'omlet', 'name': 'Омлет', 'price': 450, 'description': 'Сытный омлет с овощами', 'emoji': '🍳', 'image': 'content/omlet.jpg'},
        {'id': 'pancakes', 'name': 'Блинчики', 'price': 400, 'description': 'Домашние блинчики', 'emoji': '🥞', 'image': 'content/pancakes.jpg'},
        {'id': 'sandwich', 'name': 'Сэндвич', 'price': 380, 'description': 'Сэндвич с курицей', 'emoji': '🥪', 'image': 'content/sandwich.jpg'},
        {'id': 'croissant', 'name': 'Круассан', 'price': 320, 'description': 'Свежий круассан', 'emoji': '🥐', 'image': 'content/croissant.jpg'},
    ],
    'desserts': [
        {'id': 'cheesecake', 'name': 'Чизкейк', 'price': 450, 'description': 'Нью-йорк чизкейк', 'emoji': '🍰', 'image': 'content/cheesecake.jpg'},
        {'id': 'tiramisu', 'name': 'Тирамису', 'price': 420, 'description': 'Классический тирамису', 'emoji': '🍰', 'image': 'content/tiramisu.jpg'},
        {'id': 'brownie', 'name': 'Брауни', 'price': 350, 'description': 'Шоколадный брауни', 'emoji': '🍫', 'image': 'content/brownie.jpg'},
        {'id': 'ice_cream', 'name': 'Мороженое', 'price': 300, 'description': 'Домашнее мороженое', 'emoji': '🍦', 'image': 'content/ice_cream.jpg'},
    ]
}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    cart[user_id] = []
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('📋 Меню', callback_data='menu'),
        types.InlineKeyboardButton('🛒 Корзина', callback_data='cart')
    )
    markup.add(
        types.InlineKeyboardButton('ℹ️ О нас', callback_data='about'),
        types.InlineKeyboardButton('📍 Контакты', callback_data='contacts')
    )
    
    bot.send_message(
        user_id,
        '☕ *Добро пожаловать в Coffee Shop Bot!*\n\n'
        'Здесь вы можете:\n'
        '📋 Просмотреть наше меню\n'
        '🛒 Добавить товары в корзину\n'
        '📞 Оставить отзыв или связаться с нами',
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['menu'])
def show_menu(message):
    send_menu_categories(message.chat.id)

def send_menu_categories(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('☕ Напитки', callback_data='category_drinks'),
        types.InlineKeyboardButton('🍳 Завтраки', callback_data='category_breakfast'),
        types.InlineKeyboardButton('🍰 Десерты', callback_data='category_desserts')
    )
    
    bot.send_message(
        chat_id,
        '📋 *Выберите категорию:*',
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('category_'))
def show_category_products(call):
    category = call.data.split('_')[1]
    products = PRODUCTS.get(category, [])
    
    if not products:
        bot.answer_callback_query(call.id, 'Категория пуста')
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    for product in products:
        markup.add(
            types.InlineKeyboardButton(
                f"{product['emoji']} {product['name']} - {product['price']}₸",
                callback_data=f"product_{product['id']}"
            )
        )
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    
    bot.edit_message_text(
        call.message.chat.id,
        call.message.message_id,
        f"📋 *{category.title()}*:",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
def show_product_details(call):
    product_id = call.data.split('_')[1]
    
    # Find product
    product = None
    for category_products in PRODUCTS.values():
        for p in category_products:
            if p['id'] == product_id:
                product = p
                break
        if product:
            break
    
    if not product:
        bot.answer_callback_query(call.id, 'Товар не найден')
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('➕ Добавить в корзину', callback_data=f"add_{product_id}"),
        types.InlineKeyboardButton('🔙 Назад', callback_data='menu')
    )
    
    # Try to send image if exists
    try:
        with open(product['image'], 'rb') as photo:
            bot.send_photo(
                call.message.chat.id,
                photo,
                caption=f"{product['emoji']} *{product['name']}*\n\n"
                        f"💰 Цена: {product['price']}₸\n"
                        f"📝 {product['description']}",
                parse_mode='Markdown',
                reply_markup=markup
            )
    except FileNotFoundError:
        # Fallback to text message if image not found
        bot.send_message(
            call.message.chat.id,
            f"{product['emoji']} *{product['name']}*\n\n"
            f"💰 Цена: {product['price']}₸\n"
            f"📝 {product['description']}",
            parse_mode='Markdown',
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def add_to_cart(call):
    product_id = call.data.split('_')[1]
    user_id = call.from_user.id
    
    # Find product
    product = None
    for category_products in PRODUCTS.values():
        for p in category_products:
            if p['id'] == product_id:
                product = p
                break
        if product:
            break
    
    if product:
        cart[user_id].append(product)
        save_cart(cart)
        bot.answer_callback_query(call.id, f'✅ {product["name"]} добавлен в корзину')
    else:
        bot.answer_callback_query(call.id, '❌ Товар не найден')

@bot.callback_query_handler(func=lambda call: call.data == 'cart')
def show_cart(call):
    user_id = call.from_user.id
    user_cart = cart.get(user_id, [])
    
    if not user_cart:
        bot.answer_callback_query(call.id, 'Корзина пуста')
        bot.send_message(call.message.chat.id, '🛒 Ваша корзина пуста')
        return
    
    total = sum(item['price'] for item in user_cart)
    text = '🛒 *Ваша корзина:*\n\n'
    
    for i, item in enumerate(user_cart, 1):
        text += f"{i}. {item['emoji']} {item['name']} - {item['price']}₸\n"
    
    text += f'\n💰 *Итого: {total}₸*'
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('🗑️ Очистить корзину', callback_data='clear_cart'),
        types.InlineKeyboardButton('✅ Оформить заказ', callback_data='checkout')
    )
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'clear_cart')
def clear_cart(call):
    user_id = call.from_user.id
    cart[user_id] = []
    save_cart(cart)
    bot.answer_callback_query(call.id, 'Корзина очищена')
    bot.send_message(call.message.chat.id, '🛒 Корзина очищена')

@bot.callback_query_handler(func=lambda call: call.data == 'checkout')
def checkout(call):
    user_id = call.from_user.id
    user_cart = cart.get(user_id, [])
    
    if not user_cart:
        bot.answer_callback_query(call.id, 'Корзина пуста')
        return
    
    total = sum(item['price'] for item in user_cart)
    
    # Send order to admin
    order_text = f"🆕 Новый заказ от @{call.from_user.username or call.from_user.first_name} (ID: {user_id})\n\n"
    for item in user_cart:
        order_text += f"{item['emoji']} {item['name']} - {item['price']}₸\n"
    order_text += f"\n💰 Итого: {total}₸"
    
    # Send to admin chat (replace with actual chat ID)
    # bot.send_message(ADMIN_CHAT_ID, order_text)
    
    cart[user_id] = []
    save_cart(cart)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('📞 Связаться с нами', url='https://wa.me/77002478746'),
        types.InlineKeyboardButton('🔙 В меню', callback_data='menu')
    )
    
    bot.send_message(
        call.message.chat.id,
        '✅ *Заказ принят!*\n\n'
        f'Сумма заказа: {total}₸\n\n'
        'Наш менеджер свяжется с вами для подтверждения.',
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'contacts')
def show_contacts(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('📍 2GIS', url='https://go.2gis.com/sans3'),
        types.InlineKeyboardButton('🗺️ Yandex', url='https://yandex.kz/maps/ru/-/CDuOU4M0')
    )
    markup.add(
        types.InlineKeyboardButton('📞 WhatsApp', url='https://wa.me/77002478746'),
        types.InlineKeyboardButton('📸 Instagram', url='https://instagram.com')
    )
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    
    bot.send_message(
        call.message.chat.id,
        '📍 *Наши контакты*\n\n'
        '📞 Телефон: +7 747 838 2703\n'
        '🏠 Адрес: Кунаева 130\n'
        '⏰ Часы работы: 07:30 - 23:00',
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'about')
def show_about(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    
    bot.send_message(
        call.message.chat.id,
        '☕ *О нашей кофейне*\n\n'
        'Мы - уютная кофейня в центре города, '
        'где каждый гость может насладиться '
        'ароматным кофе и вкусными завтраками.\n\n'
        '✅ Свежая обжарка кофе\n'
        '✅ Домашняя выпечка\n'
        '✅ Бесплатный Wi-Fi\n'
        '✅ Комфортная атмосфера',
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def back_to_menu(call):
    send_menu_categories(call.message.chat.id)

# Handle all other callbacks
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    bot.answer_callback_query(call.id)

# Run bot
if __name__ == "__main__":
    print("🤖 Bot started...")
    bot.polling(none_stop=True)
