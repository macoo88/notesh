from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
# Assuming your 'Base' is defined in a 'database.py' file:
from database import Base
from sqlalchemy import Table

# The Link Table: It just connects user IDs to class IDs
user_classes = Table(
    "user_classes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("class_id", Integer, ForeignKey("classes.id"), primary_key=True),
)

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
    #notes = relationship("NoteModel", back_populates="owner")
    joined_classes = relationship("ClassModel", secondary=user_classes, back_populates="members")
    notes = relationship("NoteModel", back_populates="owner")


class ClassModel(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    invite_code = Column(String, unique=True) # Like a Discord invite link
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    schedule_slots = relationship("ScheduleCellModel", back_populates="class_parent", cascade="all, delete-orphan")

    # Relationships
    members = relationship("UserModel", secondary=user_classes, back_populates="joined_classes")
    notes = relationship("NoteModel", back_populates="class_parent")
    
class ScheduleCellModel(Base):
    __tablename__ = "schedule_cells"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), index=True)
    day = Column(Integer)        # 1 = Monday, 2 = Tuesday, ..., 5 = Friday
    period = Column(Integer)     # 1 to 8 (The hour slot)
    subject_name = Column(String, nullable=True) # e.g., "Math" or None if empty

    # Explicit relationship back to the class
    class_parent = relationship("ClassModel", back_populates="schedule_slots")



class NoteModel(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    
    # NEW: Linking to a class
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    # Categorization for your "Subjects/Topics" goal
    subject = Column(String, default="General")
    topic = Column(String, nullable=True)
    
    # Metadata
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(String) # You can use datetime later

    owner = relationship("UserModel", back_populates="notes")
    class_parent = relationship("ClassModel", back_populates="notes")
#####------------------------------------------------------------
##################### M O D E L S __ END
