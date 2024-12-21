# Mofa's Kitchen Buddy

## Overview
Mofa's Kitchen Buddy is a FastAPI-based application designed to help users manage their kitchen inventory and recipes. It includes features such as ingredient tracking, recipe storage, recipe discovery via chatbot interaction, and optical character recognition (OCR) to extract recipes from uploaded images.

---

## Features
- **Ingredient Management**: Add, update, list, and delete ingredients.
- **Recipe Management**: Add, list, and upload recipes from images using OCR.
- **Chatbot Interaction**: Get recipe suggestions based on preferences (e.g., sweet, spicy) and available ingredients.
- **File-Based Recipe Storage**: Recipes are stored in a `my_fav_recipes.txt` file for easy access.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   python main.py
   ```
   This will automatically create the database `kitchen_buddy.db` and initialize tables.

4. Install Tesseract OCR (for image processing):
   - On Ubuntu:
     ```bash
     sudo apt install tesseract-ocr
     ```
   - On macOS:
     ```bash
     brew install tesseract
     ```
   - On Windows:
     Download the installer from [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract) and follow the installation instructions.

5. Run the application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. Access the API documentation:
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

7. Access ReDoc documentation:
   Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) in your browser.

---

## API Endpoints

### Ingredients
- **Create Ingredient**: `POST /ingredients/`
  ```bash
  curl -X POST "http://127.0.0.1:8000/ingredients/" -H "Content-Type: application/json" -d '{"name": "Sugar", "quantity": 1, "unit": "kg"}'
  ```
- **List Ingredients**: `GET /ingredients/`
  ```bash
  curl -X GET "http://127.0.0.1:8000/ingredients/"
  ```
- **Update Ingredient**: `PUT /ingredients/{ingredient_id}`
  ```bash
  curl -X PUT "http://127.0.0.1:8000/ingredients/1" -H "Content-Type: application/json" -d '{"quantity": 2, "unit": "kg"}'
  ```
- **Delete Ingredient**: `DELETE /ingredients/{ingredient_id}`
  ```bash
  curl -X DELETE "http://127.0.0.1:8000/ingredients/1"
  ```

### Recipes
- **Create Recipe**: `POST /recipes/`
  ```bash
  curl -X POST "http://127.0.0.1:8000/recipes/" -H "Content-Type: application/json" -d '{"name": "Chocolate Cake", "cuisine_type": "Dessert", "preparation_time": 60, "taste_profile": "Sweet", "instructions": "Mix and bake.", "ingredients_list": "Flour, Sugar, Cocoa"}'
  ```
- **List Recipes**: `GET /recipes/`
  ```bash
  curl -X GET "http://127.0.0.1:8000/recipes/"
  ```
- **Upload Recipe Image**: `POST /recipes/upload-image/`
  ```bash
  curl -X POST "http://127.0.0.1:8000/recipes/upload-image/" -F "file=@path_to_image.jpg"
  ```

### Chatbot
- **Chat with Bot**: `POST /chatbot/chat/`
  ```bash
  curl -X POST "http://127.0.0.1:8000/chatbot/chat/" -H "Content-Type: application/json" -d '{"message": "Show me sweet recipes"}'
  ```

---

## Configuration
- Database: SQLite (`kitchen_buddy.db`).
- Recipe Storage: `recipes/my_fav_recipes.txt` (automatically created).

---

## File Structure
- `main.py`: Application entry point.
- `kitchen_buddy.db`: SQLite database file.
- `recipes/`: Directory containing `my_fav_recipes.txt` for storing recipes.

---

## Requirements
- Python 3.7+
- FastAPI
- SQLAlchemy
- Tesseract OCR
- PIL (Pillow)
- Pydantic

---

## Future Enhancements
- Add user authentication.
- Implement more advanced chatbot functionality using LLMs.
- Extend support for multiple recipe file formats.

---

## License
This project is licensed under the MIT License.

---

## Contact
For any questions or suggestions, feel free to contact Mofa's Kitchen Buddy team at `support@mofa-kitchen.com`.

