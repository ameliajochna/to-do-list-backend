import fastapi as _fastapi
import fastapi.security as _security
import jwt as _jwt
import sqlalchemy.orm as _orm
import passlib.hash as _hash

import database as _database, models as _models, schemas as _schemas

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl='/api/token')

JWT_SECRET = 'myjwtsecret'


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    user_obj = _models.User(email=user.email, hashed_password=_hash.bcrypt.hash(user.hashed_password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)

    token = _jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type='bearer')


async def get_current_user(db: _orm.Session = _fastapi.Depends(get_db), token: str = _fastapi.Depends(oauth2schema)):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = db.query(_models.User).get(payload['id'])
    except:
        raise _fastapi.HTTPException(status_code=401, detail='Invalid email or Password')

    return _schemas.User.from_orm(user)


async def create_task(user: _schemas.User, db: _orm.Session, task: _schemas.TaskCreate):
    task = _models.Task(**task.dict(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return _schemas.Task.from_orm(task)


async def get_tasks(user: _schemas.User, db: _orm.Session):
    tasks = db.query(_models.Task).filter_by(owner_id=user.id)

    return list(map(_schemas.Task.from_orm, tasks))


async def _task_selector(task_id: int, user: _schemas.User, db: _orm.Session):
    task = db.query(_models.Task).filter_by(owner_id=user.id).filter(_models.Task.id == task_id).first()

    if task is None:
        raise _fastapi.HTTPException(status_code=404, detail='Task does not exist')

    return task


async def get_task(task_id: int, user: _schemas.User, db: _orm.Session):
    task = await _task_selector(task_id=task_id, user=user, db=db)

    return _schemas.Task.from_orm(task)


async def delete_task(task_id: int, user: _schemas.User, db: _orm.Session):
    task = await _task_selector(task_id, user, db)
    db.delete(task)
    db.commit()


async def update_task(task_id: int, task: _schemas.TaskCreate, user: _schemas.User, db: _orm.Session):
    task_db = await _task_selector(task_id, user, db)
    task_db.state = task.state
    task_db.title = task.title
    task_db.description = task.description
    task_db.priority = task.priority

    db.commit()
    db.refresh(task_db)

    return _schemas.Task.from_orm(task_db)
