import logging

import urllib3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext, MessageHandler, Filters,
)

import database
import schools

token = ""
design_names = ['clown.css',
                'dark.css',
                'devil.css',
                'hearts.css',
                'microbe.css',
                'smile_with_eyes.css',
                'smile_with_glasses.css',
                'smile_with_hearts.css',
                'test.css']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
database = database.Database("schools.db", 1)
# database.create()

help_text = """🍗 хола"""

state_login_f, state_login_s, state_menu, state_design = range(4)


def getdatabyuserid(userid):
    return database.select('csrf', 'account', userid), database.select('session', 'account', userid), \
           database.select('url', 'account', userid)


def middleWare(userid):
    csrf, session, url = getdatabyuserid(userid=userid)

    if not csrf or not session:
        return False

    return schools.SchoolsAPI(csrf=csrf[0], session=session[0], url=url[0]).isValid()


def auth(update, _):
    _.user_data.clear()
    _.user_data['message'] = update.message.reply_text("Мы заметили, что вы не авторизованы или "
                                                       "данные устарели. Введите ваш логин от schools.by:")


def showMenu(update, _, query=None, inNew=False):
    _.user_data.clear()
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('✨ Оформление', callback_data='design'),
            InlineKeyboardButton('🤞🏻 Оценки', callback_data='grade'),
            InlineKeyboardButton('📆 Расписание', callback_data='timetable')
        ]
    ])

    if query is None:
        update.message.reply_text(text="Выберите пункт меню", reply_markup=reply_markup)
    else:
        if inNew:
            query.message.reply_text(text="Выберите пункт меню", reply_markup=reply_markup)
        else:
            query.edit_message_text(text="Выберите пункт меню", reply_markup=reply_markup)


def handler_design(update: Update, _: CallbackContext) -> int:
    if not middleWare(update.callback_query.from_user.id):
        auth(update.callback_query, _)
        return state_login_f

    query = update.callback_query
    query.answer()

    if query.data == 'back':
        showMenu(update, _, query)
        return state_menu

    csrf, session, url = getdatabyuserid(update.callback_query.from_user.id)
    account = schools.SchoolsAPI(csrf[0], session[0], url[0])
    iduser = database.select('id', 'account', update.callback_query.from_user.id)[0]
    name = account.getFamilyByID(iduser).split()[1]
    account.giveDesign(iduser, design_names[int(query.data) - 1])

    query.edit_message_text(f'Вы успешно изменили оформление, {name}! Проверяйте профиль.')
    showMenu(update, _, query, True)
    return state_menu


def handler_menu(update: Update, _: CallbackContext) -> int:
    if not middleWare(update.callback_query.from_user.id):
        auth(update.callback_query, _)
        return state_login_f

    query = update.callback_query
    query.answer()

    if query.data == 'design':
        query.message.reply_media_group([InputMediaPhoto('https://i.imgur.com/DQCsoqs.png', '1 вариант'),
                                          InputMediaPhoto('https://i.imgur.com/wNuS4S4.png', '2 вариант'),
                                          InputMediaPhoto('https://i.imgur.com/4DQJSm6.png', '3 вариант'),
                                          InputMediaPhoto('https://i.imgur.com/hMKDXDj.png', '4 вариант'),
                                          InputMediaPhoto('https://i.imgur.com/UXcE9Cl.png', '5 вариант'),
                                          InputMediaPhoto('https://i.imgur.com/7kQCJ8p.png', '6 вариант'),
                                          InputMediaPhoto('https://i.imgur.com/bbDloqn.png', '7 вариант'),
                                          InputMediaPhoto('https://i.imgur.com/UiprThp.png', '8 вариант'),
                                          InputMediaPhoto('https://i.imgur.com/6mSXuNH.png', '9 вариант')])

        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('1. клоун', callback_data='1'),
                InlineKeyboardButton('2. черная корона', callback_data='2'),
                InlineKeyboardButton('3. дьявол', callback_data='3')
            ],
            [
                InlineKeyboardButton('4. сердечки', callback_data='4'),
                InlineKeyboardButton('5. микроб', callback_data='5'),
                InlineKeyboardButton('6. грустный', callback_data='6')
            ],
            [
                InlineKeyboardButton('7. в очках', callback_data='7'),
                InlineKeyboardButton('8. сердечки', callback_data='8'),
                InlineKeyboardButton('9. красивая корона', callback_data='9')
            ],
            [
                InlineKeyboardButton('<<< Назад <<<', callback_data='back')
            ]
        ])

        query.message.reply_text('❗️ ВАЖНО! Если у вас уже есть оформление, '
                                 'просто удалите сообщение "Big love from Matteo" для смены дизайна\n\ns'
                                 'Выберите оформление', reply_markup=reply_markup)
        return state_design


