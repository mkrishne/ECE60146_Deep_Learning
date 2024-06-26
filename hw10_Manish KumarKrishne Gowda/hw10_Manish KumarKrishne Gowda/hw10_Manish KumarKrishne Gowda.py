# -*- coding: utf-8 -*-
"""HW10.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lVnannhndbc2VgJn-6pElo3ap2xhvfkJ
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %cd "/content/drive/My Drive/hw10_data"

pip install 'transformers[torch]'

pip install accelerate -U

pip install transformers

pip install datasets

import os
import torch
import random
import numpy as np
import requests
import matplotlib.pyplot as plt
import sys

from tqdm import tqdm
import gzip
import pickle

seed = 0
random.seed(seed)
np.random.seed(seed)

import pickle

# Load training, testing, and evaluation dictionaries from pickle files
with open('/content/drive/My Drive/hw10_data/dataset/train_dict.pkl', 'rb') as f:
    train_dict = pickle.load(f)

with open('/content/drive/My Drive/hw10_data/dataset/test_dict.pkl', 'rb') as f:
    test_dict = pickle.load(f)

with open('/content/drive/My Drive/hw10_data/dataset/eval_dict.pkl', 'rb') as f:
    eval_dict = pickle.load(f)

# Load processed training, testing, and evaluation data from pickle files
with open('/content/drive/My Drive/hw10_data/dataset/train_data_processed.pkl', 'rb') as f:
    train_processed = pickle.load(f)

with open('/content/drive/My Drive/hw10_data/dataset/test_data_processed.pkl', 'rb') as f:
    test_processed = pickle.load(f)

with open('/content/drive/My Drive/hw10_data/dataset/eval_data_processed.pkl', 'rb') as f:
    eval_processed = pickle.load(f)

# Print keys of dictionaries and processed data to verify loading
print(train_dict.keys())
print(test_dict.keys())
print(eval_dict.keys())

print(train_processed.keys())
print(test_processed.keys())
print(eval_processed.keys())

# Sample values of the dictionaries
print("Sample values of train_dict:")
sample_train = {key: list(train_dict[key])[0] for key in train_dict.keys()}
for key, value in sample_train.items():
    print(key)
    print(value)

print()
print("\nSample values of test_dict:")
sample_test = {key: list(test_dict[key])[0] for key in test_dict.keys()}
for key, value in sample_test.items():
    print(key)
    print(value)

print()
print("\nSample values of eval_dict:")
sample_eval = {key: list(eval_dict[key])[0] for key in eval_dict.keys()}
for key, value in sample_eval.items():
    print(key)
    print(value)

print()
print("\nSample values of train_processed:")
sample_train_processed = {key: list(train_processed[key])[0] for key in train_processed.keys()}
for key, value in sample_train_processed.items():
    print(key)
    print(value)

print()
print("\nSample values of test_processed:")
sample_test_processed = {key: list(test_processed[key])[0] for key in test_processed.keys()}
for key, value in sample_test_processed.items():
    print(key)
    print(value)

print()
print("\nSample values of eval_processed:")
sample_eval_processed = {key: list(eval_processed[key])[0] for key in eval_processed.keys()}
for key, value in sample_eval_processed.items():
    print(key)
    print(value)

#First, initialize a model. We use BertForQuestionAnswering to initialise the model
from transformers import BertForQuestionAnswering

model_name = 'bert-base-uncased'
model = BertForQuestionAnswering.from_pretrained(model_name)
print(model._modules)

from transformers import TrainingArguments
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'

training_args = TrainingArguments(
    output_dir='/content/drive/My Drive/hw10_data/results',  # output directory
    num_train_epochs=5,  # total number of training epochs, change this as you need
    per_device_train_batch_size=8,  # batch size per device during training, change this as you need
    per_device_eval_batch_size=8,  # batch size for evaluation, change this as you need
    weight_decay=0.01,  # strength of weight decay
    logging_dir='/content/drive/My Drive/hw10_data/logs'  # directory for storing logs
)

from transformers import Trainer
from datasets import Dataset
import pandas as pd

train_dataset = Dataset.from_pandas(pd.DataFrame(train_processed))
eval_dataset = Dataset.from_pandas(pd.DataFrame(eval_processed))
test_dataset = Dataset.from_pandas(pd.DataFrame(test_processed))
model.to(device)

trainer = Trainer(
    model=model,  # the instantiated Transformers model to be fine-tuned
    args=training_args,  # training arguments, defined above
    train_dataset=train_dataset,  # training dataset
    eval_dataset=eval_dataset,  # evaluation dataset
)
train_result = trainer.train()

import matplotlib.pyplot as plt

# Get the training loss values
train_losses = train_result.loss

# Plot the loss curve
plt.plot(train_losses, label='Training Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training Loss Curve')
plt.legend()
plt.show()

import numpy as np
from transformers import BertTokenizer


# Perform predictions on the test dataset
predictions = trainer.predict(test_dataset)

# Get predicted start and end positions
start_pos, end_pos = predictions.predictions
start_pos = np.argmax(start_pos, axis=1)
end_pos = np.argmax(end_pos, axis=1)

# Get tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # Replace 'bert-base-uncased' with your desired model

# Iterate over the first 10 samples in the test dataset
for k in range(10):
    # Get tokens for the input_ids of the k-th sample
    tokens = tokenizer.convert_ids_to_tokens(test_dataset['input_ids'][k])

    # Extract predicted answer span
    i, j = start_pos[k], end_pos[k]

    predicted_answer = tokenizer.convert_tokens_to_string(tokens[i:j+1])
    # Print question, predicted answer, and correct answer
    print('Question:', test_dict['question'][k])
    print('Predicted Answer:', predicted_answer)
    print('Correct Answer:', test_dict['answers'][k]['text'][0].lower())
    print('---')

def f1_score(prediction, truth):
    pred_tokens = prediction.split()
    truth_tokens = truth.split()
    # If either the prediction or the truth is no-answer then f1 = 1 if they agree, 0 otherwise
    if len(pred_tokens) == 0 or len(truth_tokens) == 0:
        return int(pred_tokens == truth_tokens)

    common_tokens = set(pred_tokens) & set(truth_tokens)
    # If there are no common tokens then f1 = 0
    if len(common_tokens) == 0:
        return 0

    prec = len(common_tokens) / len(pred_tokens)
    rec = len(common_tokens) / len(truth_tokens)

    return 2 * (prec * rec) / (prec + rec)

def compute_exact_match ( prediction , truth ):
    return int( prediction == truth )

from tqdm import tqdm

# Lists to store F1 scores and exact match scores
f1_scores = []
em_scores = []

# Iterate over the test dataset with progress tracking
for k in tqdm(range(len(test_dataset)), desc="Calculating scores"):
    # Get tokens for the input_ids of the k-th sample
    tokens = tokenizer.convert_ids_to_tokens(test_dataset['input_ids'][k])
    # Extract predicted answer span
    i, j = start_pos[k], end_pos[k]
    # Convert predicted answer tokens to string
    prediction = tokenizer.convert_tokens_to_string(tokens[i:j+1])
    # Get ground truth answer
    truth = test_dict['answers'][k]['text'][0].lower()
    # Calculate F1 score and exact match score
    f1_scores.append(f1_score(prediction, truth))
    em_scores.append(compute_exact_match(prediction, truth))

print("Test dataset length :",len(test_dataset))
# Calculate average and median F1-scores
average_f1 = sum(f1_scores) / len(f1_scores)
median_f1 = np.median(f1_scores)
print("Average F1-score:", average_f1)
print("Median F1-score:", median_f1)

# Calculate average and median EM-scores
average_em = sum(em_scores) / len(em_scores)
median_em = np.median(em_scores)
print("Average EM-score:", average_em)
print("Median EM-score:", median_em)
print("total matches :",sum(em_scores))

from tqdm import tqdm
from transformers import pipeline

# Instantiate the question answering pipeline
question_answerer = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')

# Iterate over the first 10 samples in the test dataset
for k in range(10):
    # Get question
    question = test_dict['question'][k]

    # Get context (assuming you have a 'context' field in your test_dict)
    context = test_dict['context'][k]

    # Perform question answering
    prediction = question_answerer(question=question, context=context)

    # Print question and predicted answer
    print('Question:', question)
    print('Predicted Answer:', prediction['answer'])
    print('Correct Answer:', test_dict['answers'][k]['text'][0])

    print('---')

# Lists to store F1 scores and exact match scores
f1_scores_pipeline = []
em_scores_pipeline = []

# Iterate over the questions in the test dataset with progress tracking
for i in tqdm(range(len(test_dict['question'])), desc="Processing questions"):
    # Get answer using the pipeline
    result = question_answerer(question=test_dict['question'][i], context=test_dict['context'][i])
    predicted_answer = result['answer']

    # Get ground truth answer
    truth = test_dict['answers'][i]['text'][0]

    # Calculate F1-score
    f1_scores_pipeline.append(f1_score(predicted_answer, truth))

    # Calculate EM-score
    em_scores_pipeline.append(compute_exact_match(predicted_answer, truth))

from transformers import pipeline

# Initialize question answering pipeline
question_answerer = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')

# Iterate over the first 10 samples in the test dataset
for k in range(10):
    # Get question
    question = test_dict['question'][k]

    # Get context (assuming you have a 'context' field in your test_dict)
    context = test_dict['context'][k]

    # Perform question answering
    prediction = question_answerer(question=question, context=context)

    # Print question and predicted answer
    print('Question:', question)
    print('Predicted Answer:', prediction['answer'])
    print('---')

# Calculate average and median F1-scores
average_f1_pipeline = sum(f1_scores_pipeline) / len(f1_scores_pipeline)
median_f1_pipeline = np.median(f1_scores_pipeline)

print("Average F1-score using distilbert-base-cased-distilled-squad model:", average_f1_pipeline)
print("Median F1-score using distilbert-base-cased-distilled-squad model:", median_f1_pipeline)

# Calculate average and median F1-scores
average_em_pipeline = sum(em_scores_pipeline) / len(em_scores_pipeline)
median_em_pipeline = np.median(em_scores_pipeline)

print("Average EM-score using distilbert-base-cased-distilled-squad model:", average_em_pipeline)
print("Median EM-score using distilbert-base-cased-distilled-squad model:", median_em_pipeline)
print("Total matches",sum(em_scores_pipeline))