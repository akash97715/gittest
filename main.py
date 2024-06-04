import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

def plot_vector_distances(query, sentences):
    # Combine query and sentences into one list
    texts = [query] + sentences
    
    # Convert texts to TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Calculate cosine similarities
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Reduce dimensionality using PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(tfidf_matrix.toarray())
    
    # Plot the vectors in 2D space
    plt.figure(figsize=(12, 8))
    plt.scatter(pca_result[:, 0], pca_result[:, 1], color='blue')
    
    # Annotate the points
    labels = ['Query'] + [f'Sentence {i+1}' for i in range(len(sentences))]
    for i, label in enumerate(labels):
        plt.annotate(label, (pca_result[i, 0], pca_result[i, 1]), fontsize=12)
    
    # Draw arrows from the query to each sentence
    query_point = pca_result[0]
    for i in range(1, len(pca_result)):
        plt.arrow(query_point[0], query_point[1], pca_result[i, 0] - query_point[0], pca_result[i, 1] - query_point[1],
                  color='red', alpha=0.5, head_width=0.05, head_length=0.1)
    
    plt.title('2D PCA Plot of Text Vectors')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.grid(True)
    plt.show()

# Example usage
query = "This is a sample query."
sentences = [
    "This is the first sentence.",
    "Here is another sentence.",
    "This sentence is a bit different.",
    "This is a sample query."
]

plot_vector_distances(query, sentences)
