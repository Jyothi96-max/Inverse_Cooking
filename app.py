from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import torch
import pickle
from sentence_transformers import SentenceTransformer, util
import spacy
import spacy_dbpedia_spotlight
import os
import re
import pysos
from datetime import datetime
import json
import cv2
import numpy as np
from scipy import ndimage

# Import image validation module
from Models.image_validation import validate_image_quality, detect_blur, detect_food_vs_nonfood

# Flask Setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration using PyMySQL
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',  # Add your MySQL password if needed
        db='foodtorecipe',
        cursorclass=pymysql.cursors.DictCursor
    )

# Uploads Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe('dbpedia_spotlight')
train = SentenceTransformer('clip-ViT-B-32')



# Load the models
print(" Models loadeing...")
with open("./Models/ingredient.pkl", 'rb') as fIn:
    labels = pickle.load(fIn)

text_emb = torch.load('./Models/food101_resnet50.pkl', map_location=torch.device('cpu'))
food2id = pysos.Dict("./Models/food2id")
gpt2recipe = pysos.Dict("./Models/gpt2_recipe.pkl")
print(" Models loaded  successfully")

# Stop Words
stop_words = set([
    'chopped', 'freshly ground', 'skinless', 'freshly squeezed', 'dash', 'powder',
    'rice', 'ice', 'noodles', 'pepper', 'milk', 'ced', 'cheese', 'sugar', 'salt',
    'pkt', 'minced', 'onion', 'onions', 'garlic', 'butter', 'slices', 'ounce',
    'sauce', 'freshly', 'grated', 'teaspoon', 'cup', 'oz', '⁄', 'to', 'or', 'diced',
    'into', 'pound', 'dried', 'water', 'about', 'whole', 'small', 'vegetable', 'inch',
    'tbsp', 'cooked', 'large', 'sliced', 'dry', 'optional', 'package', 'ounces',
    'unsalted', 'lbs', 'green', 'flour', 'for', 'wine', 'crushed', 'drained', 'lb',
    'frozen', 'tsp', 'finely', 'medium', 'tablespoon', 'tablespoons', 'juice',
    'shredded', 'can', 'fresh', 'cut', 'pieces', 'in', 'thinly', 'of', 'extract',
    'teaspoons', 'ground', 'and', 'cups', 'peeled', 'taste', 'ml', 'lengths'
])


# ========== ROUTES ==========

