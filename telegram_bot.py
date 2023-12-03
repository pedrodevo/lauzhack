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

"""

import logging


from pdfminer.high_level import extract_text
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from keys import TELEGRAM_KEY

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


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

    tmp_file = "files/preliminary.pdf"
    await file.download_to_drive(tmp_file)
    
    # Read PDF and extract text
    try:
        extracted_text = extract_text(tmp_file)
    except Exception as e:
        print(e)
        return  # Exit if there's an error in text extraction
    # Write PDF text to a .txt file
    with open("files/transcription.txt", "w") as txt_file:
        txt_file.write(extracted_text)

    # Get title (you may want to extract it from the PDF metadata)

    # Respond with the transcribed text file
    with open("files/transcription.txt", "r") as txt_file:
        title = txt_file.readline()
        await update.message.reply_document(txt_file, caption=f"PDF title: {title}")

async def test_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test the bot."""
    await update.message.reply_text("Test!")
    # TODO: finish this function; it should send a file to the backend and return the text


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_KEY).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("testme", test_me))

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