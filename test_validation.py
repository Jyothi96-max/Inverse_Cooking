#!/usr/bin/env python3
import sys
import os
import cv2
import numpy as np

def test_validation(image_path):
    print(f"Testing: {image_path}")
    
    # Blur test
    image = cv2.imread(image_path)
    if image is None:
        print("❌ Cannot read image")
        return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_blurry = laplacian_var < 50
    
    print(f"Laplacian variance: {laplacian_var:.2f}")
    print(f"Blur result: {'❌ BLURRY' if is_blurry else '✅ CLEAR'}")
    
    # Food test (simplified)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    green_ratio = np.sum((h >= 35) & (h <= 85) & (s > 50)) / (h.shape[0] * h.shape[1])
    blue_ratio = np.sum((h >= 100) & (h <= 130) & (s > 50)) / (h.shape[0] * h.shape[1])
    
    print(f"Green ratio: {green_ratio:.2f}")
    print(f"Blue ratio: {blue_ratio:.2f}")
    
    if green_ratio > 0.4 or blue_ratio > 0.3:
        print("❌ Likely nature/landscape image")
    else:
        print("✅ Not nature/landscape")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_validation.py <image_path>")
        sys.exit(1)
    
    test_validation(sys.argv[1])
