import random

import requests
import os
import sys
from pdfminer.high_level import extract_text

# INFO FOR API CALLS
from keys import HUGGING_FACE_KEY
VALHALLA_URL = "https://api-inference.huggingface.co/models/valhalla/t5-base-qa-qg-hl"
KEYPHRASE_URL = "https://api-inference.huggingface.co/models/ml6team/keyphrase-extraction-kbir-inspec"
OPENCHAT_URL = "https://api-inference.huggingface.co/models/openchat/openchat_3.5"
headers = {"Authorization": f"Bearer {HUGGING_FACE_KEY}"}

# RUNNING INFO PRINTING
DEBUG = False
PROGRESS = True

# THINGS YOU CAN CHANGE
QUESTIONS = 20
FILES = 'files'
DOCUMENT = 'lecture_notes'
DATA = '/'.join([FILES, DOCUMENT]) + '.pdf'

# data = {
#     "inputs": "You are a large language model named OpenChat. Write a poem to describe yourself"
# }


# def query_pdf(payload):
#     response = requests.post(
#         OPENCHAT_URL,
#         headers=headers,
#         json=payload
#     )
#     return response.json()


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
        elif DEBUG:
            print(response)

    return list(result)


def pdf_to_txt(pdf_file, txt_file=None):
    """
    given a pdf file, convert it to a txt file
    """
    if PROGRESS:
        print('-- START: pdf_to_txt --')
    # check if pdf file exists
    if not os.path.isfile(pdf_file):
        print("PDF file {} does not exist.".format(pdf_file))
        sys.exit(1)

    # check if txt file exists
    # if os.path.isfile(txt_file):
    #     print("TXT file {} already exists.".format(txt_file))
    #     sys.exit(1)

    # extract text from pdf file
    text = extract_text(pdf_file)
    assert type(text) == str
    if DEBUG:
        print(text)
    if PROGRESS:
        print('-- DONE: pdf_to_txt --')
    return text


def txt_to_list(text):
    if PROGRESS:
        print('-- START: txt_to_list --')
    text = text.split('.')
    questions = []
    if DEBUG:
        print(text)
    length = len(text)
    while len(text) != 0:
        sentence_length = int(length/QUESTIONS)
        sentence_length += random.randint(-5, 5)
        sentences = '. '.join(text[:length])
        keyphrases = keyphrase_query(sentences)
        for keyphrase in keyphrases:
            sentences = f' <hl> {keyphrase} <hl> '.join(sentences.split(keyphrase))
        questions.append('generate question: ' + sentences)
        text = text[length:]
        if DEBUG:
            print(text)
    if PROGRESS:
        print('-- DONE: txt_to_list --')
    return questions


def valhalla_query(payload):
    response = requests.post(VALHALLA_URL, headers=headers, json=payload)
    return response.json()


for sentence in txt_to_list(pdf_to_txt(DATA)):
    if '<hl>' in sentence:
        print('highlighted')
    output = valhalla_query({
        "inputs": sentence,
    })

    print(output)
