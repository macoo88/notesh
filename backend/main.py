from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel


from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



########## ----------------------
## H A S H E R
import bcrypt

def hash_password(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
#############-------------
######H A S H E R   __ END



# 1. Database Setup (SQLite)
DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

####---------------------------------------------------------
############## M O D E L S

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # This links the user to their notes
    notes = relationship("NoteModel", back_populates="owner")

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


# 2. Database Model (How it looks in SQLite)
class NoteModel(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id")) # <--- Link!

    owner = relationship("UserModel", back_populates="notes")

# What the user sends TO you (POST)
class NoteCreate(BaseModel):
    title: str
    content: str

# What you send BACK to the user (GET)
class NoteView(NoteCreate):
    id: int # Now the ID is included!

    class Config:
        from_attributes = True

#####------------------------------------------------------------
##################### M O D E L S __ END

Base.metadata.create_all(bind=engine)

# 3. Pydantic Schema (How it looks in JSON)
class NoteSchema(BaseModel):
    title: str
    content: str

    class Config:
        from_attributes = True

# 4. FastAPI App
app = FastAPI()


## 1. Create a session manually
#db = SessionLocal()
#
#try:
#    # 2. Create the note
#    # Pro-tip: Don't manually set id=1. Let SQLite do it automatically!
#    new_note = NoteModel(title="My First Note", content="This is the content!")
#    
#    # 3. Add and commit
#    db.add(new_note)
#    db.commit()
#    print("Note saved successfully!")
#except Exception as e:
#    print(f"Oops, something went wrong: {e}")
#finally:
#    # 4. Always close it!
#    db.close()



# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#####---------------------------------
## U S E R S __ A Ps

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash the password!
    new_user = UserModel(
        username=user.username, 
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "id": new_user.id}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 1. Find the user
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid Username")

    # 2. Check the password using our helper from earlier
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong Password, mate.")

    return {"message": "Login successful", "user_id": db_user.id}


########----------------------------------
######## N O T E S __ A Ps

@app.get("/")
def read_root():
    return {"message": "hello"}

##################
## Get all notes ##
#############
@app.get("/notes/", response_model=list[NoteView]) # It returns a LIST of notes
def get_notes(db: Session = Depends(get_db)):
    return db.query(NoteModel).all()


#####################
##  Get note via its ID ##
############################
@app.get("/notes/{note_id}", response_model=NoteView)
def get_note(note_id: int, db: Session = Depends(get_db)):
    # .first() grabs the one result, or None if it doesn't exist
    
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found, mate.") 
    return note



# Create a note
@app.post("/notes/", response_model=NoteView) # It will return the note WITH the new ID
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    # We turn the 'note' (Schema) into a 'new_note' (Model)
    db_note = NoteModel(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note) # This gets the ID that SQLite just generated
    return db_note
