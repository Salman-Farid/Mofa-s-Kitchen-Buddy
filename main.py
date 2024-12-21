# -------------------- IMPORTS --------------------
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import pytesseract
from PIL import Image
import io
import os
import json

# -------------------- DATABASE CONFIGURATION --------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./kitchen_buddy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- DATABASE MODELS --------------------
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    quantity = Column(Float)
    unit = Column(String(20))
    category = Column(String(50), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True)
    cuisine_type = Column(String(50))
    preparation_time = Column(Integer)  # in minutes
    difficulty_level = Column(String(20))
    taste_profile = Column(String(100))
    instructions = Column(Text)
    ingredients_list = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# -------------------- PYDANTIC SCHEMAS --------------------
class IngredientBase(BaseModel):
    name: str
    quantity: float
    unit: str
    category: Optional[str] = None
    expiry_date: Optional[datetime] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(IngredientBase):
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None

class IngredientModel(IngredientBase):
    id: int
    last_updated: datetime

    class Config:
        orm_mode = True

class RecipeBase(BaseModel):
    name: str
    cuisine_type: str
    preparation_time: int
    difficulty_level: Optional[str] = "Medium"
    taste_profile: str
    instructions: str
    ingredients_list: str

class RecipeCreate(RecipeBase):
    pass

class RecipeModel(RecipeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
    message: str

# -------------------- HELPER FUNCTIONS --------------------
def ensure_recipe_directory():
    """Ensure the recipes directory exists"""
    os.makedirs("recipes", exist_ok=True)
    if not os.path.exists("recipes/my_fav_recipes.txt"):
        with open("recipes/my_fav_recipes.txt", "w") as f:
            f.write("# Mofa's Kitchen Buddy - Recipe Collection\n\n")

def save_recipe_to_file(recipe: RecipeModel):
    """Save recipe to text file"""
    ensure_recipe_directory()
    with open("recipes/my_fav_recipes.txt", "a", encoding="utf-8") as f:
        f.write(f"\nRECIPE: {recipe.name}\n")
        f.write(f"Cuisine: {recipe.cuisine_type}\n")
        f.write(f"Prep Time: {recipe.preparation_time} minutes\n")
        f.write(f"Difficulty: {recipe.difficulty_level}\n")
        f.write(f"Taste: {recipe.taste_profile}\n")
        f.write(f"Ingredients:\n{recipe.ingredients_list}\n")
        f.write(f"Instructions:\n{recipe.instructions}\n")
        f.write("-" * 50 + "\n")

def process_recipe_image(image: Image) -> str:
    """Process recipe image using OCR"""
    try:
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

# -------------------- FASTAPI APP --------------------
app = FastAPI(title="Mofa's Kitchen Buddy")

# Create database tables
Base.metadata.create_all(bind=engine)
ensure_recipe_directory()

# -------------------- INGREDIENTS ROUTES --------------------
@app.post("/ingredients/", response_model=IngredientModel)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    try:
        db_ingredient = Ingredient(**ingredient.dict())
        db.add(db_ingredient)
        db.commit()
        db.refresh(db_ingredient)
        return db_ingredient
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ingredients/", response_model=List[IngredientModel])
def list_ingredients(
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Ingredient)
    if category:
        query = query.filter(Ingredient.category == category)
    return query.offset(skip).limit(limit).all()

@app.put("/ingredients/{ingredient_id}", response_model=IngredientModel)
def update_ingredient(
        ingredient_id: int,
        ingredient: IngredientUpdate,
        db: Session = Depends(get_db)
):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    update_data = ingredient.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ingredient, key, value)

    db_ingredient.last_updated = datetime.utcnow()
    try:
        db.commit()
        db.refresh(db_ingredient)
        return db_ingredient
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not db_ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    try:
        db.delete(db_ingredient)
        db.commit()
        return {"message": "Ingredient deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# -------------------- RECIPES ROUTES --------------------
@app.post("/recipes/", response_model=RecipeModel)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    try:
        db_recipe = Recipe(**recipe.dict())
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)

        # Save to text file
        save_recipe_to_file(db_recipe)
        return db_recipe
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recipes/", response_model=List[RecipeModel])
def list_recipes(
        skip: int = 0,
        limit: int = 100,
        cuisine_type: Optional[str] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Recipe)
    if cuisine_type:
        query = query.filter(Recipe.cuisine_type == cuisine_type)
    return query.offset(skip).limit(limit).all()

@app.post("/recipes/upload-image/")
async def upload_recipe_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        text = process_recipe_image(image)

        # Save to my_fav_recipes.txt
        ensure_recipe_directory()
        with open("recipes/my_fav_recipes.txt", "a", encoding="utf-8") as f:
            f.write(f"\nRECIPE FROM IMAGE:\n")
            f.write(text)
            f.write("\n" + "-" * 50 + "\n")

        return {
            "message": "Recipe image processed and saved successfully",
            "extracted_text": text
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------- CHATBOT ROUTES --------------------
@app.post("/chatbot/chat/")
def chat_with_bot(message: ChatMessage, db: Session = Depends(get_db)):
    try:
        # Get available ingredients
        available_ingredients = db.query(Ingredient).all()
        ingredient_names = [ing.name.lower() for ing in available_ingredients]

        # Read recipes
        with open("recipes/my_fav_recipes.txt", "r", encoding="utf-8") as f:
            recipes = f.read()

        # Simple response logic (in production, use a proper LLM)
        msg = message.message.lower()
        if "sweet" in msg:
            return {
                "response": "Based on your available ingredients, here are some sweet recipes you might like to try:\n" +
                            "".join([line for line in recipes.split('\n') if 'sweet' in line.lower()][:3])
            }
        elif "spicy" in msg:
            return {
                "response": "I found these spicy recipes that match your ingredients:\n" +
                            "".join([line for line in recipes.split('\n') if 'spicy' in line.lower()][:3])
            }
        elif "available" in msg or "ingredients" in msg:
            return {
                "response": f"You currently have: {', '.join(ingredient_names)}"
            }

        return {
            "response": "I can help you find recipes based on your preferences and available ingredients. " +
                        "Would you like something sweet, spicy, or should I list your available ingredients?"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- ROOT ROUTE --------------------
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Mofa's Kitchen Buddy!",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

# -------------------- RUN APPLICATION --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)