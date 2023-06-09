import fastapi
import fastapi.security as _security
import sqlalchemy.orm as _orm
from fastapi.middleware.cors import CORSMiddleware


import database
import models
import schemas
import services

models.Base.metadata.create_all(bind=database.engine)

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any source
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


app.route('/')


@app.post('/api/users')
async def create_user(user: schemas.UserCreate, db: _orm.Session = fastapi.Depends(services.get_db)):
    db_user = await services.get_user_by_email(user.email, db)
    if db_user:
        raise fastapi.HTTPException(status_code=400, detail='Email already in use')

    user = await services.create_user(user, db)

    return await services.create_token(user)


@app.post('/api/token')
async def generate_token(
    form_data: _security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    user = await services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise fastapi.HTTPException(status_code=401, detail='Invalid email or password. Please try entering it again.')

    return await services.create_token(user)


@app.get('/api/users/me', response_model=schemas.User)
async def get_user(user: schemas.User = fastapi.Depends(services.get_current_user)):
    return user


@app.post('/api/tasks', response_model=schemas.Task)
async def create_task(
    task: schemas.TaskCreate,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.create_task(user=user, db=db, task=task)


@app.get('/api/tasks', response_model=list[schemas.Task])
async def get_tasks(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.get_tasks(user=user, db=db)


@app.get('/api/tasks/{task_id}', status_code=200)
async def get_task(
    task_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.get_task(task_id, user, db)


@app.delete('/api/tasks/{task_id}', status_code=204)
async def delete_task(
    task_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.delete_task(task_id, user, db)


@app.put('/api/tasks/{task_id}', status_code=200)
async def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.update_task(task_id, task, user, db)


@app.put('/api/users/{user_id}', status_code=200)
async def update_password(
    user_id: int,
    changepassword: schemas.ChangePassword,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.update_password(user_id, changepassword, user, db)
