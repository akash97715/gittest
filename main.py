import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def plot_cosine_similarity(query, sentences):
    # Combine query and sentences into one list
    texts = [query] + sentences
    
    # Convert texts to TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Calculate cosine similarities
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Plot the similarities
    plt.figure(figsize=(10, 6))
    sentence_indices = range(1, len(sentences) + 1)
    plt.bar(sentence_indices, cosine_similarities, color='blue')
    plt.xlabel('Sentence Index')
    plt.ylabel('Cosine Similarity')
    plt.title('Cosine Similarity between Query and Sentences')
    plt.xticks(sentence_indices, [f'Sentence {i}' for i in sentence_indices])
    plt.ylim(0, 1)
    plt.show()

# Example usage
query = "This is a sample query."
sentences = [
    "This is the first sentence.",
    "Here is another sentence.",
    "This sentence is a bit different.",
    "This is a sample query."
]

plot_cosine_similarity(query, sentences)
