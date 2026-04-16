from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel


from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

import random
import string


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



def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
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
    email = Column(String, unique=True, index=True) # New!
    hashed_password = Column(String)

    is_verified = Column(Boolean, default=False) # New!

    verification_code = Column(String, nullable=True) # New!
    notes = relationship("NoteModel", back_populates="owner")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    again_password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserVerify(BaseModel):
    username: str
    code: str


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

@app.post("/register")# register ---------------------------------------- register
def register(user: UserCreate, db: Session = Depends(get_db)):

    if db.query(UserModel).filter(UserModel.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(UserModel).filter(UserModel.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.password != user.again_password:
        raise HTTPException(status_code=401, detail="The passwords do not match") # 401 ?


    code = generate_code()
    
    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        verification_code=code,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    
    # 3. TODO: send mails maybe ? 
    print(f"DEBUG: Verification code for {user.email} is {code}")
    
    return {"message": "User created. Please check your email for the code."}

@app.post('/verify')
def verify_code(user: UserVerify, db:Session = Depends(get_db)):
    # use user.password as the verifycation code
    user_indb = db.query(UserModel).filter(UserModel.username == user.username).first()
    
    if not user_indb:
        raise HTTPException(status_code=404, detail="User not found")

    if user_indb.is_verified == True:
        return {"Username":user_indb.username, "Message": "user aready verified"}

    if user_indb.verification_code == user.code:
        user_indb.is_verified = True
        user_indb.verification_code = None  # Clean up the code after use
        db.commit() # Save the change to notes.db
        return {"message": "Verification successful! You can now login."}
    else:
        raise HTTPException(status_code=400, detail="Wrong code, try again.")


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 1. Find the user
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    
    if not db_user.is_verified:
        return {"message": "You have to verify first"}

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid Username")

    # 2. Check the password
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong Password, mate.")

    return {"message": "Login successful", "user_id": db_user.id}

@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()


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
