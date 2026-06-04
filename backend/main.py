import os
import random
import shutil
import string
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from sqlalchemy.orm import Session, relationship, sessionmaker

import auth
import models
import schemas
from auth import ALGORITHM, SECRET_KEY
from database import Base, SessionLocal, engine, get_db

# Inicializácia databázy
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()

# Povolenie CORS pre spojenie s frontendom
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # V produkcii zmeň na konkrétnu URL adresu frontendu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nastavenie OAuth2 schémy pre hľadanie tokenu v "/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Dekódovanie tokenu
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        
        if username is None or user_id is None:
            raise HTTPException(status_code=400, detail="credentials_exception")
            
    except JWTError:
        raise HTTPException(status_code=400, detail="credentials_exception")

    # 2. Vyhľadanie používateľa v databáze
    user = db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user


os.makedirs("uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="uploads"), name="static")


#####---------------------------------
## U S E R S __ A Ps

@app.get("/users/me", response_model=schemas.UserView)
def read_users_me(current_user: models.UserModel = Depends(get_current_user)):
    return current_user


@app.get("/users/me/classes")
def get_my_classes(current_user: models.UserModel = Depends(get_current_user)):
    return current_user.joined_classes


@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.UserModel).filter(models.UserModel.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if db.query(models.UserModel).filter(models.UserModel.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.password != user.again_password:
        raise HTTPException(status_code=401, detail="The passwords do not match")

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
    
    print(f"DEBUG: Verification code for {user.email} is {code}")
    
    return {
        "message": "User created", 
        "debug_code": code, 
        "username": user.username
    }


@app.post('/verify')
def verify_code(user: schemas.UserVerify, db: Session = Depends(get_db)):
    user_indb = db.query(models.UserModel).filter(models.UserModel.username == user.username).first()
    
    if not user_indb:
        raise HTTPException(status_code=404, detail="User not found")

    if user_indb.is_verified:
        return {"Username": user_indb.username, "Message": "user already verified"}

    if user_indb.verification_code == user.code:
        user_indb.is_verified = True
        user_indb.verification_code = None  # Vyčistenie kódu po overení
        db.commit()
        return {"message": "Verification successful! You can now login."}
    else:
        raise HTTPException(status_code=400, detail="Wrong code, try again.")


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.UserModel).filter(models.UserModel.username == form_data.username).first()
    
    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = auth.create_access_token(data={"sub": db_user.username, "id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.id}


@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    return db.query(models.UserModel).all()


#####----------------------------------
######## C L A S S E S  __ A Ps

@app.post("/classes/create")
def create_class(name: str, description: str, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    # Vygenerovanie náhodného 8-miestneho pozývacieho kódu
    invite = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    new_class = models.ClassModel(
        name=name, 
        description=description, 
        invite_code=invite, 
        owner_id=current_user.id
    )
    
    # Automatické pridanie stvoriteľa triedy medzi jej členov
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


#####----------------------------------
######## SCHEDULE (ROZVRH) APIs

@app.get("/classes/{class_id}")
def get_class_details(class_id: int, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    if current_user not in target_class.members:
        raise HTTPException(status_code=403, detail="Join the class to see details")

    return target_class


@app.get("/classes/{class_id}/schedule")
def get_class_schedule(class_id: int, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    if not target_class or current_user not in target_class.members:
        raise HTTPException(status_code=403, detail="Access denied")

    cells = db.query(models.ScheduleCellModel).filter(models.ScheduleCellModel.class_id == class_id).all()
    return cells


@app.post("/classes/{class_id}/schedule")
def update_class_schedule(
    class_id: int, 
    schedule_data: List[schemas.ScheduleCellUpdate], 
    db: Session = Depends(get_db), 
    current_user: models.UserModel = Depends(get_current_user)
):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    # Bezpečnosť: Len vlastník (tvorca) triedy môže upravovať rozvrh
    if target_class.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the class owner can modify the schedule")

    # Vymazanie starého rozvrhu pre danú triedu, aby nevznikali duplicity
    db.query(models.ScheduleCellModel).filter(models.ScheduleCellModel.class_id == class_id).delete()

    # Hromadný zápis nových buniek rozvrhu
    for cell in schedule_data:
        new_cell = models.ScheduleCellModel(
            class_id=class_id,
            day=cell.day,
            period=cell.period,
            subject_name=cell.subject_name if cell.subject_name and cell.subject_name.strip() else None
        )
        db.add(new_cell)
        
    db.commit()
    return {"message": "Schedule updated successfully!"}


#####----------------------------------
######## SUBJECTS & NOTES APIs

@app.get("/classes/{class_id}/subjects")
def get_class_subjects(class_id: int, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    if not target_class or current_user not in target_class.members:
        raise HTTPException(status_code=403, detail="Access denied")

    # Získanie unikátnych a neprázdnych názvov predmetov priamo z buniek rozvrhu matice
    subjects = db.query(models.ScheduleCellModel.subject_name).\
        filter(models.ScheduleCellModel.class_id == class_id, models.ScheduleCellModel.subject_name != None).\
        distinct().all()
        
    return [s[0] for s in subjects]


@app.get("/classes/{class_id}/notes", response_model=List[schemas.NoteView])
def get_class_notes(class_id: int, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    if current_user not in target_class.members:
        raise HTTPException(status_code=403, detail="Join the class to see notes")

    return target_class.notes


@app.get("/classes/{class_id}/notes/{subject}", response_model=List[schemas.NoteView])
def get_class_subject_notes(class_id: int, subject: str, db: Session = Depends(get_db), current_user: models.UserModel = Depends(get_current_user)):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    if current_user not in target_class.members:
        raise HTTPException(status_code=403, detail="Join the class to see notes")

    filtered_notes = db.query(models.NoteModel).filter(
        models.NoteModel.class_id == class_id,
        models.NoteModel.subject == subject
    ).all()

    return filtered_notes


@app.post("/classes/{class_id}/notes")
def create_note_json(
    class_id: int,
    note_data: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
    if current_user not in target_class.members:
        raise HTTPException(status_code=403, detail="Access denied")

    new_note = models.NoteModel(
        title=note_data.title,
        content=note_data.content,
        class_id=class_id,
        owner_id=current_user.id,
        subject=note_data.subject,
        image_path=None
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@app.post("/classes/{class_id}/notes-with-image")
def create_note_with_image(
    class_id: int,
    title: str = Form(...),
    content: Optional[str] = Form(""),
    subject: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    target_class = db.query(models.ClassModel).filter(models.ClassModel.id == class_id).first()
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    if current_user not in target_class.members:
        raise HTTPException(status_code=403, detail="Access denied")

    saved_path = None

    # Spracovanie a fyzické uloženie nahraného súboru
    if image and image.filename:
        clean_filename = image.filename.replace(" ", "_")
        filename = f"{class_id}_{current_user.id}_{clean_filename}"
        
        # 1. Zápis súboru na disk do priečinka 'uploads'
        file_location = f"uploads/{filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        # 2. Relatívna cesta pre frontend prístupná cez app.mount
        saved_path = f"static/{filename}"

    # Vytvorenie a zápis záznamu poznámky s obrázkom do DB
    new_note = models.NoteModel(
        title=title,
        content=content if content else "",
        class_id=class_id,
        owner_id=current_user.id,
        subject=subject,
        image_path=saved_path
    )
    
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return {"message": "Note with image saved!", "image_path": saved_path}


@app.put("/classes/{class_id}/notes/{note_id}", response_model=schemas.NoteView)
def update_note(
    class_id: int,
    note_id: int,
    note_data: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.UserModel = Depends(get_current_user)
):
    note = db.query(models.NoteModel).filter(
        models.NoteModel.id == note_id, 
        models.NoteModel.class_id == class_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own notes")

    # Aktualizácia dát poznámky
    note.title = note_data.title
    note.content = note_data.content
    note.subject = note_data.subject

    db.commit()
    db.refresh(note)
    return note


@app.get("/")
def read_root():
    return {"message": "hello"}
