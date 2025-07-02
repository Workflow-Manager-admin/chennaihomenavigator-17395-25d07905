from fastapi import FastAPI, WebSocket, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from pydantic import BaseModel, EmailStr
import sqlite3
import datetime

# SQLite setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./homequestai.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------- DATABASE MODELS -----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Relationship to profile
    profile = relationship("UserProfile", uselist=False, back_populates="user")

class UserProfile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    budget = Column(Integer)
    preferred_location = Column(String)
    filters = Column(Text)
    # Relationship
    user = relationship("User", back_populates="profile")

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String, index=True)
    price = Column(Float)
    property_type = Column(String)  # rental/purchase
    amenities = Column(String)
    listed_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Relationship
    photos = relationship("Media", back_populates="property")

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    property_id = Column(Integer, ForeignKey("properties.id"))
    media_type = Column(String)  # photo, video, affiliate
    property = relationship("Property", back_populates="photos")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    review_text = Column(Text)
    rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    approved = Column(Boolean, default=False)

class Viewing(Base):
    __tablename__ = "viewings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))
    scheduled_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create all tables
Base.metadata.create_all(bind=engine)


# ----------------- PYDANTIC MODELS (SCHEMAS) -----------------
class UserCreate(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    password: str
    name: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    phone: Optional[str]
    name: str

    class Config:
        orm_mode = True

class ProfileCreate(BaseModel):
    budget: Optional[int] = None
    preferred_location: Optional[str] = None
    filters: Optional[str] = None

class ProfileOut(ProfileCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class PropertyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: str
    price: float
    property_type: str
    amenities: Optional[str] = None

class PropertyOut(PropertyCreate):
    id: int
    listed_by: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class MediaOut(BaseModel):
    id: int
    url: str
    media_type: str

    class Config:
        orm_mode = True

class ReviewCreate(BaseModel):
    property_id: int
    review_text: str
    rating: int

class ReviewOut(BaseModel):
    id: int
    user_id: int
    property_id: int
    review_text: str
    rating: int
    created_at: datetime.datetime
    approved: bool

    class Config:
        orm_mode = True

class ViewingCreate(BaseModel):
    property_id: int
    scheduled_at: datetime.datetime

class ViewingOut(BaseModel):
    id: int
    user_id: int
    property_id: int
    scheduled_at: datetime.datetime
    created_at: datetime.datetime

    class Config:
        orm_mode = True

# ----------------- FASTAPI SETUP -----------------
app = FastAPI(
    title="HomeQuestAI Backend API",
    description="API for HomeQuestAI: a smart real estate platform for Chennai. Features: user management, properties, recommendations, chat, scheduling, reviews, and more.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "API Health and DB Connectivity"},
        {"name": "Users", "description": "User registration, login, profiles"},
        {"name": "Properties", "description": "Create/search/filter property listings"},
        {"name": "Media", "description": "Media for listings (photos, videos, links)"},
        {"name": "Search", "description": "Property and map search/filter"},
        {"name": "Scheduling", "description": "Schedule/track property visits"},
        {"name": "Chat", "description": "WebSocket and Twilio chat"},
        {"name": "AI", "description": "AI Recommendations and insights"},
        {"name": "Reviews", "description": "CRUD for reviews & moderation"},
        {"name": "VirtualTours", "description": "360°/AR/VR/Media access"},
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- HEALTH CHECK ENDPOINTS -----------------
# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Basic health check", description="Returns API health status")
def health_check():
    """
    Returns basic status for FastAPI running.
    """
    return {"status": "Healthy"}

# PUBLIC_INTERFACE
@app.get("/health/db", tags=["Health"], summary="Database health check", description="Checks DB connection and returns status")
def db_health_check():
    """
    Verifies SQLite DB connection.
    """
    try:
        conn = sqlite3.connect("homequestai.db")
        conn.execute("SELECT 1;")
        conn.close()
        return {"db_connection": "ok"}
    except Exception as e:
        return JSONResponse(status_code=503, content={"db_connection": "failed", "detail": str(e)})

# ----------------- USERS + PROFILE ENDPOINTS -----------------
# Dummy auth only -- integrate with real auth later, hashed_password is not really used
# PUBLIC_INTERFACE
@app.post("/users/register", tags=["Users"], summary="Register a new user")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register user (simulated, not real auth)"""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(email=user.email, phone=user.phone, hashed_password=user.password, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserOut.from_orm(db_user)

# PUBLIC_INTERFACE
@app.get("/users/{user_id}", tags=["Users"], response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.from_orm(user)

# PUBLIC_INTERFACE
@app.post("/users/{user_id}/profile", tags=["Users"], response_model=ProfileOut)
def create_profile(user_id: int, profile: ProfileCreate, db: Session = Depends(get_db)):
    """Create or update user profile."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if existing:
        for k, v in profile.dict(exclude_unset=True).items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return ProfileOut.from_orm(existing)
    new_profile = UserProfile(**profile.dict(), user_id=user_id)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return ProfileOut.from_orm(new_profile)

# PUBLIC_INTERFACE
@app.get("/users/{user_id}/profile", tags=["Users"], response_model=ProfileOut)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileOut.from_orm(profile)

# ----------------- PROPERTY ENDPOINTS -----------------
# PUBLIC_INTERFACE
@app.post("/properties/", tags=["Properties"], response_model=PropertyOut)
def create_property(property: PropertyCreate, listed_by: int = Query(..., description="User ID of listing agent"), db: Session = Depends(get_db)):
    """Create a property listing."""
    db_property = Property(**property.dict(), listed_by=listed_by)
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return PropertyOut.from_orm(db_property)

# PUBLIC_INTERFACE
@app.get("/properties/", tags=["Properties"], response_model=List[PropertyOut])
def search_properties(
        location: Optional[str] = Query(None),
        property_type: Optional[str] = Query(None),
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        amenities: Optional[str] = None,
        db: Session = Depends(get_db)):
    """Search property listings with filters."""
    q = db.query(Property)
    if location:
        q = q.filter(Property.location == location)
    if property_type:
        q = q.filter(Property.property_type == property_type)
    if min_price:
        q = q.filter(Property.price >= min_price)
    if max_price:
        q = q.filter(Property.price <= max_price)
    if amenities:
        q = q.filter(Property.amenities.contains(amenities))
    results = q.order_by(Property.created_at.desc()).limit(20).all()
    return [PropertyOut.from_orm(p) for p in results]

# PUBLIC_INTERFACE
@app.get("/properties/{property_id}", tags=["Properties"], response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    """Get details for one property."""
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return PropertyOut.from_orm(prop)

# ----------------- MEDIA ENDPOINTS -----------------
# PUBLIC_INTERFACE
@app.get("/properties/{property_id}/media", tags=["Media"], response_model=List[MediaOut])
def get_property_media(property_id: int, db: Session = Depends(get_db)):
    """Get all media for given property (photos/videos/links)"""
    media = db.query(Media).filter(Media.property_id == property_id).all()
    return [MediaOut.from_orm(m) for m in media]

# PUBLIC_INTERFACE
@app.post("/properties/{property_id}/media", tags=["Media"], response_model=MediaOut)
def add_property_media(property_id: int, url: str = Query(...), media_type: str = Query("photo"), db: Session = Depends(get_db)):
    """Add media (image/video/link) to a property listing."""
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    m = Media(property_id=property_id, url=url, media_type=media_type)
    db.add(m)
    db.commit()
    db.refresh(m)
    return MediaOut.from_orm(m)

# ----------------- VIEWING/SCHEDULING ENDPOINTS -----------------
# PUBLIC_INTERFACE
@app.post("/schedule/{user_id}/viewing", tags=["Scheduling"], response_model=ViewingOut)
def schedule_viewing(user_id: int, details: ViewingCreate, db: Session = Depends(get_db)):
    """Schedule a viewing for a property."""
    user = db.query(User).filter(User.id == user_id).first()
    prop = db.query(Property).filter(Property.id == details.property_id).first()
    if not user or not prop:
        raise HTTPException(status_code=404, detail="User or property not found")
    v = Viewing(user_id=user_id, property_id=details.property_id, scheduled_at=details.scheduled_at)
    db.add(v)
    db.commit()
    db.refresh(v)
    return ViewingOut.from_orm(v)

# PUBLIC_INTERFACE
@app.get("/schedule/{user_id}/viewings", tags=["Scheduling"], response_model=List[ViewingOut])
def get_user_viewings(user_id: int, db: Session = Depends(get_db)):
    """Get all scheduled viewings by a user."""
    viewings = db.query(Viewing).filter(Viewing.user_id == user_id).order_by(Viewing.scheduled_at.desc()).all()
    return [ViewingOut.from_orm(v) for v in viewings]

# ----------------- CHAT (WebSocket + SMS STUB) -----------------
# PUBLIC_INTERFACE
@app.websocket("/ws/chat/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket-based chat (only in-app, not real SMS).
    Usage: Connect using ws://host/ws/chat/{user_id},
    send/receive dicts with keys: 'message', 'to'.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Echo message back for now (dummy)
            await websocket.send_json({"from": user_id, "echoed_message": data.get("message")})
    except Exception:
        await websocket.close()

# PUBLIC_INTERFACE
@app.post("/chat/sms", tags=["Chat"], description="Stub: Send SMS via Twilio", summary="Send SMS (stub only)")
def send_sms_stub(phone_number: str = Query(...), message: str = Query(...)):
    """Simulate SMS sending, for future integration with Twilio."""
    return {"status": "stub", "detail": f"Would send to {phone_number}: {message}"}

# ----------------- SEARCH/AI/RECOMMENDATIONS/MARKET ENDPOINTS -----------------
# PUBLIC_INTERFACE
@app.get("/ai/recommendations", tags=["AI"], summary="Get AI-driven property recommendations (stub)")
def get_ai_recommendations(user_id: int = Query(...)):
    """Stub endpoint for Hugging Face AI recommendations. No real ML call."""
    # Return dummy recommendations for now
    return {"user_id": user_id, "recommendations": ["Property-101", "Property-202"]}

# PUBLIC_INTERFACE
@app.get("/market/insights", tags=["AI"], summary="Get market insights (stub)")
def market_insights():
    """Stub for aggregated NayaPurana.in/market data."""
    return {"insights": "Stub market insights about pricing, trends, supply, demand."}

# ----------------- VIRTUAL TOUR ENDPOINTS -----------------
# PUBLIC_INTERFACE
@app.get("/virtualtour/{property_id}", tags=["VirtualTours"], summary="Get property tour media")
def get_virtual_tour(property_id: int, db: Session = Depends(get_db)):
    """
    Get links to property virtual tour and AR/360° media (stub/dummy for now).
    """
    # Real endpoint would return AR.js or 360° media links.
    # Stub: just send all videos for now
    media = db.query(Media).filter(Media.property_id == property_id, Media.media_type == "video").all()
    return [MediaOut.from_orm(m) for m in media]

# PUBLIC_INTERFACE
@app.get("/virtualtour/{property_id}/ar", tags=["VirtualTours"], summary="Get AR preview for property")
def get_ar_preview(property_id: int):
    """Stub: Returns a dummy AR preview link."""
    return {"ar_preview": f"https://ar-stub.homequestai.com/property/{property_id}"}

# ----------------- REVIEWS ENDPOINTS -----------------
# PUBLIC_INTERFACE
@app.post("/reviews/{user_id}", tags=["Reviews"], response_model=ReviewOut)
def create_review(user_id: int, review: ReviewCreate, db: Session = Depends(get_db)):
    """Create a new review for a property (defaults to unapproved)."""
    user = db.query(User).filter(User.id == user_id).first()
    prop = db.query(Property).filter(Property.id == review.property_id).first()
    if not user or not prop:
        raise HTTPException(status_code=404, detail="User or property not found")
    r = Review(user_id=user_id, property_id=review.property_id, review_text=review.review_text, rating=review.rating)
    db.add(r)
    db.commit()
    db.refresh(r)
    return ReviewOut.from_orm(r)

# PUBLIC_INTERFACE
@app.get("/reviews/property/{property_id}", tags=["Reviews"], response_model=List[ReviewOut])
def get_property_reviews(property_id: int, db: Session = Depends(get_db)):
    """Get (approved) reviews for a property."""
    reviews = db.query(Review).filter(Review.property_id == property_id, Review.approved is True).all()
    return [ReviewOut.from_orm(r) for r in reviews]

# PUBLIC_INTERFACE
@app.get("/reviews/pending", tags=["Reviews"], response_model=List[ReviewOut], summary="Get reviews awaiting moderation")
def get_reviews_pending_moderation(db: Session = Depends(get_db)):
    """List all pending reviews for moderator (admin use)."""
    reviews = db.query(Review).filter(Review.approved is False).all()
    return [ReviewOut.from_orm(r) for r in reviews]

# PUBLIC_INTERFACE
@app.post("/reviews/{review_id}/approve", tags=["Reviews"], summary="Approve a review", response_model=ReviewOut)
def approve_review(review_id: int, approve: bool = Query(True), db: Session = Depends(get_db)):
    """Approve (or reject & delete) a pending review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if approve:
        review.approved = True
        db.commit()
        db.refresh(review)
        return ReviewOut.from_orm(review)
    else:
        db.delete(review)
        db.commit()
        raise HTTPException(status_code=204, detail="Review deleted")

# ---- Swagger documentation for direct WebSocket API usage ----
# PUBLIC_INTERFACE
@app.get("/docs/websocket", tags=["Chat"], summary="WebSocket API usage guide")
def ws_api_usage():
    """
    API endpoint showing info on how to connect to the WebSocket chat endpoint.
    """
    return {
        "usage": "ws://<host>/ws/chat/{user_id}, send JSON {'message': <message>, 'to': <user_id>}, echo is returned.",
        "hint": "No authentication in stub. In production, pass token as query param or header."
    }

# ---- Entrypoint for local testing and preview (enables backend preview for cloud/dev environments) ----
if __name__ == "__main__":
    # Use 0.0.0.0 so containerized/cloud envs work
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=3001, reload=True)
