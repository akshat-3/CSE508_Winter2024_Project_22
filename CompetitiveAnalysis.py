from PIL import Image, ImageOps, ImageEnhance
import ast

import pandas as pd
import random
import pickle
import copy
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.autograd import Variable

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from nltk.stem import PorterStemmer

import numpy as np

import math



nltk.download('punkt', quiet = True)
nltk.download('stopwords', quiet = True)


# preprocessing the image
def preprocess_image(image):
  image = image.resize((256, 256))
  image = image.rotate(45)
  image = image.transpose(Image.FLIP_LEFT_RIGHT)
  enhancer = ImageEnhance.Contrast(image)
  image = enhancer.enhance(2.0)
  enhancer = ImageEnhance.Brightness(image)
  image = enhancer.enhance(1.5)
  return image

# Extracting image features
def extract_image_features(model, image):
  scaler = transforms.Resize((224, 224))
  normalize = transforms.Normalize(mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])
  to_tensor = transforms.ToTensor()
  img_transformed = Variable(normalize(to_tensor(scaler(image))).unsqueeze(0))

  layer = model._modules.get('avgpool')
  model.eval()

  img_embedding = torch.zeros(1, 512, 1, 1)

  def copy_embedding(m, i, o):
    img_embedding.copy_(o.data)

  h = layer.register_forward_hook(copy_embedding)
  model(img_transformed)
  h.remove()
  output = img_embedding.squeeze()
  output /= torch.linalg.vector_norm(output)
  print("DONE")
  return output.tolist()



# Preprocessing text


def preprocess_text(sent):
  stwords = set(stopwords.words('english'))
  puncts = string.punctuation
  sent = sent.lower()
  sent  = word_tokenize(sent)

  temp = []
  for j in sent:
    if j not in stwords:
      temp.append(j)
  sent = temp.copy()

  temp = []
  for j in sent:
    new_tok = ""
    for k in j:
      if k not in puncts:
        new_tok += k
    temp.append(new_tok)
  sent = temp.copy()


  ps = PorterStemmer()
  temp = []
  for word in sent:
    temp.append(ps.stem(word))
  sent = temp.copy()


  temp = []
  for j in sent:
    flag = True
    for k in j:
      if k != " ":
        flag = False
        break
    if not flag:
      if j == "":
        continue
      temp.append(j)
  sent = temp.copy()

  return sent


def get_tf_idf(input_text, idf_counts, total_vocab):
   tf_idf_vector = []

   input_tf = {}

   for word in input_text:
      if word not in input_tf:
         input_tf[word] = 0
      input_tf[word] += 1
   for word in total_vocab:
      if word not in input_tf:
         tf_idf_vector.append(0)
      else:
         tf_idf_vector.append((input_tf[word] / len(input_tf))*(math.log2(len(total_vocab) / idf_counts[word])))
    
   return tf_idf_vector 

def get_total_vocab(product_dict):
   total_vocab = []

   for i in product_dict:
      name = product_dict[i][0]
      description = product_dict[i][1]

      for word in name:
         if word not in total_vocab:
            total_vocab.append(word)
      
      for word in description:
         if word not in total_vocab:
            total_vocab.append(word)
   return total_vocab

def get_idf_scores(product_dict):
   idf_counts = {}
   

   for i in product_dict:
    name = product_dict[i][0]
    description = product_dict[i][1]
    for word in name:
         if word not in idf_counts:
            idf_counts[word] = []
         
         if i not in idf_counts[word]:
            idf_counts[word].append(i)
    for word in description:
         if word not in idf_counts:
            idf_counts[word] = []
         
         if i not in idf_counts[word]:
            idf_counts[word].append(i)
    
   final_idf = {}
   for i in idf_counts:
      final_idf[i] = len(idf_counts[i])
   return final_idf

def get_cosine_similarity(vec1, vec2):
   np1 = np.array(vec1)
   np2 = np.array(vec2)
   
   out = np.dot(np1, np2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
   if out == np.nan:
      print(np1)
      print(np2)
      print(vec1)
      print(vec2)
   return out


def get_top_k_recommendations(input_text, product_dict_input, k = 3):
   product_dict = copy.deepcopy(product_dict_input)
   invalid = []
   for i in product_dict:
      try:
         product_dict[i][0] = preprocess_text(product_dict[i][0])
         product_dict[i][1] = preprocess_text(product_dict[i][1])
         product_dict[i][2] = preprocess_image(product_dict[i][2])
      except:
         invalid.append(i)
   for i in invalid:
      del product_dict[i]
   

   idf_scores = get_idf_scores(product_dict)
   
   total_vocab = get_total_vocab(product_dict)
   tf_idf_vectors = {}

   processed_input = preprocess_text(input_text)

   for i in product_dict:
      tf_idf_vectors[i] = [get_tf_idf(product_dict[i][0], idf_scores, total_vocab), get_tf_idf(product_dict[i][1], idf_scores, total_vocab)]
   
   model = models.resnet18(pretrained=True)

   image_embeddings = {}

   for i in product_dict:
      image_embeddings[i] = extract_image_features(model, product_dict[i][2])
   
   cosine_similarity_text = {}

   input_tf_idf = get_tf_idf(processed_input, idf_scores, total_vocab)

   max_cosine_sim = -100
   max_index = 0
   for i in product_dict:
      cosine_sim = get_cosine_similarity(input_tf_idf, tf_idf_vectors[i][0])
      if cosine_sim > max_cosine_sim:
         max_cosine_sim = cosine_sim
         max_index = i
    
   cosine_sims_with_input = {}
   for i in product_dict:
      if i != max_index:
         image_sim = get_cosine_similarity(image_embeddings[max_index], image_embeddings[i])
         title_sim = get_cosine_similarity(tf_idf_vectors[max_index][0], tf_idf_vectors[i][0])
         description_sim = get_cosine_similarity(tf_idf_vectors[max_index][1], tf_idf_vectors[i][1])
         cosine_sims_with_input[i] = 0.7*image_sim + 0.5*description_sim + 0.2*title_sim
   
   #normalize the cosine similarity
   max_cosine_sim = max(cosine_sims_with_input.values())
   for i in cosine_sims_with_input:
      cosine_sims_with_input[i] /= max_cosine_sim
         
   
   sorted_sims = dict(sorted(cosine_sims_with_input.items(), key=lambda x: x[1], reverse=True))

   top_k_dict = {}
   count = 0
   for i in sorted_sims:
      if count >= k:
         break
      top_k_dict[i] = sorted_sims[i]
      count += 1
   return max_index, top_k_dict
