from PIL import ImageOps
import numpy as np
import copy
from rouge_score import rouge_scorer
from image_similarity_measures.quality_metrics import rmse
from sklearn.metrics import classification_report


scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)

def get_image_pixels(img):
    img = ImageOps.grayscale(img)
    img = img.resize((220, 220))
    return np.array(img)


def get_image_sim(img1, img2):

    img1_array = get_image_pixels(img1)
    img2_array = get_image_pixels(img2)
    return rmse(org_img=np.array(img1_array), pred_img=np.array(img2_array))


def get_rouge_score(text1, text2):
    return scorer.score(text1, text2)["rouge1"][2]




def get_vader_label(vader_score):
    if vader_score >= 0.25:
        return 2
    elif vader_score >= -0.25:
        return 1
    return 0

def get_star_rating_label(star_rating):
    if star_rating > 3:
        return 2
    elif star_rating >= 2:
        return 1
    return 0

def evaluate_sentiment(vader_sentiments, star_ratings):
    # Classes: 2 -> Positive, 1-> Neutral, 0 -> Negative
    predictions = []
    labels = []

    for i in vader_sentiments:
        predictions.append(get_vader_label(vader_sentiments[i]))
        labels.append(get_star_rating_label(star_ratings[i]))
    print("Evaluating sentiment scores")    
    print(classification_report(labels, predictions))
        

def evaluate_similarity(product_dict, top_product_ids, input_id):

    similarity_scores = {}

    inp_product = product_dict[input_id]

    other_products = copy.deepcopy(product_dict)
    del other_products[input_id]

    for i in other_products:
        text_similarity = get_rouge_score(inp_product[1], other_products[i][1])
        img_error = get_image_sim(inp_product[2], other_products[i][2])
        similarity_scores[i] = text_similarity / (img_error + 1e-10) # Small value to avoid division by zero
    
    top_k = dict(sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True))
    count = 0
    similar_values = 0
    for i in top_k:
        if count >= len(top_product_ids):
            break
        if i in top_product_ids:
            similar_values += 1
        count += 1
    
    print("Number of common values: ", similar_values)
