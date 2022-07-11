from sqlalchemy import Column, Integer, String, Boolean, DATETIME
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app import Base
from app.users.profiles.profiles import Profile
from app.associations import association_account_connection


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    platform_id = Column(String)
    type = Column(String)
    credentials = Column(JSONB)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    active_flag = Column(Boolean)
    created_at = Column(DATETIME)
    updated_at = Column(DATETIME)

    profile = relationship(Profile, uselist=False)

    connections = relationship('Connection', secondary=association_account_connection,
                               back_populates='accounts')

    def update(self, other):
        if other.platform_id:
            self.platform_id = other.platform_id
        if other.type:
            self.type = other.type
        if other.credentials:
            self.credentials = other.credentials
        if other.username:
            self.username = other.username
        if other.email:
            self.email = other.email
        if other.password:
            self.password = other.password
        if other.active_flag:
            self.active_flag = other.active_flag
        if other.created_at:
            self.created_at = other.created_at
        if other.updated_at:
            self.updated_at = other.updated_at
