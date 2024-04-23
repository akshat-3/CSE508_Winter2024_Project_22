from PIL import Image, ImageEnhance

import pandas as pd
import copy


import torch
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from nltk.stem import PorterStemmer

import numpy as np
from transformers import AutoProcessor, CLIPModel
from sentence_transformers import SentenceTransformer



TextModel = SentenceTransformer('bert-base-nli-mean-tokens')


nltk.download('punkt', quiet = True)
nltk.download('stopwords', quiet = True)


device = torch.device('cuda' if torch.cuda.is_available() else "cpu")
processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
ImageModel = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)

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
def extract_image_features(image):
   with torch.no_grad():
      inputs = processor(images=image, return_tensors="pt").to(device)
      image_features = ImageModel.get_image_features(**inputs)
   print("DONE")
   return image_features.tolist()[0]



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


  return " ".join(sent)


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


def get_top_k_recommendations(input_text, product_dict_input, k = 10):
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
   
   text_embeddings = {}

   processed_input = preprocess_text(input_text)


   for i in product_dict:
      text_embeddings[i] = [list(TextModel.encode(product_dict[i][0])), list(TextModel.encode(product_dict[i][1]))]
   image_embeddings = {}

   for i in product_dict:
      image_embeddings[i] = extract_image_features(product_dict[i][2])

   input_embedding = TextModel.encode(processed_input)

   max_cosine_sim = -100
   max_index = 0
   for i in product_dict:
      cosine_sim = get_cosine_similarity(input_embedding, text_embeddings[i][0])
      if cosine_sim > max_cosine_sim:
         max_cosine_sim = cosine_sim
         max_index = i
    
   cosine_sims_with_input = {}
   for i in product_dict:
      if i != max_index:
         image_sim = get_cosine_similarity(image_embeddings[max_index], image_embeddings[i])
         title_sim = get_cosine_similarity(text_embeddings[max_index][0], text_embeddings[i][0])
         description_sim = get_cosine_similarity(text_embeddings[max_index][1], text_embeddings[i][1])
         cosine_sims_with_input[i] = 0.8*image_sim + 0.2*description_sim + 0.3*title_sim
   
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
