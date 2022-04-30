# Импортируем необходимые классы.
import json
from random import shuffle
import os
import logging
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5286642210:AAEI3OsKiWZy4YnsFyU8UdfWa7v1hVCURV4'
count_json = 0


def start(update, context):
    update.message.reply_text('Скиньте файл JSON c тестом')
    context.user_data['questions'] = False
    context.user_data['count_question'] = 0
    context.user_data['count_correct_answers'] = 0
    context.user_data['first_question'] = True

    return 1


def files(update, context):
    global count_json
    print(update.message.effective_attachment.get_file())
    newFile = update.message.effective_attachment.get_file()
    newFile.download(f'files/{count_json}.json')
    context.user_data['questions'] = parse_questions(f'files/{count_json}.json')
    count_json += 1
    update.message.reply_text("Отлично! Введите любой символ для начала викторины")
    return 2


def parse_questions(path):
    with open(path, encoding='utf-8') as cat_file:
        response = json.load(cat_file)['test']
        print(response)
    answer = []

    for question in response:
        print((question['question'], question['response']))
        answer.append((question['question'], question['response']))
    shuffle(answer)
    return answer


def start_questions(update, context):
    if not context.user_data['first_question']:
        if context.user_data['questions'][context.user_data['count_question']][1] == update.message.text:
            context.user_data['count_correct_answers'] += 1
        context.user_data['count_question'] += 1

        if context.user_data['count_question'] == len(context.user_data['questions']):
            update.message.reply_text(f'Поздравляю, вы набрали очков: {context.user_data["count_correct_answers"]}')
            update.message.reply_text(f'Новая викторина: /start')

            return ConversationHandler.END

        update.message.reply_text(context.user_data['questions'][context.user_data['count_question']][0])

    else:
        update.message.reply_text(context.user_data['questions'][context.user_data['count_question']][0])
        context.user_data['first_question'] = False
    return 2


def stop(update, context):
    update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('start', start)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.document, files, pass_user_data=True)],
            2: [MessageHandler(Filters.text & ~Filters.command, start_questions, pass_user_data=True)],

        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
