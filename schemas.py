import pydantic as _pydantic


class _UserBase(_pydantic.BaseModel):
    email: str


class UserCreate(_UserBase):
    hashed_password: str

    class Config:
        orm_mode = True


class User(_UserBase):
    id: int

    class Config:
        orm_mode = True


class _TaskBase(_pydantic.BaseModel):
    state: str
    title: str
    description: str
    priority: str


class TaskCreate(_TaskBase):
    pass


class Task(_TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
