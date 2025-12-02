#!/usr/bin/env python3
"""
Simple test script for blur detection
Usage: python test_blur_detection.py <image_path>
"""

import sys
import os
import cv2
import numpy as np

def detect_blur(image_path, threshold=50):
    """
    Detect if an image is blurry using Laplacian variance
    Returns True if image is blurry, False if clear
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not read image: {image_path}")
            return True
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Also check for motion blur using gradient magnitude
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        avg_gradient = np.mean(gradient_magnitude)
        
        # Combined blur detection
        is_blurry_laplacian = laplacian_var < threshold
        is_blurry_gradient = avg_gradient < 25
        
        print(f"\n=== BLUR DETECTION RESULTS ===")
        print(f"Image: {image_path}")
        print(f"Image size: {image.shape}")
        print(f"Laplacian variance: {laplacian_var:.2f} (threshold: {threshold})")
        print(f"Average gradient: {avg_gradient:.2f} (threshold: 25)")
        print(f"Is blurry (Laplacian): {is_blurry_laplacian}")
        print(f"Is blurry (Gradient): {is_blurry_gradient}")
        
        is_blurry = is_blurry_laplacian or is_blurry_gradient
        print(f"Final result: {'❌ BLURRY' if is_blurry else '✅ CLEAR'}")
        
        return is_blurry
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_blur_detection.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    detect_blur(image_path)
