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
FILE_INPUT = "files/preliminary.pdf"
FILE_OUTPUT_TXT = "files/output.txt"
FILE_OUTPUT_PDF = "files/output.pdf"
FILE_DIR = "files/"



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

async def upload_coursenotes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo user attachment."""
    # Get the file path and download the file
    await update.message.reply_text("Send me your coursenotes")

    file = get_uploaded_file(update, context)

    tmp_file = FILE_INPUT
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

    await update.message.reply_text("PDF received and transcribed!")

async def upload_pastexams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Upload past exams into telegram bot."""
    await update.message.reply_text("Send exams from previous years")

    file = await get_uploaded_file(update, context)

    tmp_file = FILE_DIR+"exam.pdf"
    await file.download_to_drive(tmp_file)
    
    # Read PDF and extract text
    try:
        extracted_text = extract_text(tmp_file)
    except Exception as e:
        print(e)
        return  # Exit if there's an error in text extraction
    
    # Write PDF text to a .txt file
    with open(FILE_DIR+"exam.txt", "w") as txt_file:
        txt_file.write(extracted_text)

    await update.message.reply_text("PDF received and transcribed!")


    #----------
    # GOOOOD - this is useful
    # with open(FILE_TRANSCRIPT, "r") as txt_file:
    #     title = txt_file.readline()
    #     await update.message.reply_document(txt_file, caption=f"PDF title: {title}")

    # success = test_huggingface.execute_pipeline()

    # if not success:
    #     await update.message.reply_text("Error generating exam :(")
    # else:
    #     await update.message.reply_document(FILE_OUTPUT_PDF, caption="Exam generated!")

    #---------

# async def upload_coursenotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Echo user attachment."""
#     file = await get_uploaded_file(update)

#     if file is None:
#         return  # Exit if no file uploaded

#     coursenote_input = FILE_DIR+"course_notes.pdf"
#     coursenote_transcript = FILE_DIR+"course_notes.txt"
    
#     await process_uploaded_file(file, coursenote_input, coursenote_transcript)


async def get_uploaded_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the uploaded file."""
    if update.message.document:
        file = await update.message.document.get_file()
        return file





async def generate_exam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Execute CHAT-GPT Query"""
    print("Generating exam...")


# async def process_uploaded_file(file, file_input, file_transcript):
#     """Process the uploaded file."""
#     tmp_file = file_input
#     await file.download_to_drive(tmp_file)
    
#     try:
#         extracted_text = extract_text(tmp_file)
#     except Exception as e:
#         print(e)
#         return  # Exit if there's an error in text extraction
    
#     with open(file_transcript, "w") as txt_file:
#         txt_file.write(extracted_text)


async def test_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test the bot."""
    await update.message.reply_text("Test!")
    # TODO: finish this function; it should send a file to the backend and return the text


# async def upload_pastexams(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Upload past exams into telegram bot."""
#     await update.message.reply_text("Send exams from previous years")

#     FILE_DIR = "your_directory_path_here"  # Define your file directory
#     exam_number = 1  # Counter for exam numbering

#     while True:
#         file = await get_uploaded_file(update)

#         if file is None:
#             break  # Exit loop if no file uploaded

#         FILE_INPUT = f"{FILE_DIR}/exam{exam_number}.pdf"
#         FILE_TRANSCRIPT = f"{FILE_DIR}/exam{exam_number}.txt"

#         await process_uploaded_file(file, FILE_INPUT, FILE_TRANSCRIPT)
#         exam_number += 1

#         # Ask if the user wants to upload another exam
#         await update.message.reply_text("Do you want to send another exam? (Yes/No)")

#         user_response = await get_user_response(update)
#         if user_response.text and user_response.text.lower() != 'yes':
#             break  # Exit loop if the user doesn't want to send another exam

    # Additional processing or reply after all exams are uploaded



# async def load_document(input_filepath, output_filepath, transmitted_file):
#     """Load document from telegram"""
#     await file.download_to_drive(filepath)

#     try:
#         extracted_text = extract_text(previous_exam_pdf[0])
#     except Exception as e:
#         print(e)
#         return  # Exit if there's an error in text extraction
    
#     with open(FILE_TRANSCRIPT, "w") as txt_file:
#         txt_file.write(previous_exam_txt[0])


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_KEY).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("testme", test_me))
    application.add_handler(CommandHandler("coursenotes", upload_coursenotes))
    application.add_handler(CommandHandler("pastexams", upload_pastexams))
    application.add_handler(CommandHandler("generateexam", generate_exam))
    application.add_handler(MessageHandler(filters.ATTACHMENT, get_uploaded_file))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

        # attachments
    # application.add_handler(
    #     MessageHandler(filters.ATTACHMENT & ~filters.COMMAND, attachment, block=True)
    # )


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()