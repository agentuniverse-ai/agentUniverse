# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/27 21:38
# @Author  : zhangdongxu
# @Email   : zhangdongxu0852@163.com
# @FileName: test_readimage_tool.py
import cv2
import pytesseract
from PIL import Image
import numpy as np
import re
import os

def enhance_image(image):
    """
    Enhance the image: convert to grayscale, apply CLAHE for contrast enhancement,
    then apply bilateral filtering to reduce noise while preserving edges.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    # Bilateral filtering reduces noise while preserving edge details
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    return filtered

def detect_text_regions(image, east_model='frozen_east_text_detection.pb', min_confidence=0.5, width=320, height=320):
    """
    Detect text regions in the image using the EAST text detection model.
    Returns a list of image regions (as numpy arrays) corresponding to text areas.
    """
    # Load the EAST model
    net = cv2.dnn.readNet(east_model)
    orig = image.copy()
    (origH, origW) = image.shape[:2]

    # The EAST model requires dimensions to be multiples of 32.
    newW, newH = width, height
    rW = origW / float(newW)
    rH = origH / float(newH)
    resized = cv2.resize(image, (newW, newH))

    blob = cv2.dnn.blobFromImage(resized, 1.0, (newW, newH),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)
    # Output layers of the EAST model
    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
    (scores, geometry) = net.forward(layerNames)
    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    # Iterate over rows and columns to extract predictions
    for y in range(0, numRows):
        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(0, numCols):
            if scoresData[x] < min_confidence:
                continue

            offsetX = x * 4.0
            offsetY = y * 4.0

            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append((startX, startY, endX, endY))
            confidences.append(float(scoresData[x]))

    # Apply non-maxima suppression to suppress overlapping boxes
    boxes = cv2.dnn.NMSBoxes(rects, confidences, min_confidence, 0.4)
    regions = []
    if len(boxes) > 0:
        for i in boxes.flatten():
            (startX, startY, endX, endY) = rects[i]
            # Scale the bounding box coordinates back to the original image dimensions
            startX = int(startX * rW)
            startY = int(startY * rH)
            endX = int(endX * rW)
            endY = int(endY * rH)
            # Crop the detected text region from the original image
            region = orig[startY:endY, startX:endX]
            regions.append(region)
    return regions

def ocr_on_regions(regions, lang='chi_sim+eng'):
    """
    Perform OCR on each text region separately and concatenate the results.
    """
    texts = []
    config = "--oem 3 --psm 6"
    for region in regions:
        if region.size == 0:
            continue
        # Optionally, additional preprocessing (e.g., binarization) can be applied here.
        pil_img = Image.fromarray(region)
        text = pytesseract.image_to_string(pil_img, lang=lang, config=config)
        texts.append(text)
    return "\n".join(texts)

def clean_extracted_text(text):
    """
    Clean the OCR output text by removing extra whitespace.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def save_text_to_file(text, output_file='extracted_text.txt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Text content saved to {output_file}")

def extract_text_from_image(image_path, use_east=True, lang='chi_sim+eng'):
    """
    Extract text from an image:
      - First, enhance the image.
      - If use_east is True, use the EAST model to detect text regions and perform OCR on each region.
      - Otherwise, perform OCR on the enhanced whole image.
    """
    # Read image using IMREAD_UNCHANGED to support any image format
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError("Cannot load image, please check the path")
    
    # Convert image to 3-channel BGR if it's not already
    if len(image.shape) == 2:
        # If the image is grayscale, convert to BGR
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif len(image.shape) == 3 and image.shape[2] == 4:
        # If the image has an alpha channel, convert BGRA to BGR
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    
    # Enhance the image
    enhanced = enhance_image(image)
    
    if use_east:
        try:
            # Use the original color image for EAST detection (usually yields better results)
            regions = detect_text_regions(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if len(regions) == 0:
                raise Exception("No text regions detected, falling back to full image OCR")
            raw_text = ocr_on_regions(regions, lang=lang)
        except Exception as e:
            print("EAST detection failed, using full image OCR:", e)
            pil_img = Image.fromarray(enhanced)
            config = "--oem 3 --psm 6"
            raw_text = pytesseract.image_to_string(pil_img, lang=lang, config=config)
    else:
        pil_img = Image.fromarray(enhanced)
        config = "--oem 3 --psm 6"
        raw_text = pytesseract.image_to_string(pil_img, lang=lang, config=config)
    
    final_text = clean_extracted_text(raw_text)
    return final_text

if __name__ == "__main__":
    # Specify the input image file. It can be a jpg, png, or any common format.
    image_file = 'input.png'  # Change to 'input.png' or other formats as needed
    text_output = extract_text_from_image(image_file, use_east=True, lang='chi_sim+eng')
    print("Extracted text:")
    print(text_output)
    save_text_to_file(text_output, 'extracted_text.txt')

