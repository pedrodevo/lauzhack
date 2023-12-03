import random

import requests
import os
import sys
from openai import OpenAI
from pdfminer.high_level import extract_text

# INFO FOR API CALLS
from keys import OPENAI_KEY
from keys import HUGGING_FACE_KEY
from utils import create_exam_pdf

# RUNNING INFO PRINTING
DEBUG = False
EXTENSIVE_DEBUG = False
PROGRESS = True

# THINGS YOU CAN CHANGE
QUESTIONS = 20
FILES = 'files'
DOCUMENT = 'preliminary'
EXAM = 'exam'
DATA_NOTES = '/'.join([FILES, DOCUMENT]) + '.pdf'
DATA_EXAM = '/'.join([FILES, EXAM]) + '.pdf'
OUTPUT = 'files/output.pdf'
# INPUT = 'files/input.pdf'

KEYPHRASE_URL = "https://api-inference.huggingface.co/models/ml6team/keyphrase-extraction-kbir-inspec"
headers = {"Authorization": f"Bearer {HUGGING_FACE_KEY}"}


def keyphrase_query(payload):
    responses = requests.post(KEYPHRASE_URL, headers=headers, json=payload)
    # result = []
    # for response in responses.json():
    #     result.append(response['word'])
    result = set()  # Use a set for efficient uniqueness checking

    for response in responses.json():
        if isinstance(response, dict):
            word = response.get("word")
            if isinstance(word, str):
                result.add(word.strip())
        if EXTENSIVE_DEBUG:
            print(response)

    return list(result)


def txt_to_list(text):
    if PROGRESS:
        print('-- START: txt_to_list --')
    text = text.split('.')
    if DEBUG:
        print(text[0])
    max_len = 36

    questions = []
    while len(text) > 0:
        sentences = '. '.join(text[:max_len])
        keyphrases = keyphrase_query(sentences)
        for keyphrase in keyphrases:
            sentences = f' <hl> {keyphrase} <hl> '.join(sentences.split(keyphrase))
        questions.append(sentences)
        text = text[max_len:]
        if EXTENSIVE_DEBUG:
            print(text)
        max_len = max_len-1
    if PROGRESS:
        print('-- DONE: txt_to_list --')
    return questions


client = OpenAI(
    api_key=OPENAI_KEY,
    # LauzHack
    organization="org-bcv27ooZj8JyXgpgj5sed8rH",
)


def gpt_query(payload, past_exam):

    response = []
    total = len(payload)
    print(f'Total messages: {total}')
    for i in range(len(payload)):
        print(f'{i+1}. Length of message: {len(payload[i])}')
        response.append(client.chat.completions.create(
        model="gpt-3.5-turbo",
        # giving history of chat
        messages=[
            {"role": "system", "content": f'I am doing an exam for a university level course at a technical university. \
             I will send you the course notes and you will generate 1 question based on the notes. The questions \
             should be relevant to the course and should be answerable by someone who has studied the course, yet not \
             fully trivial. The context for each question will be put in a form of a (python list) and some of the key \
             words will be highlighted by putting <hl> <hl> around it; for example: \
             The highlighted words dont have to be answers but it is incentivised. Also the questions from a past exam \
             are given as an example. Try not only to use the first exam question as a template but also explore other questions \
             and even new questions. Also questions already asked are given as a list, dont pose questions about the same \
             topic more than 1 time, make a new question from the content. Limit the use of define questions'},
            {"role": "user", "content": 'past exam: ' + past_exam},
            {"role": "user", "content": 'content: ' + payload[i]},
            {"role": "user", "content": 'asked questions: ' + str(response)},]
            ))

    print('Done')
    # extract text
    return response


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
    extracted_text = extract_text(DATA_NOTES)
    past_exam = extract_text(DATA_EXAM)
    splitted_text = txt_to_list(extracted_text)
    question_list = gpt_query(splitted_text, past_exam)
    for question in question_list:
        print(question.choices[0].message.content)


if __name__ == "__main__":
    main()
