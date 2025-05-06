import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
import pickle
from torch.utils.data import DataLoader, Dataset
import os
from backbone.WideResNet import WideResNet

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = WideResNet(num_classes=2).to(device)

alpha = 0.75

# Datq Agumentation And MixUp
def sharpen(x, T):
    temp = x**(1/T)
    return temp / temp.sum(axis=1, keepdims=True)

def mixup(x1, x2, y1, y2, alpha):
    beta = np.random.beta(alpha, alpha)
    x = beta * x1 + (1 - beta) * x2
    y = beta * y1 + (1 - beta) * y2
    return x, y

# Load Pretrained Model
with open('ctgan_model.pkl', 'rb') as f:
    ctgan = pickle.load(f)

def augment_with_ctgan(ctgan, num_samples):
    synthetic_data = ctgan.sample(num_samples)
    synthetic_data = synthetic_data.values.astype(np.float32)
    return synthetic_data

def guess_labels_with_ctgan(model, unlabelled_data, num_augments=2, T=0.5):
    all_augments = []
    for data in unlabelled_data:
        augmented_data = augment_with_ctgan(ctgan, num_augments)
        all_augments.append(augmented_data)
        
    predictions = []
    for augmented_data in all_augments:
        pred = []
        for data_row in augmented_data:
            tensor_data = torch.tensor(data_row, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device)
            pred.append(model(tensor_data))
        pred = torch.stack(pred).mean(dim=0)
        predictions.append(pred)
    
    avg_predictions = torch.stack(predictions)
    return sharpen(avg_predictions, T)

def mas(train_data, train_labels, unlabelled_data, model, alpha, num_augments=2, T=0.5):
    guessed_labels = guess_labels_with_ctgan(model, unlabelled_data, num_augments, T)
    
    num_classes = train_labels.max().item() + 1
    train_labels_one_hot = np.eye(num_classes)[train_labels.cpu().numpy()]
    guessed_labels = guessed_labels.detach().cpu().numpy()
    
    data_length = min(len(train_data), len(unlabelled_data))
    
    mixed_data = []
    mixed_labels = []
    mixed_labels_int = []

    for i in range(data_length):
        x1, y1 = train_data[i].cpu().numpy(), train_labels_one_hot[i]
        x2, y2 = unlabelled_data[i].cpu().numpy(), guessed_labels[i]
        
        mixed_x, mixed_y = mixup(x1, x2, y1, y2, alpha)
        mixed_data.append(mixed_x)
        mixed_labels.append(mixed_y)
        mixed_labels_int.append(np.argmax(mixed_y))
    
    mixed_data = np.array(mixed_data)
    mixed_labels_int = np.array(mixed_labels_int)
    
    mixed_data = torch.tensor(mixed_data, dtype=torch.float32).to(device)
    mixed_labels_int = torch.tensor(mixed_labels_int, dtype=torch.int64).to(device)
    
    return mixed_data, mixed_labels_int