import enum
import uuid
from datetime import datetime
from typing import Optional
import os

from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="UbuntuCycle", description="Community Sharing Platform")

# Mount static files
app.mount("/static", StaticFiles(directory="ubuntu_cycle/static"), name="static")

# Templates
templates = Jinja2Templates(directory="ubuntu_cycle/templates")

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///ubuntu_cycle/ubuntucycle.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.getenv("CLOUDINARY_API_KEY", ""),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "")
)

# Pydantic Models
class ItemStatusEnum(str, enum.Enum):
    AVAILABLE = "Available"
    CLAIMED = "Claimed"
    GONE = "Gone"

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: str
    image_url: Optional[str] = None
    status: str = ItemStatusEnum.AVAILABLE.value
    claimed_by_note: Optional[str] = None
    date_posted: datetime

    class Config:
        from_attributes = True

# SQLAlchemy DB Model
class DBItem(Base):
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    category = Column(String)
    image_url = Column(String)
    status = Column(String, default=ItemStatusEnum.AVAILABLE.value)
    claimed_by_note = Column(String)
    date_posted = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def public_index(request: Request, db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "items": items,
        "item_status_enum": ItemStatusEnum,
        "now": datetime.now()
    })

@app.post("/items/{item_id}/claim")
async def claim_item(item_id: str, claimer_info: str = Form(...), db: Session = Depends(get_db)):
    item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item.status != ItemStatusEnum.AVAILABLE.value:
        raise HTTPException(status_code=400, detail="Item is not available for claiming")
    
    # Update the item using SQLAlchemy update
    db.query(DBItem).filter(DBItem.id == item_id).update({
        "status": ItemStatusEnum.CLAIMED.value,
        "claimed_by_note": claimer_info
    })
    db.commit()
    
    return {"message": "Item claimed successfully", "item_id": item_id}

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    items = db.query(DBItem).all()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "items": items,
        "item_status_enum": ItemStatusEnum,
        "now": datetime.now()
    })

@app.post("/admin/items/add")
async def admin_add_item(
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(""),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_url = None
    
    # Upload image to Cloudinary if provided and configured
    if image and image.filename and os.getenv("CLOUDINARY_CLOUD_NAME"):
        try:
            result = cloudinary.uploader.upload(image.file)
            image_url = result.get("secure_url")
        except Exception as e:
            print(f"Error uploading image: {e}")
    
    # Create new item
    new_item = DBItem(
        title=title,
        description=description if description else None,
        category=category if category else None,
        image_url=image_url
    )
    
    db.add(new_item)
    db.commit()
    
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/items/{item_id}/update_status")
async def admin_update_item_status(
    item_id: str,
    status: str = Form(...),
    claimed_by_note: str = Form(""),
    db: Session = Depends(get_db)
):
    item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update using SQLAlchemy update
    db.query(DBItem).filter(DBItem.id == item_id).update({
        "status": status,
        "claimed_by_note": claimed_by_note if claimed_by_note else None
    })
    db.commit()
    
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)