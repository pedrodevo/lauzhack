import random

import requests
import os
import sys
import numpy as np
from pdfminer.high_level import extract_text

from keys import HUGGING_FACE_KEY

DEBUG = False
PROGRESS = True

OPENCHAT_URL = "https://api-inference.huggingface.co/models/openchat/openchat_3.5"
# url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
headers = {
    # "Content-Type": "application/json",
    "Authorization": f"Bearer {HUGGING_FACE_KEY}"
}
data = {
    "inputs": "You are a large language model named OpenChat. Write a poem to describe yourself"
}


def query_pdf(payload):
    response = requests.post(
        OPENCHAT_URL,
        headers=headers,
        json=payload
    )
    return response.json()


# print(query_pdf(data))

API_URL = "https://api-inference.huggingface.co/models/valhalla/t5-base-qa-qg-hl"
headers = {"Authorization": f"Bearer {HUGGING_FACE_KEY}"}

"""
given a pdf file, convert it to a txt file
"""


KEYPHRASE_URL = "https://api-inference.huggingface.co/models/ml6team/keyphrase-extraction-kbir-inspec"
headers = {"Authorization": f"Bearer {HUGGING_FACE_KEY}"}


def keyphrase_query(payload):
    responses = requests.post(KEYPHRASE_URL, headers=headers, json=payload)
    # result = []
    # for response in responses.json():
    #     result.append(response['word'])
    for response in responses.json():
        if type(response) != str:
            result = [response.get("word").strip()]
        else:
            print(response)
            result = []
    return np.unique(result)


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
    while len(text) != 0:
        length = random.randint(80, 100)
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


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


for sentence in txt_to_list(pdf_to_txt('lecture.pdf')):
    output = query({
        "inputs": sentence,
    })

    print(output)

# def query_asr(filename):
#     with open(filename, "rb") as f:
#         data = f.read()
#     response = requests.post(
#         "https://api-inference.huggingface.co/models/openai/whisper-large-v3",
#         headers=headers,
#         data=data
#     )
#     return response.json()
