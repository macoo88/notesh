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


class ClassModel(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    invite_code = Column(String, unique=True) # Like a Discord invite link
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    members = relationship("UserModel", secondary=user_classes, back_populates="joined_classes")



#class NoteModel(Base):
#    __tablename__ = "notes"
#    id = Column(Integer, primary_key=True, index=True)
#    title = Column(String)
#    content = Column(Text)
#    subject = Column(String) # e.g., "Math"
#    topic = Column(String)   # e.g., "Calculus"
#    image_path = Column(String, nullable=True) # For your "Notes as Photos" goal
#    owner_id = Column(Integer, ForeignKey("users.id"))

#####------------------------------------------------------------
##################### M O D E L S __ END
