from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import relationship

from fastapi.middleware.cors import CORSMiddleware

import models
import schemas

from database import SessionLocal, engine, Base, get_db
import auth
import random, string


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# This tells FastAPI: "Look for a token at the /login endpoint"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()


#allow all connections ?
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change "*" to his specific URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        
        if username is None or user_id is None:
            raise HTTPException(status_code=400, detail="credentials_exception")
            
    except JWTError:
        raise HTTPException(status_code=400, detail="credentials_exception")

    # 2. Find the actual user in the DB
    user = db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user # This returns the full User object!#####---------------------------------
## U S E R S __ A Ps
@app.get("/users/me", response_model=schemas.UserView) # Use a schema to filter sensitive data
def read_users_me(current_user: models.UserModel = Depends(get_current_user)):
    return current_user
@app.get("/users/me/classes")
def get_my_classes(current_user: UserModel = Depends(get_current_user)):
    return current_user.joined_classes



@app.post("/register")# register ---------------------------------------- register
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    if db.query(models.UserModel).filter(models.UserModel.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(models.UserModel).filter(models.UserModel.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.password != user.again_password:
        raise HTTPException(status_code=401, detail="The passwords do not match") # 401 ?


    code = auth.generate_code()
    
    new_user = models.UserModel(
        username=user.username,
        email=user.email,
        hashed_password=auth.hash_password(user.password),
        verification_code=code,
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    
    # 3. TODO: send mails maybe ? 
    print(f"DEBUG: Verification code for {user.email} is {code}")
    
    
    return {
        "message": "User created", 
        "debug_code": code, 
        "username": user.username
    }

@app.post('/verify')
def verify_code(user: schemas.UserVerify, db:Session = Depends(get_db)):
    # use user.password as the verifycation code
    user_indb = db.query(models.UserModel).filter(models.UserModel.username == user.username).first()
    
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
# Change 'user: UserLogin' to 'form_data: OAuth2PasswordRequestForm = Depends()'
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Now use form_data.username instead of user.username
    db_user = db.query(models.UserModel).filter(models.UserModel.username == form_data.username).first()
    
    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = auth.create_access_token(data={"sub": db_user.username, "id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.id}


@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(models.UserModel).all()


## U S E R S __ A Ps    E N D
#########---------------------------------




########----------------------------------
######## C L A S S E S  __ A Ps

@app.post("/classes/create")
def create_class(name: str, description: str, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    # Generate a random 8-character invite code
    invite = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    new_class = models.ClassModel(
        name=name, 
        description=description, 
        invite_code=invite, 
        owner_id=current_user.id
    )
    
    # Automatically add the creator as a member
    new_class.members.append(current_user)
    
    db.add(new_class)
    db.commit()
    return {"message": "Class created", "invite_code": invite}


@app.post("/classes/join/{invite_code}")
def join_class(invite_code: str, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.invite_code == invite_code).first()
    
    if not target_class:
        raise HTTPException(status_code=404, detail="Invalid invite code")
    
    if current_user in target_class.members:
        return {"message": "You are already in this class"}

    target_class.members.append(current_user)
    db.commit()
    return {"message": f"Joined {target_class.name} successfully!"}

######## C L A S S E S  __ A Ps       E N D
########----------------------------------




########----------------------------------
######## N O T E S __ A Ps

@app.get("/")
def read_root():
    return {"message": "hello"}

##################
## Get all notes ##
#############
#@app.get("/notes/", response_model=list[schemas.NoteView]) # It returns a LIST of notes
#def get_notes(db: Session = Depends(get_db)):
#    return db.query(models.NoteModel).all()
#
#
######################
###  Get note via its ID ##
#############################
#@app.get("/notes/{note_id}", response_model=schemas.NoteView)
#def get_note(note_id: int, db: Session = Depends(get_db)):
#    # .first() grabs the one result, or None if it doesn't exist
#    
#    note = db.query(models.NoteModel).filter(models.NoteModel.id == note_id).first()
#    if not note:
#        raise HTTPException(status_code=404, detail="Note not found, mate.") 
#    return note
#
#
#
## Create a note
#@app.post("/notes/", response_model=schemas.NoteView) # It will return the note WITH the new ID
#def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
#    # We turn the 'note' (Schema) into a 'new_note' (Model)
#    db_note = models.NoteModel(title=note.title, content=note.content)
#    db.add(db_note)
#    db.commit()
#    db.refresh(db_note) # This gets the ID that SQLite just generated
#    return db_note
