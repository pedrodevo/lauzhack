#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages. Receives file and sends it to trained model in backend.
returns the text from the model and sends it back to the user.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.


Usage:

```python
python echobot.py
```

Press Ctrl-C on the command line to stop the bot.


### past exam fine-tuning

- /pastexams
- /coursenotes
- /generateexam
"""

import logging


from pdfminer.high_level import extract_text
from telegram import ForceReply, Update
from telegram.ext import Updater, Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from keys import TELEGRAM_KEY
import test_huggingface 
from utils import text_to_pdf

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

PROGRESS = True
DEBUG = True
FILE_TRANSCRIPT = "files/transcription.txt"
FILE_PRELIMINARY = "files/preliminary.pdf"
FILE_OUTPUT_TXT = "files/output.txt"
FILE_OUTPUT_PDF = "files/output.pdf"

# Define states
WAITING_FOR_COMMAND, WAITING_FOR_FILE = range(2)

def start_command(update: Update, context):
    update.message.reply_text('Please input a command to specify what kind of file you want to upload.')
    return WAITING_FOR_COMMAND

def handle_command(update: Update, context):
    # Handle the command here
    update.message.reply_text('Waiting for file...')
    return WAITING_FOR_FILE

def handle_file(update: Update, context):
    file = update.message.document.get_file()

    # Download the file
    file.download('file.txt')

    update.message.reply_text('File received and transcribed.')
    return ConversationHandler.END

# def main():
#     updater = Updater(token='YOUR_BOT_TOKEN', use_context=True)

#     conv_handler = ConversationHandler(
#         entry_points=[CommandHandler('start', start_command)],
#         states={
#             WAITING_FOR_COMMAND: [MessageHandler(Filters.text & ~Filters.command, handle_command)],
#             WAITING_FOR_FILE: [MessageHandler(Filters.document, handle_file)]
#         },
#         fallbacks=[CommandHandler('cancel', lambda update, context: ConversationHandler.END)],
#     )

#     updater.dispatcher.add_handler(conv_handler)

#     updater.start_polling()
#     updater.idle()


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text + " LauzHack!!")

async def attachment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo user attachment."""
    # Get the file path and download the file
    file = await update.message.document.get_file()

    tmp_file = FILE_PRELIMINARY
    await file.download_to_drive(tmp_file)
    
    # Read PDF and extract text
    try:
        extracted_text = extract_text(tmp_file)
    except Exception as e:
        print(e)
        return  # Exit if there's an error in text extraction
    # Write PDF text to a .txt file
    with open(FILE_TRANSCRIPT, "w") as txt_file:
        txt_file.write(extracted_text)

    # Get title (you may want to extract it from the PDF metadata)

    await update.message.reply_text("PDF received and transcribed!")
    # Respond with the transcribed text file
    with open(FILE_TRANSCRIPT, "r") as txt_file:
        title = txt_file.readline()
        await update.message.reply_document(txt_file, caption=f"PDF title: {title}")

    success = test_huggingface.execute_pipeline()

    if not success:
        await update.message.reply_text("Error generating exam :(")
    else:
        await update.message.reply_document(FILE_OUTPUT_PDF, caption="Exam generated!")


async def test_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test the bot."""
    await update.message.reply_text("Test!")
    # TODO: finish this function; it should send a file to the backend and return the text

async def coursenotes_command(update: Update, context):
    await update.message.reply_text('Please upload the course notes.')
    return WAITING_FOR_FILE

async def pastexams_command(update: Update, context):
    await update.message.reply_text('Please upload the past exams.')
    return WAITING_FOR_FILE

async def generate_exam_command(update: Update, context):
    ...
    # try except try except? 

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_KEY).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("testme", test_me)) # delete??? 
    application.add_handler(CommandHandler("pastexams", pastexams_command))
    application.add_handler(CommandHandler("coursenotes", coursenotes_command))
    application.add_handler(CommandHandler("generateexam", generate_exam_command))



    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        # attachments
    application.add_handler(
        MessageHandler(filters.ATTACHMENT & ~filters.COMMAND, attachment, block=True)
    )


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()