import passlib.hash as _hash
import sqlalchemy as _sql
import sqlalchemy.orm as _orm

import database as db


class User(db.Base):
    __tablename__ = 'users'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    email = _sql.Column(_sql.String, unique=True, index=True)
    hashed_password = _sql.Column(_sql.String)

    tasks = _orm.relationship('Task', back_populates='owner')

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)


class Task(db.Base):
    __tablename__ = 'tasks'
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey('users.id'))
    state = _sql.Column(_sql.String, index=True)
    title = _sql.Column(_sql.String, index=True)
    description = _sql.Column(_sql.String, index=True)
    priority = _sql.Column(_sql.String, index=True, default='')

    owner = _orm.relationship('User', back_populates='tasks')
