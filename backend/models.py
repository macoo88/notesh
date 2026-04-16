from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
# Assuming your 'Base' is defined in a 'database.py' file:
from database import Base

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


# 2. Database Model (How it looks in SQLite)
class NoteModel(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id")) # <--- Link!

    owner = relationship("UserModel", back_populates="notes")


#####------------------------------------------------------------
##################### M O D E L S __ END
