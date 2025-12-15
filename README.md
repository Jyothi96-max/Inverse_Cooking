<img width="2454" height="88" alt="image" src="https://github.com/user-attachments/assets/b90bd470-a49a-46a3-b140-1358f7b9a14b" /><img width="2454" height="88" alt="image" src="https://github.com/user-attachments/assets/77da8d2e-2416-4aef-94ab-3cacd0f57967" /># Inverse_Cooking:Recipe generation from food images

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

The home page introduces the core functionality of the application—generating recipes from food images—through a clean and engaging layout. 

# Register Page
<img width="941" height="500" alt="image" src="https://github.com/user-attachments/assets/4c7222bc-1e56-4e0b-94b1-f8bd67e50109" />
If the user doesn’t have an account, they can easily register using the “Register” button on the top navigation bar. Once signed up, they can log in instantly to start generating recipes.

# Login Page
<img width="941" height="500" alt="image" src="https://github.com/user-attachments/assets/a88b9ffd-b344-4e1c-8aee-5f41efc18165" />

The login page allows registered users to securely access their account and start generating recipes from food images.


# Prediction page

<img width="941" height="500" alt="image" src="https://github.com/user-attachments/assets/a65549fc-9ae5-4153-a2e0-f5cc67693125" />
The prediction page displays the generated recipe based on the uploaded food image, including ingredients, instructions, and confidence score.

# Result page

<img width="941" height="500" alt="image" src="https://github.com/user-attachments/assets/562f16e0-dbc8-4a47-afbf-2e5a24100bde" />
The result page presents the final recipe output with a detailed ingredient list, cooking instructions, and an interactive voice assistant for guided preparation, offering a user-friendly experience tailored to the detected dish.

# History Page

<img width="940" height="500" alt="image" src="https://github.com/user-attachments/assets/57580894-b856-4ff9-8fa2-4629d184ba62" />
The history page provides users with a personalized timeline of previously generated recipes, displaying dish names, images, and upload dates to help them revisit.

# Favorite Page

<img width="1034" height="549" alt="image" src="https://github.com/user-attachments/assets/29cc8ddb-cf32-4d02-8ea7-b881769f406a" />

The Favorites page showcases the user's most loved recipes with ratings, tags, and options to view or remove them from their personal collection.
# Future Enhancements
Mobile app with camera integration

Real-time recipe suggestions based on pantry photos

Nutrition analysis and calorie tracking

Advanced recommendation engine using user history

Cloud deployment (AWS/Heroku) for public access

# Acknowledgments
Open-source contributors: PyTorch, Flask, Tailwind CSS, spaCy
Datasets: Food-101, Recipe NLG
# Contact
 Jyothi96-max (GitHub)
# Star & Contribute
⭐ Star this repo if helpful!
🐛 Found a bug? Open an issue
✨ Want to contribute? Fork and submit a PR!

# Built with ❤️ for AI-powered cooking