@app.route('/')
def index():
   return render_template('index.html')
    

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Comprehensive image validation
            print(f"\n Starting validation for: {filename}")
            is_valid, validation_message, validation_details = validate_image_quality(filepath)
            print(f"Validation result: {is_valid}")
            print(f"Validation message: {validation_message}")
            
            if not is_valid:
                print(f" Validation failed: {validation_message}")
                # Remove the uploaded file since it's not valid
                try:
                    os.remove(filepath)
                    print(f" Removed invalid file: {filepath}")
                except Exception as e:
                    print(f" Could not remove file: {e}")
                
                flash(validation_message, 'error')
                return redirect(request.url)
            else:
                print(f" Validation passed, proceeding with recipe generation")

            
            results = detect_food(filepath, 3)
            food_name, score = results[0]

            # Additional validation: Check if the detected food exists in our database
            try:
                food_id = food2id[food_name]
            except KeyError:
                # Remove the uploaded file since the detected food is not in our database
                try:
                    os.remove(filepath)
                except:
                    pass
                
                flash(f'Invalid upload! The detected food "{food_name}" is not recognized in our recipe database. Please upload a different food image.', 'error')
                return redirect(request.url)

            # Get recipe details
            food_id = food2id[food_name]
            recipe = gpt2recipe[food_id]

            # Process ingredients
            ingredients_raw = recipe['ingredients']
            highlighted_ingredients = get_spacy_dbpedia_highlights(ingredients_raw)

            # Prepare instructions in both list and string formats
            raw_instructions = recipe['instructions']
            if isinstance(raw_instructions, list):
                instructions_list = [instr for instr in raw_instructions if str(instr).strip()]
                instructions = '\n'.join(instructions_list)
            else:
                instructions_list = [line for line in str(raw_instructions).split('\n') if line.strip()]
                instructions = '\n'.join(instructions_list)

            # Prepare prediction data
            prediction = {
                'recipe_name': food_name.title(),
                'highlighted_ingredients': highlighted_ingredients,
                'recipe': instructions,
                'ingredients_raw': ingredients_raw,
                'instructions_list': instructions_list,
                'nutritional_facts': recipe.get('nutrition_facts', 'Nutrition information not available'),
                'source': recipe.get('recipesource', ''),
                'image_filename': filename,
                'score': f"{score * 100:.1f}%"
            }

            # Save to database (upload_history)
            try:
                connection = get_db_connection()
                with connection.cursor() as cur:
                    cur.execute("""
                        INSERT INTO upload_history (user_id, filename, food_detected, score, upload_time)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (session['id'], filename, food_name, score, datetime.now()))
                    connection.commit()
            except Exception as e:
                print(f"Database error: {e}")
                flash('Error saving to history', 'warning')
            finally:
                connection.close()

            return render_template('predict.html', prediction=prediction)

    return render_template('predict.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/test_validation', methods=['GET', 'POST'])
def test_validation():
    """Test route for image validation"""
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No file uploaded'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Test all validation functions (imported from Models.image_validation)
            is_blurry = detect_blur(filepath)
            is_food, food_confidence, food_reason = detect_food_vs_nonfood(filepath)
            is_valid, validation_message, validation_details = validate_image_quality(filepath)
            
            # Clean up test file
            try:
                os.remove(filepath)
            except:
                pass
            
            return jsonify({
                'filename': filename,
                'is_blurry': is_blurry,
                'is_food': is_food,
                'food_confidence': food_confidence,
                'food_reason': food_reason,
                'is_valid': is_valid,
                'validation_message': validation_message,
                'validation_details': validation_details
            })
    
    return render_template('test_validation.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('index'))

    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            connection = get_db_connection()
            with connection.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                
                if user and check_password_hash(user['password'], password):
                    session['loggedin'] = True
                    session['id'] = user['id']
                    session['name'] = user['name']
                    session['email'] = user['email']
                    return redirect(url_for('index'))
                else:
                    msg = 'Invalid email or password!'
        except Exception as e:
            print(f"Database error: {e}")
            msg = 'Database error occurred'
        finally:
            connection.close()

    return render_template('login.html', msg=msg)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'loggedin' in session:
        return redirect(url_for('index'))

    msg = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            connection = get_db_connection()
            with connection.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                account = cur.fetchone()

                if account:
                    msg = 'Account already exists!'
                else:
                    cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                                (name, email, hashed_password))
                    connection.commit()
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for('login'))
        except Exception as e:
            print(f"Database error: {e}")
            msg = 'Database error occurred'
        finally:
            connection.close()

    return render_template('signup.html', msg=msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/history')
def history():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    try:
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("""
                SELECT id, food_detected AS food_name, filename AS image_path, upload_time AS predicted_at, score 
                FROM upload_history 
                WHERE user_id = %s 
                ORDER BY upload_time DESC
            """, (session['id'],))
            history = cur.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
        history = []
        flash('Error retrieving history', 'error')
    finally:
        connection.close()

    return render_template('history.html', history=history)

# ========== UTILITY FUNCTIONS ==========

def detect_food(query_path, k=3):
    image = Image.open(query_path).convert("RGB")
    query_emb = train.encode(image, convert_to_tensor=True, show_progress_bar=False)
    hits = util.semantic_search(query_emb, text_emb, top_k=k)[0]
    return [(labels[hit['corpus_id']], hit['score']) for hit in hits]

def get_spacy_dbpedia_highlights(ingredients):
    raw = ingredients
    cleaned = re.sub(r"[0-9,()\/\-\.]", "", ingredients)
    doc = nlp(cleaned)
    for ent in doc.ents:
        if ent.text.lower() not in stop_words and ent.text in raw:
            link = f'<mark style="color:green;background-color:yellow;"><a href="{ent.kb_id_}" target="_blank">{ent.text}</a></mark>'
            raw = raw.replace(ent.text, link)
    return raw


# ========== RECIPE RATING & FEEDBACK ROUTES ==========

@app.route('/rate_recipe', methods=['POST'])
def rate_recipe():
    if 'loggedin' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        data = request.get_json(force=True)
        food_name = data.get('food_name')
        rating = int(data.get('rating', 5))
        feedback_text = data.get('feedback_text', '')
        cooking_experience = data.get('cooking_experience', 'medium')
        taste_rating = int(data.get('taste_rating', 5))
        presentation_rating = int(data.get('presentation_rating', 5))
        would_cook_again = data.get('would_cook_again', True)
        
        # Validate ratings
        if not (1 <= rating <= 5 and 1 <= taste_rating <= 5 and 1 <= presentation_rating <= 5):
            return jsonify({'error': 'Ratings must be between 1 and 5'}), 400
        
        connection = get_db_connection()
        with connection.cursor() as cur:
            # Insert or update rating
            cur.execute("""
                INSERT INTO recipe_ratings 
                (user_id, food_name, rating, feedback_text, cooking_experience, taste_rating, presentation_rating, would_cook_again)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                rating = VALUES(rating),
                feedback_text = VALUES(feedback_text),
                cooking_experience = VALUES(cooking_experience),
                taste_rating = VALUES(taste_rating),
                presentation_rating = VALUES(presentation_rating),
                would_cook_again = VALUES(would_cook_again),
                created_at = CURRENT_TIMESTAMP
            """, (session['id'], food_name, rating, feedback_text, cooking_experience, 
                  taste_rating, presentation_rating, would_cook_again))
            connection.commit()
        
        return jsonify({'success': True, 'message': 'Recipe rated successfully!'})
        
    except Exception as e:
        print(f"Rating error: {e}")
        return jsonify({'error': 'Failed to save rating'}), 500
    finally:
        connection.close()

@app.route('/get_recipe_stats/<food_name>')
def get_recipe_stats(food_name):
    try:
        connection = get_db_connection()
        with connection.cursor() as cur:
            # Get average ratings
            cur.execute("""
                SELECT 
                    AVG(rating) as avg_rating,
                    AVG(taste_rating) as avg_taste,
                    AVG(presentation_rating) as avg_presentation,
                    COUNT(*) as total_ratings,
                    SUM(CASE WHEN would_cook_again = 1 THEN 1 ELSE 0 END) as would_cook_again_count
                FROM recipe_ratings 
                WHERE food_name = %s
            """, (food_name,))
            stats = cur.fetchone()
            
            # Get recent feedback
            cur.execute("""
                SELECT r.feedback_text, r.rating, r.created_at, u.name as user_name
                FROM recipe_ratings r
                JOIN users u ON r.user_id = u.id
                WHERE r.food_name = %s AND r.feedback_text IS NOT NULL AND r.feedback_text != ''
                ORDER BY r.created_at DESC
                LIMIT 5
            """, (food_name,))
            recent_feedback = cur.fetchall()
            
        return jsonify({
            'stats': stats,
            'recent_feedback': recent_feedback
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'error': 'Failed to get recipe stats'}), 500
    finally:
        connection.close()

@app.route('/share_recipe', methods=['POST'])
def share_recipe():
    if 'loggedin' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        data = request.get_json(force=True)
        food_name = data.get('food_name')
        share_type = data.get('share_type')
        share_data = data.get('share_data', {})
        
        # Log the share
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("""
                INSERT INTO recipe_shares (user_id, food_name, share_type, share_data)
                VALUES (%s, %s, %s, %s)
            """, (session['id'], food_name, share_type, json.dumps(share_data)))
            connection.commit()
        
        # Generate share URLs
        share_urls = generate_share_urls(food_name, share_type)
        
        return jsonify({
            'success': True, 
            'share_urls': share_urls,
            'message': f'Recipe shared via {share_type}!'
        })
        
    except Exception as e:
        print(f"Share error: {e}")
        return jsonify({'error': 'Failed to share recipe'}), 500
    finally:
        connection.close()

def generate_share_urls(food_name, share_type):
    """Generate sharing URLs for different platforms"""
    base_url = request.host_url.rstrip('/')
    recipe_url = f"{base_url}/recipe/{food_name.replace(' ', '_')}"
    
    share_urls = {}
    
    if share_type == 'whatsapp':
        share_urls['whatsapp'] = f"https://wa.me/?text=Check out this amazing {food_name} recipe! {recipe_url}"
    
    elif share_type == 'email':
        share_urls['email'] = f"mailto:?subject=Amazing {food_name} Recipe&body=I found this great recipe: {recipe_url}"
    
    elif share_type == 'social_media':
        share_urls['facebook'] = f"https://www.facebook.com/sharer/sharer.php?u={recipe_url}"
        share_urls['twitter'] = f"https://twitter.com/intent/tweet?text=Check out this {food_name} recipe!&url={recipe_url}"
        share_urls['linkedin'] = f"https://www.linkedin.com/sharing/share-offsite/?url={recipe_url}"
    
    elif share_type == 'copy_link':
        share_urls['copy_link'] = recipe_url
    
    return share_urls

@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'loggedin' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        data = request.get_json(force=True)
        food_name = data.get('food_name')
        comment_text = data.get('comment_text', '').strip()
        is_public = data.get('is_public', True)
        
        if not comment_text:
            return jsonify({'error': 'Comment cannot be empty'}), 400
        
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("""
                INSERT INTO recipe_comments (user_id, food_name, comment_text, is_public)
                VALUES (%s, %s, %s, %s)
            """, (session['id'], food_name, comment_text, is_public))
            connection.commit()
        
        return jsonify({'success': True, 'message': 'Comment added successfully!'})
        
    except Exception as e:
        print(f"Comment error: {e}")
        return jsonify({'error': 'Failed to add comment'}), 500
    finally:
        connection.close()

@app.route('/get_recipe_comments/<food_name>')
def get_recipe_comments(food_name):
    try:
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("""
                SELECT c.comment_text, c.created_at, c.is_public, u.name as user_name
                FROM recipe_comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.food_name = %s AND c.is_public = 1
                ORDER BY c.created_at DESC
                LIMIT 10
            """, (food_name,))
            comments = cur.fetchall()
        
        return jsonify({'comments': comments})
        
    except Exception as e:
        print(f"Comments error: {e}")
        return jsonify({'error': 'Failed to get comments'}), 500
    finally:
        connection.close()

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    print(f"DEBUG: toggle_favorite called, session: {session}")  # Debug log
    
    if 'loggedin' not in session:
        print("DEBUG: User not logged in")  # Debug log
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        data = request.get_json(force=True)
        food_name = data.get('food_name')
        action = data.get('action', 'toggle')  # 'check' or 'toggle'
        print(f"DEBUG: Processing favorite for food: {food_name}, user_id: {session['id']}, action: {action}")  # Debug log
        
        connection = get_db_connection()
        with connection.cursor() as cur:
            # Check if already favorited
            cur.execute("""
                SELECT id FROM recipe_favorites 
                WHERE user_id = %s AND food_name = %s
            """, (session['id'], food_name))
            
            existing = cur.fetchone()
            print(f"DEBUG: Existing favorite found: {existing}")  # Debug log
            
            if action == 'check':
                # Just return the current status
                is_favorited = bool(existing)
                message = 'Status checked'
            else:
                # Toggle the favorite
                if existing:
                    # Remove from favorites
                    cur.execute("""
                        DELETE FROM recipe_favorites 
                        WHERE user_id = %s AND food_name = %s
                    """, (session['id'], food_name))
                    message = 'Removed from favorites'
                    is_favorited = False
                    print("DEBUG: Removed from favorites")  # Debug log
                else:
                    # Add to favorites
                    cur.execute("""
                        INSERT INTO recipe_favorites (user_id, food_name)
                        VALUES (%s, %s)
                    """, (session['id'], food_name))
                    message = 'Added to favorites'
                    is_favorited = True
                    print("DEBUG: Added to favorites")  # Debug log
                
                connection.commit()
        
        result = {
            'success': True, 
            'message': message,
            'is_favorited': is_favorited
        }
        print(f"DEBUG: Returning result: {result}")  # Debug log
        return jsonify(result)
        
    except Exception as e:
        print(f"DEBUG: Favorite error: {e}")  # Debug log
        print(f"DEBUG: Error type: {type(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full traceback
        return jsonify({'error': 'Failed to update favorites'}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/is_favorited/<food_name>')
def is_favorited(food_name):
    """Check if a recipe is favorited by the current user"""
    if 'loggedin' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("""
                SELECT id FROM recipe_favorites 
                WHERE user_id = %s AND food_name = %s
            """, (session['id'], food_name))
            
            is_favorited = bool(cur.fetchone())
        
        return jsonify({'is_favorited': is_favorited})
        
    except Exception as e:
        print(f"Is favorited error: {e}")
        return jsonify({'error': 'Failed to check favorite status'}), 500
    finally:
        connection.close()

@app.route('/check_favorite', methods=['POST'])
def check_favorite():
    if 'loggedin' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        data = request.get_json(force=True)
        food_name = data.get('food_name')
        
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("""
                SELECT id FROM recipe_favorites 
                WHERE user_id = %s AND food_name = %s
            """, (session['id'], food_name))
            
            is_favorited = bool(cur.fetchone())
        
        return jsonify({'is_favorited': is_favorited})
        
    except Exception as e:
        print(f"Check favorite error: {e}")
        return jsonify({'error': 'Failed to check favorite'}), 500
    finally:
        connection.close()

@app.route('/favorites')
def favorites():
    if 'loggedin' not in session:
        print("DEBUG: User not logged in, redirecting to login")
        return redirect(url_for('login'))
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cur:
            # Get favorites with all rating information
            cur.execute("""
                SELECT f.food_name, f.added_at, 
                       r.rating, r.taste_rating, r.presentation_rating, r.feedback_text,
                       r.cooking_experience, r.would_cook_again
                FROM recipe_favorites f
                LEFT JOIN recipe_ratings r ON f.user_id = r.user_id AND f.food_name = r.food_name
                WHERE f.user_id = %s
                ORDER BY f.added_at DESC
            """, (session['id'],))
            favorites = cur.fetchall()
        
        return render_template('favorites.html', favorites=favorites)
        
    except Exception as e:
        print(f"Favorites error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading favorites', 'error')
        return render_template('favorites.html', favorites=[])
    finally:
        connection.close()

@app.route('/debug')
def debug():
    """Debug page for troubleshooting"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cur:
            # Check if user is logged in
            user_info = {
                'loggedin': 'loggedin' in session,
                'user_id': session.get('id') if 'loggedin' in session else None,
                'username': session.get('username') if 'loggedin' in session else None
            }
            
            # Get all favorites for debugging
            cur.execute("SELECT * FROM recipe_favorites ORDER BY added_at DESC LIMIT 10")
            all_favorites = cur.fetchall()
            
            # Get favorites for current user
            user_favorites = []
            if 'loggedin' in session:
                cur.execute("""
                    SELECT f.food_name, f.added_at, 
                           r.rating, r.taste_rating, r.presentation_rating, r.feedback_text,
                           r.cooking_experience, r.would_cook_again
                    FROM recipe_favorites f
                    LEFT JOIN recipe_ratings r ON f.user_id = r.user_id AND f.food_name = r.food_name
                    WHERE f.user_id = %s
                    ORDER BY f.added_at DESC
                """, (session['id'],))
                user_favorites = cur.fetchall()
            
            # Get all users
            cur.execute("SELECT id, name, email FROM users LIMIT 10")
            users = cur.fetchall()
            
        connection.close()
        
        return jsonify({
            'user_info': user_info,
            'all_favorites': all_favorites,
            'user_favorites': user_favorites,
            'users': users,
            'total_favorites': len(all_favorites),
            'user_favorites_count': len(user_favorites)
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/test_session')
def test_session():
    """Test session and authentication"""
    return jsonify({
        'session_data': dict(session),
        'loggedin': 'loggedin' in session,
        'user_id': session.get('id') if 'loggedin' in session else None,
        'username': session.get('username') if 'loggedin' in session else None
    })

# ========== TEST ROUTES FOR DEBUGGING ==========

@app.route('/test_db')
def test_db():
    """Test database connection and favorites table"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cur:
            # Test basic connection
            cur.execute("SELECT 1 as test")
            test_result = cur.fetchone()
            
            # Test favorites table
            cur.execute("SHOW TABLES LIKE 'recipe_favorites'")
            table_exists = cur.fetchone()
            
            # Test users table
            cur.execute("SELECT id, username FROM users LIMIT 5")
            users = cur.fetchall()
            
            # Test recipe_favorites structure
            cur.execute("DESCRIBE recipe_favorites")
            table_structure = cur.fetchall()
            
        connection.close()
        
        return jsonify({
            'success': True,
            'db_connection': 'OK',
            'test_query': test_result,
            'favorites_table_exists': bool(table_exists),
            'users_count': len(users),
            'sample_users': users,
            'favorites_table_structure': table_structure
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# ========== SIMPLE TRANSLATION ENDPOINT ==========

# Simple translation mapping for common food terms
FOOD_TRANSLATIONS = {
    'hi': {  # Hindi
        'ingredients': 'सामग्री',
        'instructions': 'निर्देश',
        'step': 'चरण',
        'recipe': 'व्यंजन',
        'cook': 'पकाना',
        'mix': 'मिलाना',
        'add': 'जोड़ना',
        'heat': 'गर्म करना',
        'stir': 'हिलाना',
        'serve': 'परोसना'
    },
    'te': {  # Telugu
        'ingredients': 'పదార్థాలు',
        'instructions': 'సూచనలు',
        'step': 'దశ',
        'recipe': 'వంటకం',
        'cook': 'వండు',
        'mix': 'కలపండి',
        'add': 'జోడించండి',
        'heat': 'వేడి చేయండి',
        'stir': 'కదపండి',
        'serve': 'వడ్డించండి'
    },
    'ta': {  # Tamil
        'ingredients': 'பொருட்கள்',
        'instructions': 'வழிமுறைகள்',
        'step': 'படி',
        'recipe': 'சமையல்',
        'cook': 'சமைக்கவும்',
        'mix': 'கலக்கவும்',
        'add': 'சேர்க்கவும்',
        'heat': 'சூடாக்கவும்',
        'stir': 'கிளறவும்',
        'serve': 'பரிமாறவும்'
    }
}

def _normalize_lang_code(lang_code: str) -> str:
    """Extract language code from locale string"""
    try:
        return lang_code.split('-')[0].lower()
    except Exception:
        return 'en'

def simple_translate(text, target_lang):
    """Simple translation using predefined mappings"""
    if target_lang == 'en':
        return text
    
    translations = FOOD_TRANSLATIONS.get(target_lang, {})
    if not translations:
        return text
    
    # Simple word replacement for common cooking terms
    translated_text = text
    for english, translated in translations.items():
        translated_text = translated_text.replace(english, translated)
    
    return translated_text

@app.route('/translate', methods=['POST'])
def translate_content():
    try:
        data = request.get_json(force=True) or {}
        lang = _normalize_lang_code(str(data.get('lang', 'en')))

        title = str(data.get('title', ''))
        ingredients = str(data.get('ingredients', ''))
        steps = data.get('steps', []) or []

        # Use simple translation
        translated_title = simple_translate(title, lang) if title else ''
        translated_ingredients = simple_translate(ingredients, lang) if ingredients else ''

        translated_steps = []
        for s in steps:
            s_text = str(s).strip()
            translated_steps.append(simple_translate(s_text, lang) if s_text else '')

        return jsonify({
            'ok': True,
            'title': translated_title,
            'ingredients': translated_ingredients,
            'steps': translated_steps
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)