# Inverse_Cooking:Recipe generation from food images

# Project Overview
Inverse Cooking generates complete recipes directly from food images using AI. Users upload food photos through a Flask web app, and ResNet-50 + GPT-2 predict ingredients and step-by-step instructions. Includes user authentication, history, favorites, ratings, comments, and multilingual voice support. 

# Key Features
AI Pipeline: ResNet-50 (Food-101 dataset) extracts features; GPT-2 (Recipe NLG) generates recipes​

Image Validation: Laplacian variance filters blurred/non-food images​

Web App: Flask backend + HTML/Tailwind CSS/JavaScript frontend​

Database: MySQL (XAMPP) stores users, history, favorites, ratings, comments​

Voice Assistant: Multilingual recipe narration

# Tech Stack

| Category         | Technologies                                                                

| Backend          | Python, Flask, PyTorch, PyMySQL 
| AI Models        | ResNet-50, GPT-2, spaCy, Sentence Transformers 
| Frontend         | HTML, Tailwind CSS, JavaScript               
| Database         | MySQL (XAMPP)                                
| Image Processing | OpenCV, Pillow                        
| Development      | Visual Studio Code, Git    

# Live Demo Screenshots

# Home page
<img width="938" height="571" alt="image" src="https://github.com/user-attachments/assets/99b6a5f2-464a-4d4c-9790-2e8d8cca53c3" />

