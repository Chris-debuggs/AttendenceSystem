#!/usr/bin/env python3
"""
Test script to verify face similarity detection
This script helps debug face recognition issues
"""

import numpy as np
from database import get_all_face_embeddings

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    norm_a = a / np.linalg.norm(a)
    norm_b = b / np.linalg.norm(b)
    return np.dot(norm_a, norm_b)

def test_face_similarities():
    """Test face similarities between all registered faces"""
    print("=== Face Similarity Test ===")
    
    # Get all face embeddings
    embeddings = get_all_face_embeddings()
    
    if not embeddings:
        print("No face embeddings found in database")
        return
    
    names = list(embeddings.keys())
    embedding_list = list(embeddings.values())
    
    print(f"Found {len(names)} registered faces: {names}")
    print("\n=== Similarity Matrix ===")
    
    # Create similarity matrix
    for i, name1 in enumerate(names):
        for j, name2 in enumerate(names):
            if i <= j:  # Only show upper triangle to avoid duplicates
                if i == j:
                    similarity = 1.0  # Same person
                else:
                    similarity = cosine_similarity(embedding_list[i], embedding_list[j])
                
                print(f"{name1:15} vs {name2:15}: {similarity:.4f}")
                
                # Highlight potential issues
                if i != j and similarity > 0.8:
                    print(f"  ⚠️  WARNING: High similarity detected! These faces might be the same person!")
    
    print("\n=== Recommendations ===")
    print("1. Similarity scores above 0.8 indicate very similar faces")
    print("2. Similarity scores above 0.9 indicate likely the same person")
    print("3. If you see high similarities between different names, consider:")
    print("   - Using different photos for registration")
    print("   - Checking if the same person was registered multiple times")
    print("   - Adjusting the similarity threshold in register_module.py")

if __name__ == "__main__":
    test_face_similarities() 