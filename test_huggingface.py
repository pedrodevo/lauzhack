import random

import requests
import os
import sys
from pdfminer.high_level import extract_text

# INFO FOR API CALLS
from keys import HUGGING_FACE_KEY
VOIDFUL_URL = "https://api-inference.huggingface.co/models/voidful/context-only-question-generator"
VALHALLA_URL = "https://api-inference.huggingface.co/models/valhalla/t5-base-qa-qg-hl"
KEYPHRASE_URL = "https://api-inference.huggingface.co/models/ml6team/keyphrase-extraction-kbir-inspec"
OPENCHAT_URL = "https://api-inference.huggingface.co/models/openchat/openchat_3.5"
headers = {"Authorization": f"Bearer {HUGGING_FACE_KEY}"}

# RUNNING INFO PRINTING
DEBUG = False
PROGRESS = True

# THINGS YOU CAN CHANGE
QUESTIONS = 40
FILES = 'files'
DOCUMENT = 'lecture'
DATA = '/'.join([FILES, DOCUMENT]) + '.pdf'
OUTPUT = 'files/output.txt'

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
        if DEBUG:
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
    if DEBUG:
        print(text)
    length = len(text)
    sentence_length = int(length / QUESTIONS+1)
    if sentence_length > 70:
        sentence_length = 70
    if PROGRESS:
        print(f'Questions: {int(length/sentence_length)}')
    questions = []
    while len(text) > 0:
        sentences = '. '.join(text[:sentence_length])
        keyphrases = keyphrase_query(sentences)
        for keyphrase in keyphrases:
            sentences = f' <hl> {keyphrase} <hl> '.join(sentences.split(keyphrase))
        questions.append('generate question: ' + sentences)
        text = text[sentence_length:]
        if DEBUG:
            print(text)
    if PROGRESS:
        print('-- DONE: txt_to_list --')
    return questions


def valhalla_query(payload):
    response = requests.post(VALHALLA_URL, headers=headers, json=payload)
    return response.json()


def voidful_query(payload):
    response = requests.post(VOIDFUL_URL, headers=headers, json=payload)
    return response.json()


def execute_pipeline():
    counter = 0
    with open('files/transcription.txt', 'r') as file:
        text = file.read().rstrip('\n')

    response = []

    for sentence in txt_to_list(text):
        counter += 1
        if '<hl>' in sentence:
            print('Highlighted')
            if counter == 1 and DEBUG:
                print(sentence)
        output = valhalla_query({
            "inputs": sentence,
        })
        print(output)
        response.append(output[0]['generated_text'])
        # print(output)

    with open(OUTPUT, 'w') as file:
        file.write(' '.join(response))


def main():
    i = 1
    for sentence in txt_to_list(pdf_to_txt(DATA)):
        # if DEBUG:
        print(f'Sentence length: {len(sentence)}')
        if '<hl>' in sentence:
            print('highlighted')
        output = valhalla_query({
            "inputs": sentence,
        })
        print(f'Question {i}:')
        print(output)
        i += 1


if __name__ == "__main__":
    main()
