import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def plot_detailed_cosine_similarity(query, sentences):
    # Combine query and sentences into one list
    texts = [query] + sentences
    
    # Convert texts to TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Calculate cosine similarities
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Plot the similarities with detailed visualization
    plt.figure(figsize=(12, 8))
    sentence_indices = np.arange(1, len(sentences) + 1)
    bar_colors = plt.cm.viridis(cosine_similarities)
    
    bars = plt.bar(sentence_indices, cosine_similarities, color=bar_colors)
    plt.colorbar(plt.cm.ScalarMappable(cmap='viridis'), label='Cosine Similarity')
    
    plt.xlabel('Sentence Index')
    plt.ylabel('Cosine Similarity')
    plt.title('Cosine Similarity between Query and Sentences')
    plt.xticks(sentence_indices, [f'Sentence {i}' for i in sentence_indices])
    plt.ylim(0, 1)
    
    # Add text annotations to display similarity values
    for bar, similarity in zip(bars, cosine_similarities):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, round(similarity, 2), ha='center', va='bottom')
    
    plt.show()

# Example usage
query = "This is a sample query."
sentences = [
    "This is the first sentence.",
    "Here is another sentence.",
    "This sentence is a bit different.",
    "This is a sample query."
]

plot_detailed_cosine_similarity(query, sentences)