def start(update: Update, _: CallbackContext) -> int:
    update.message.reply_text("Привет! Для использования бота необходимо авторизоваться с помощью логина и пароля из "
                              "schools.by\nМы не сохраняем ваши данные, мы их используем для единоразовой авторизации "
                              "на сайте, после чего удаляем их\nРазработчик: Matteo Bunos (> https://t.me/bloglutie <)")

    if not middleWare(update.message.from_user.id):
        auth(update, _)
        return state_login_f

    showMenu(update, _)
    return state_menu


def menu(update: Update, _: CallbackContext) -> int:
    if not middleWare(update.message.from_user.id):
        auth(update, _)
        return state_login_f

    showMenu(update, _)
    return state_menu


def handler_login_first(update: Update, _: CallbackContext) -> int:
    _.user_data['username'] = update.message.text
    _.user_data['message'].edit_text("🎃 Теперь введите пароль от schools.by:")

    update.message.delete()
    return state_login_s


def handler_login_second(update: Update, _: CallbackContext) -> int:
    update.message.delete()
    userid = update.message.from_user.id
    username, password = _.user_data['username'], update.message.text
    _.user_data['message'].edit_text("Пытаемся авторизоваться...")
    data = schools.tryToLogin(username, password)
    if data is None:
        _.user_data['message'].edit_text("Ошибка авторизации. Попробуйте ещё раз. \nВведите ваш логин от schools.by:")
        return state_login_f

    csrf, session, url = data
    correctURL = url[:url.find('schools.by')+10]
    idschools = url.split('/')[-1]

    get_ = database.select('csrf', 'account', userid)
    if get_ is not None:
        database.delete('account', userid)
    database.insert(['`account`', '`csrf`', '`session`', '`url`', '`id`'], [str(userid), f"'{csrf}'", f"'{session}'",
                                                                    f"'{correctURL}'", str(idschools)])

    schoolsAccount = schools.SchoolsAPI(csrf, session, correctURL)
    _.user_data['message'].edit_text(f"Вы успешно авторизовались, {' '.join(schoolsAccount.getFamilyByID(idschools).split()[1:])}!\n"
                      f"Ваш подсайт: {correctURL}")
    _.user_data.clear()
    return state_menu


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('menu', menu)],
        states={
            state_login_f: [
                MessageHandler(filters=Filters.all, callback=handler_login_first),
            ],
            state_login_s: [
                MessageHandler(filters=Filters.all, callback=handler_login_second),
            ],
            state_menu: [
                CallbackQueryHandler(handler_menu),
            ],
            state_design: [
                CallbackQueryHandler(handler_design),
            ],
            # state_day: [
            #     CallbackQueryHandler(handler_day),
            # ],
            # state_time: [
            #     MessageHandler(filters=Filters.all, callback=handler_time),
            # ],
        },
        fallbacks=[CommandHandler('start', start), CommandHandler('menu', menu)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling
    # updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    urllib3.disable_warnings(UserWarning)
    main()
