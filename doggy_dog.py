#!/usr/bin/env python

import logging
import os
import pickle
import random

import requests
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# включаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('DP_DOGGY_DOG_BOT_TOKEN')

DOG_FACTS = list()
with open('dog_facts_rus.pkl', 'rb') as f:
    DOG_FACTS = pickle.load(f)


# это обработчики команд (handler-ы). Обычно приниают вот эти два параметра, которые содержат нужный
# контекст, то есть необъодимые для нас переменные (типа, имени пользователя, его ID и так далее), и
# созданный нами движок (об этом ниже)

# вот обработчик команды /start. Когда пользователь вводит /start, вызывается эта функция
# то же самое происходит, если пользователь выберет команду start из списка команд (это
# сделаем позже в BotFather)
def start(engine: Update, context: CallbackContext) -> None:
    # получаем имя пользователя, которое он указал у себя в настройках телеграма,
    # из нашего "движка"
    user = engine.effective_user
    # отправляем нашему пользователю приветственное сообщение
    engine.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


# другой обработчик - для команды /help. Когда пользователь вводит /help, вызывается этот код
def help_command(engine: Update, context: CallbackContext) -> None:
    # отправляем какой-то стандартный жестко заданный текст
    engine.message.reply_text('Помощь!')


def get_dog(engine: Update, context: CallbackContext) -> None:
    ret = requests.get('https://random.dog/woof.json')
    random_photo_url = ret.json()['url']
    dog_fact = random.choice(DOG_FACTS)
    print(random_photo_url + dog_fact)
    engine.message.reply_photo(random_photo_url, caption=dog_fact)


def echo(engine: Update, context: CallbackContext) -> None:
    # вызываем команду отправки сообщения пользователю, используя
    # при это текст сообщения, полученный от пользователя
    engine.message.reply_text(engine.message.text)


def main() -> None:
    # создаем объект фреймворка (библиотеки) для создания телеграм-ботов, с помощью
    # которого мы сможем взаимодействовать с фреймворком, то есть тот связующий объект,
    # через который мы будем общаться со всеми внутренностями (которые делают основную
    # работу по отправке сообщений за нас) фреймворка. Причем, общаться будем в обе стороны:
    # принимать сообщения от него и задавать параметры для него
    #
    # я назвал его engine (движок), чтобы было понятнее. В самой либе (библиотеке, фреймворке)
    # он называется Updater, как видно, что немного запутывает
    engine = Updater(BOT_TOKEN)

    # получаем объект "передатчика" или обработчика сообщений от нашего движка
    dispatcher = engine.dispatcher

    # тут "связываем" наши команды и соответствующие им обработчики (хендлеры);
    # иногда говорят "повесить коллбэк" (коллбэк это то же самое что и обработчики (они же хендлеры),
    # то есть та функция, которая вызывается в ответ на какое-то событие: callback, то есть
    # call back - дословно, что-то вроде вызвать обратно, то есть наша функция, которую мы передали,
    # вызовется позже в ответ на какое-то событие; в нашем случае они будут вызываться тогда, когда
    # пользователь будет выбирать соответствующие команды
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("dog", get_dog))

    # говорим обработчику сообений, чтобы он вызывал функцию echo каждый раз,
    # когда пользователь отправляем боту сообщение
    #
    # про параметр 'Filters.text & ~Filters.command' можно пока не заморачиваться;
    # он означает, что функция echo будет вызываться только тогда, когда пользователь
    # ввел именно текст, а не команду; в противном случае, если пользователь введет
    # команду /start или /help, эта функция будет вызвана, что нам не нужно
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # непосредственно старт бота
    engine.start_polling()

    # говорим боту работать, пока не нажмем Ctrl-C или что-то не сломается само :)
    engine.idle()


if __name__ == '__main__':
    main()
