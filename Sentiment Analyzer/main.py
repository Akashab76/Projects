

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
import random
import string
from nltk.corpus import movie_reviews, stopwords
from nltk.classify import NaiveBayesClassifier
from nltk.classify.util import accuracy
from nltk.tokenize import word_tokenize

# Download NLTK resources
nltk.download('movie_reviews')
nltk.download('punkt')
nltk.download('stopwords')

# Preparing stopwords and punctuation
stop_words = set(stopwords.words('english'))
punctuation = set(string.punctuation)

# Load dataset
documents = [
    (list(movie_reviews.words(fileid)), category)
    for category in movie_reviews.categories()
    for fileid in movie_reviews.fileids(category)
]

# Shuffle for randomness
random.shuffle(documents)

# Feature extractor
def extract_features(words):
    cleaned_words = [
        word.lower() for word in words
        if word.lower() not in stop_words and word not in punctuation
    ]
    return {word: True for word in cleaned_words}

# Build feature sets
feature_sets = [(extract_features(doc), label) for (doc, label) in documents]

# Train/test split
split_index = int(len(feature_sets) * 0.8)
train_set, test_set = feature_sets[:split_index], feature_sets[split_index:]

# Train classifier
classifier = NaiveBayesClassifier.train(train_set)

# Accuracy
print(f"\nAccuracy: {accuracy(classifier, test_set) * 100:.2f}%")

# Most informative features
print("\nMost Informative Features:")
classifier.show_most_informative_features(10)

# --- Neutral Words Analysis ---
all_features = set(
    key[1] for key in classifier._feature_probdist.keys()
    if key[0] in ('pos', 'neg')
)

neutral_features = []
for feature in all_features:
    if feature in stop_words or feature in punctuation:
        continue

    try:
        prob_pos = classifier._feature_probdist[('pos', feature)].prob(True)
        prob_neg = classifier._feature_probdist[('neg', feature)].prob(True)

        if prob_pos == 0 or prob_neg == 0:
            continue

        ratio = prob_pos / prob_neg
        if 0.75 <= ratio <= 1.33:  # roughly balanced
            neutral_features.append((feature, prob_pos, prob_neg))
    except KeyError:
        continue

neutral_features.sort(key=lambda x: abs((x[1] / x[2]) - 1))

print("\nTop Neutral-Looking Words (pos:neg ≈ 1:1):")
for feature, prob_pos, prob_neg in neutral_features[:10]:
    print(f"{feature} → pos: {prob_pos:.3f}, neg: {prob_neg:.3f}, ratio: {prob_pos/prob_neg:.2f}")

# --- Sentiment Prediction ---
def predict_sentiment(text):
    words = word_tokenize(text.lower())
    features = extract_features(words)
    return classifier.classify(features)

# Test predictions
print("\nSample Predictions:")
print("Review: 'I loved the movie!' →", predict_sentiment("I loved the movie!"))
print("Review: 'It was boring and slow.' →", predict_sentiment("It was boring and slow."))
print("Review: 'The movie was about two hours long.' →", predict_sentiment("The movie was about two hours long."))

