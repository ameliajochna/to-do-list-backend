import passlib
from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (PrimaryKeyConstraint('id', name='users_pkey'), UniqueConstraint('email', name='users_email_key'))

    id = Column(Integer)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)

    tasks = relationship('Tasks', back_populates='owner')

    def verify_password(self, password: str):
        return passlib.hash.bcrypt.verify(password, self.hashed_password)


class Tasks(Base):
    __tablename__ = 'tasks'
    __table_args__ = (
        ForeignKeyConstraint(['owner_id'], ['users.id'], name='tasks_owner_id_fkey'),
        PrimaryKeyConstraint('id', name='tasks_pkey'),
    )

    id = Column(Integer)
    owner_id = Column(Integer, nullable=False)
    state = Column(String(8), nullable=False)
    priority = Column(String(6), nullable=False)
    title = Column(String(255))
    description = Column(String(255))

    owner = relationship('Users', back_populates='tasks')
