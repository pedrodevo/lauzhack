import random

import requests
import os
import sys
from openai import OpenAI
from pdfminer.high_level import extract_text

# INFO FOR API CALLS
from keys import OPENAI_KEY
from utils import create_exam_pdf

# RUNNING INFO PRINTING
DEBUG = True
EXTENSIVE_DEBUG = False
PROGRESS = True

# THINGS YOU CAN CHANGE
QUESTIONS = 20
DATA = 'files/lecture_notes.pdf'
OUTPUT = 'files/output.pdf'
# INPUT = 'files/input.pdf'

client = OpenAI(
    api_key=OPENAI_KEY,
    # LauzHack
    organization="org-bcv27ooZj8JyXgpgj5sed8rH",
)

def gpt_query(payload):
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    # giving history of chat
    messages=[
        {"role": "system", "content": f'I am doing an exam for a university level course. I will send you the course notes \
         and you will generate {QUESTIONS} questions based on the notes. The questions should be relevant to the course and \
            should be answerable by someone who has studied the course, yet not fully trivial.'},
        {"role": "user", "content": payload}]
        )

    # extract text
    print(response.choices[0].message.content)
    return response.choices[0].message.content


def execute_pipeline():
    with open('files/transcription.txt', 'r') as file:
        text = file.read().rstrip('\n')

    try:
        print("-- Querying GPT --")
        response = gpt_query(text)
    except Exception as e:
        print(e)
        return False

    print(response)

    return False
    

def main():
    extracted_text = extract_text(DATA)
    gpt_query(extracted_text)



if __name__ == "__main__":
    main()
