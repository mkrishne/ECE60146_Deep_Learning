# -*- coding: utf-8 -*-
"""HW9_bonus.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19sclnKEby_gxk0fxdEyykoHKfNgLc0X8
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/My Drive/hw9_data

!tar -xvf "/content/drive/My Drive/hw9_data/text_datasets_for_DLStudio.tar.gz" -C "/content/drive/My Drive/hw9_data/"

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

import gensim.downloader as gen_api
import gensim.downloader as genapi
from gensim.models import KeyedVectors

# Custom SentimentAnalysis Dataset
class SentimentAnalysisDataset(torch.utils.data.Dataset):
    def __init__(self, root, dataset_file, mode = 'train', path_to_saved_embeddings=None):
        super(SentimentAnalysisDataset, self).__init__()
        self.path_to_saved_embeddings = path_to_saved_embeddings
        self.mode = mode
        root_dir = root
        f = gzip.open(root_dir + dataset_file, 'rb')
        dataset = f.read()
        if path_to_saved_embeddings is not None:
            if os.path.exists(path_to_saved_embeddings + 'vectors_200.kv'):
                self.word_vectors = KeyedVectors.load(path_to_saved_embeddings + 'vectors_200.kv')
            else:
                self.word_vectors = genapi.load("word2vec-google-news-300")
                ##  'kv' stands for  "KeyedVectors", a special datatype used by gensim because it
                ##  has a smaller footprint than dict
                self.word_vectors.save(path_to_saved_embeddings + 'vectors_200.kv')
        if mode == 'train':
            if sys.version_info[0] == 3:
                self.positive_reviews_train, self.negative_reviews_train, self.vocab = pickle.loads(dataset, encoding='latin1')
            else:
                self.positive_reviews_train, self.negative_reviews_train, self.vocab = pickle.loads(dataset)
            self.categories = sorted(list(self.positive_reviews_train.keys()))
            self.category_sizes_train_pos = {category : len(self.positive_reviews_train[category]) for category in self.categories}
            self.category_sizes_train_neg = {category : len(self.negative_reviews_train[category]) for category in self.categories}
            self.indexed_dataset_train = []
            for category in self.positive_reviews_train:
                for review in self.positive_reviews_train[category]:
                    self.indexed_dataset_train.append([review, category, 1])
            for category in self.negative_reviews_train:
                for review in self.negative_reviews_train[category]:
                    self.indexed_dataset_train.append([review, category, 0])
            random.shuffle(self.indexed_dataset_train)
        elif mode == 'test':
            if sys.version_info[0] == 3:
                self.positive_reviews_test, self.negative_reviews_test, self.vocab = pickle.loads(dataset, encoding='latin1')
            else:
                self.positive_reviews_test, self.negative_reviews_test, self.vocab = pickle.loads(dataset)
            self.vocab = sorted(self.vocab)
            self.categories = sorted(list(self.positive_reviews_test.keys()))
            self.category_sizes_test_pos = {category : len(self.positive_reviews_test[category]) for category in self.categories}
            self.category_sizes_test_neg = {category : len(self.negative_reviews_test[category]) for category in self.categories}
            self.indexed_dataset_test = []
            for category in self.positive_reviews_test:
                for review in self.positive_reviews_test[category]:
                    self.indexed_dataset_test.append([review, category, 1])
            for category in self.negative_reviews_test:
                for review in self.negative_reviews_test[category]:
                    self.indexed_dataset_test.append([review, category, 0])
            random.shuffle(self.indexed_dataset_test)

    def review_to_tensor(self, review):
        list_of_embeddings = []
        for i,word in enumerate(review):
            if word in self.word_vectors.key_to_index:
                embedding = self.word_vectors[word]
                list_of_embeddings.append(np.array(embedding))
            else:
                next
        review_tensor = torch.FloatTensor(list_of_embeddings)
        return review_tensor

    def sentiment_to_tensor(self, sentiment):
        sentiment_tensor = torch.zeros(2)
        if sentiment == 1:
            sentiment_tensor[1] = 1
        elif sentiment == 0:
            sentiment_tensor[0] = 1
        sentiment_tensor = sentiment_tensor.type(torch.long)
        return sentiment_tensor

    def __len__(self):
        if self.mode == 'train':
            return len(self.indexed_dataset_train)
        elif self.mode == 'test':
            return len(self.indexed_dataset_test)

    def __getitem__(self, idx):
        sample = self.indexed_dataset_train[idx] if self.mode == 'train' else self.indexed_dataset_test[idx]
        review = sample[0]
        review_category = sample[1]
        review_sentiment = sample[2]
        review_sentiment = self.sentiment_to_tensor(review_sentiment)
        review_tensor = self.review_to_tensor(review)
        category_index = self.categories.index(review_category)
        sample = {'review'       : review_tensor,
                    'category'     : category_index, # should be converted to tensor, but not yet used
                    'sentiment'    : review_sentiment }
        return sample

# Create custom training dataset
train_dataset_400 = SentimentAnalysisDataset('/content/drive/My Drive/hw9_data/data/','sentiment_dataset_train_400.tar.gz',
                                         path_to_saved_embeddings = '/content/drive/My Drive/hw9_data/data/word2vec/')

len(train_dataset_400)

# Create custom validation dataset
val_dataset_400 = SentimentAnalysisDataset('/content/drive/My Drive/hw9_data/data/', 'sentiment_dataset_test_400.tar.gz',
                                       mode = 'test', path_to_saved_embeddings = '/content/drive/My Drive/hw9_data/data/word2vec/')

len(val_dataset_400)

# Create custom training dataset
train_dataset_200 = SentimentAnalysisDataset('/content/drive/My Drive/hw9_data/data/','sentiment_dataset_train_200.tar.gz',
                                         path_to_saved_embeddings = '/content/drive/My Drive/hw9_data/data/word2vec/')

len(train_dataset_200)

# Create custom validation dataset
val_dataset_200 = SentimentAnalysisDataset('/content/drive/My Drive/hw9_data/data/', 'sentiment_dataset_test_200.tar.gz',
                                       mode = 'test', path_to_saved_embeddings = '/content/drive/My Drive/hw9_data/data/word2vec/')

len(val_dataset_200)

# Create custom training/validation dataloader
train_data_loader = torch.utils.data.DataLoader(train_dataset_200, batch_size=1, shuffle=True, num_workers=1)
val_data_loader = torch.utils.data.DataLoader(val_dataset_200, batch_size=1, shuffle=False, num_workers=1)

# Printing sizes of elements in train_data_loader
print("Sizes of elements in train_data_loader:")
for batch in train_data_loader:
    for key, value in batch.items():
        print(f"Size of {key}: {value.size()}")
    break  # Only print the first batch for brevity

# Printing sizes of elements in val_data_loader
print("\nSizes of elements in val_data_loader:")
for batch in val_data_loader:
    for key, value in batch.items():
        print(f"Size of {key}: {value.size()}")
    break  # Only print the first batch for brevity

import seaborn as sns

# Plotting confusion matrix
def plot_conf_mat(conf_mat, classes, model_name):
    labels = []
    num_classes = len(classes)
    for row in range(num_classes):
        rows = []
        total_labels =  np.sum(conf_mat[row])
        for col in range(num_classes):
            count = conf_mat[row][col]
            percent = "%.2f%%" % (count / total_labels * 100)
            label = str(count) + '\n' + str(percent)
            rows.append(label)
        labels.append(rows)
    labels = np.asarray(labels)

    plt.figure(figsize=(6, 6))
    sns.heatmap(conf_mat, annot=labels, fmt="", cmap="YlOrBr", cbar=True,
                xticklabels=classes, yticklabels=classes)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.title(f'Confusion Matrix for model {model_name}')
    plt.show()

# Commented out IPython magic to ensure Python compatibility.
import torch.nn as nn
import torch.optim as optim
import copy
import time

# Routine to train GRU with embeddings
def train_gru_with_embeddings(device, net, dataloader, model_name, epochs, display_interval):
    #net = copy.deepcopy(net)
    net = net.to(device)

    criterion = nn.NLLLoss()
    accum_times = []
    optimizer = optim.Adam(net.parameters(), lr=1e-3, betas = (0.5, 0.999))
    training_loss_tally = []
    start_time = time.perf_counter()
    for epoch in range(epochs):
        running_loss = 0.0
        for i, data in enumerate(dataloader):
            review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
            review_tensor = review_tensor.to(device)
            sentiment = sentiment.to(device)

            optimizer.zero_grad()
            hidden = net.init_hidden().to(device)
            output, hidden = net(torch.unsqueeze(review_tensor[0], 1), hidden)
            loss = criterion(output, torch.argmax(sentiment, 1))
            running_loss += loss.item()
            loss.backward()
            optimizer.step()

            if (i+1) % display_interval == 0:
                avg_loss = running_loss / float(display_interval)
                training_loss_tally.append(avg_loss)
                current_time = time.perf_counter()
                time_elapsed = current_time-start_time
                print("[epoch:%d  iter:%4d  elapsed_time:%4d secs] loss: %.5f" % (epoch+1,i+1, time_elapsed,avg_loss))
                accum_times.append(current_time-start_time)
                running_loss = 0.0

    # Save model weights
    checkpoint_path = os.path.join('/content/drive/My Drive/hw9_data/saved_models',
                                   f'{model_name}.pt')
    torch.save(net.state_dict(), checkpoint_path)

    print("Total Training Time: {}".format(str(sum(accum_times))))
    print("\nFinished Training\n\n")
    plt.figure(figsize=(10,5))
    plt.title(f"Training Loss vs. Iterations - {model_name}")
    plt.plot(training_loss_tally)
    plt.xlabel("Iterations")
    plt.ylabel("Training loss")
    plt.legend()
    plt.savefig(f"/content/drive/My Drive/hw9_data/training_loss_{model_name}.png")
    plt.show()

    return training_loss_tally

# Routine to validate GRU with embeddings
def validate_gru_with_embeddings(device, net, model_path, dataloader, model_name, display_interval):
    net.load_state_dict(torch.load(model_path))
    net = net.to(device)
    classification_accuracy = 0.0
    negative_total = 0
    positive_total = 0
    confusion_matrix = torch.zeros(2,2)
    with torch.no_grad():
        for i, data in enumerate(dataloader):
            review_tensor,category,sentiment = data['review'], data['category'], data['sentiment']
            review_tensor = review_tensor.to(device)
            sentiment = sentiment.to(device)

            hidden = net.init_hidden().to(device)
            output, hidden = net(torch.unsqueeze(review_tensor[0], 1), hidden)
            predicted_idx = torch.argmax(output).item()
            gt_idx = torch.argmax(sentiment).item()
            if (i+1) % display_interval == 0:
                print("   [i=%d]    predicted_label=%d       gt_label=%d" % (i+1, predicted_idx,gt_idx))
            if predicted_idx == gt_idx:
                classification_accuracy += 1
            if gt_idx == 0:
                negative_total += 1
            elif gt_idx == 1:
                positive_total += 1
            confusion_matrix[gt_idx,predicted_idx] += 1
    print("\nOverall classification accuracy: %0.2f%%" %  (float(classification_accuracy) * 100 /float(i)))
    out_percent = np.zeros((2,2), dtype='float')
    out_percent[0,0] = "%.3f" % (100 * confusion_matrix[0,0] / float(negative_total))
    out_percent[0,1] = "%.3f" % (100 * confusion_matrix[0,1] / float(negative_total))
    out_percent[1,0] = "%.3f" % (100 * confusion_matrix[1,0] / float(positive_total))
    out_percent[1,1] = "%.3f" % (100 * confusion_matrix[1,1] / float(positive_total))
    print("\n\nNumber of positive reviews tested: %d" % positive_total)
    print("\n\nNumber of negative reviews tested: %d" % negative_total)
    print("\n\nDisplaying the confusion matrix:\n")
    out_str = "                      "
    out_str +=  "%18s    %18s" % ('predicted negative', 'predicted positive')
    print(out_str + "\n")
    for i,label in enumerate(['true negative', 'true positive']):
        out_str = "%12s:  " % label
        for j in range(2):
            out_str +=  "%18s%%" % out_percent[i,j]
        print(out_str)

    plot_conf_mat(confusion_matrix.numpy(), ['negative_reviews', 'positive_reviews'], model_name)

import numpy as np
import matplotlib.pyplot as plt

def plot_loss(mean_losses, display_interval, model_name):
    """
    Plot training loss.

    Parameters:
        mean_losses (list): List of mean losses over each display interval.
        display_interval (int): Interval at which losses are recorded.
        model_name (str): Name of the model for which the loss is being plotted.
    """
    iterations = np.arange(len(mean_losses)) * display_interval
    plt.figure()
    plt.plot(iterations, mean_losses, label="Training Loss")
    plt.title(f'Training Loss for {model_name}')
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

# torch.nn GRU with Embeddings
class GRUnetWithEmbeddings(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1):
        super(GRUnetWithEmbeddings, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers)
        self.fc = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
        self.logsoftmax = nn.LogSoftmax(dim=1)

    def forward(self, x, h):
        out, h = self.gru(x, h)
        out = self.fc(self.relu(out[-1]))
        out = self.logsoftmax(out)
        return out, h

    def init_hidden(self):
        weight = next(self.parameters()).data
        #                  num_layers  batch_size    hidden_size
        hidden = weight.new(  2,          1,         self.hidden_size    ).zero_()
        return hidden

import torch

# Initialize device
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
print(f"Device: {device}")

# Initialize torch.nn GRU with Embeddings
model = GRUnetWithEmbeddings(input_size=300, hidden_size=100, output_size=2, num_layers=2)

# Uncomment the following line if you want to load model weights from a file
# model.load_state_dict(torch.load('/content/drive/My Drive/hw9_data/saved_models/HW9_bonus_200.pt'))

epochs = 5
display_interval = 500

# Count the number of learnable parameters
number_of_learnable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print("\nThe number of learnable parameters in the model:", number_of_learnable_params)

# Count the number of layers
num_layers = len(list(model.parameters()))
print("\nThe number of layers in the model:", num_layers)

# Train nnGRU
net1_losses = train_gru_with_embeddings(device, model, dataloader=train_data_loader,
                                        model_name='HW9_bonus_200', epochs=epochs, display_interval=display_interval)

# Validate nnGRU
save_path = '/content/drive/My Drive/hw9_data/saved_models/HW9_bonus_200.pt'
validate_gru_with_embeddings(device, model, dataloader=val_data_loader,
                             display_interval=display_interval, model_path=save_path, model_name='HW9_bonus_200.pt')

import torch

# Initialize device
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
print(f"Device: {device}")

# Initialize torch.nn GRU with Embeddings
model = GRUnetWithEmbeddings(input_size=300, hidden_size=100, output_size=2, num_layers=2)

# Uncomment the following line if you want to load model weights from a file
# model.load_state_dict(torch.load('/content/drive/My Drive/hw9_data/saved_models/HW9_bonus_400.pt'))

epochs = 5
display_interval = 500

# Count the number of learnable parameters
number_of_learnable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print("\nThe number of learnable parameters in the model:", number_of_learnable_params)

# Count the number of layers
num_layers = len(list(model.parameters()))
print("\nThe number of layers in the model:", num_layers)

# Train nnGRU
net1_losses = train_gru_with_embeddings(device, model, dataloader=train_data_loader,
                                        model_name='HW9_bonus_400', epochs=epochs, display_interval=display_interval)

# Validate nnGRU
save_path = '/content/drive/My Drive/hw9_data/saved_models/HW9_bonus_400.pt'
validate_gru_with_embeddings(device, model, dataloader=val_data_loader,
                             display_interval=display_interval, model_path=save_path, model_name='HW9_bonus_400.pt')

# Bidirectional torch.nn GRU with Embeddings
class BiGRUnetWithEmbeddings(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1):
        super(BiGRUnetWithEmbeddings, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers, bidirectional=True)
        self.fc = nn.Linear(2*hidden_size, output_size)
        self.relu = nn.ReLU()
        self.logsoftmax = nn.LogSoftmax(dim=1)

    def forward(self, x, h):
        out, h = self.gru(x, h)
        out = self.fc(self.relu(out[-1]))
        out = self.logsoftmax(out)
        return out, h

    def init_hidden(self):
        weight = next(self.parameters()).data
        #                  num_layers  batch_size    hidden_size
        hidden = weight.new(  2*2,          1,         self.hidden_size    ).zero_()
        return hidden

import torch

# Initialize device
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
print(f"Device: {device}")

# Initialize torch.nn GRU with Embeddings
model = BiGRUnetWithEmbeddings(input_size=300, hidden_size=100, output_size=2, num_layers=2)

# Uncomment the following line if you want to load model weights from a file
# model.load_state_dict(torch.load('/content/drive/My Drive/hw9_data/saved_models/HW9_bonus_bi400.pt'))

epochs = 5
display_interval = 500

# Count the number of learnable parameters
number_of_learnable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print("\nThe number of learnable parameters in the model:", number_of_learnable_params)

# Count the number of layers
num_layers = len(list(model.parameters()))
print("\nThe number of layers in the model:", num_layers)

# Train nnGRU
net1_losses = train_gru_with_embeddings(device, model, dataloader=train_data_loader,
                                        model_name='HW9_bonus_bi400', epochs=epochs, display_interval=display_interval)

# Validate nnGRU
save_path = '/content/drive/My Drive/hw9_data/saved_models/HW9_bonus_bi400.pt'
validate_gru_with_embeddings(device, model, dataloader=val_data_loader,
                             display_interval=display_interval, model_path=save_path, model_name='HW9_bonus_bi400.pt')

import torch

# Initialize device
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
print(f"Device: {device}")

# Initialize torch.nn GRU with Embeddings
model = BiGRUnetWithEmbeddings(input_size=300, hidden_size=100, output_size=2, num_layers=2)

# Uncomment the following line if you want to load model weights from a file
# model.load_state_dict(torch.load('/content/drive/My Drive/hw9_data/saved_models/HW9_bonus_bi200.pt'))

epochs = 5
display_interval = 500

# Count the number of learnable parameters
number_of_learnable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print("\nThe number of learnable parameters in the model:", number_of_learnable_params)

# Count the number of layers
num_layers = len(list(model.parameters()))
print("\nThe number of layers in the model:", num_layers)

# Train nnGRU
net1_losses = train_gru_with_embeddings(device, model, dataloader=train_data_loader,
                                        model_name='HW9_bonus_bi200', epochs=epochs, display_interval=display_interval)

# Validate nnGRU
save_path = '/content/drive/My Drive/hw9_data/saved_models/HW9_bonus_bi200.pt'
validate_gru_with_embeddings(device, model, dataloader=val_data_loader,
                             display_interval=display_interval, model_path=save_path, model_name='HW9_bonus_bi200.pt')