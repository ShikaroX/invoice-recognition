# Automatic invoice recognition project
College project on automatic invoice recognition using machine learning techniques like OCR and NLP.

## Required downloads

### Poppler package - Essential for handling PDF files.

Windows - *https://github.com/oschwartz10612/poppler-windows/releases*

Linux - Run **sudo apt install poppler-utils** in the terminal. (Not tested yet)

IOS - Install 'Homebrew' by running **/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"** and then run **brew install poppler**. (Not tested yet)

### Tesseract OCR

Windows - *https://github.com/UB-Mannheim/tesseract/wiki*

In the installation menu, **only English comes by default**. If you need other languages, **additional script and language data are necessary!**

#### Portuguese Language Support

Ensure that the *por.traineddata* file is present in the *tessdata* directory inside the *Tesseract-OCR* path: **Tesseract-OCR\tessdata\por.traineddata**

This file is required to enable Portuguese language support for Tesseract OCR.

For more details, visit the official Tesseract OCR documentation: **[Tesseract Wiki](https://tesseract-ocr.github.io/)**

## Required libraries

All the required libraries are listed in the *requirements.txt* file.

To install them, run the following command in the terminal: **pip install -r requirements.txt**


