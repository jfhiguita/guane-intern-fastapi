"""dogs handler"""

#standard libraries
from datetime import datetime

#typing
from typing import List

#fastapi
from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.params import Path

# auth
from ..auth.bearer import JWTBearer

# functions to be implement
from .crud import get_dog, post_dog, get_all, get_dog_adopted, put_dog, delete_dog
from .models import DogDB, DogSchema
from .utils import get_picture
from app.users.crud import get_user_id

# celery task
from worker import create_task


router = APIRouter()

# create dog
@router.post("/{name}", dependencies=[Depends(JWTBearer())], response_model=DogDB, response_model_exclude_unset=True, status_code=201)
async def create_dog(*,
    name: str = Path(..., title="Name of the user", min_length=3, max_length=50),
    payload: DogSchema
    ):

    # validate foreign key
    if await get_user_id(payload.id_user) is None:
        raise HTTPException(status_code=404, detail="User not found")

    # async task
    create_task.delay(name)

    dog_picture = await get_picture()
    dog_create_date = datetime.now()
    dog_id = await post_dog(name, payload, dog_picture, dog_create_date)

    response_object = {
        "id": dog_id,
        "id_user": payload.id_user,
        "name": name,
        "picture": dog_picture,
        "is_adopted": payload.is_adopted,
        "create_date": dog_create_date,
    }

    return response_object

# get all
@router.get("/", response_model=List[DogDB], response_model_exclude_unset=True)
async def dogs():
    
    return await get_all()

# get is_adopted
@router.get("/is_adopted", response_model=List[DogDB], response_model_exclude_unset=True)
async def dogs_adopted():
    
    return await get_dog_adopted()    

# get dog for name
@router.get("/{name}", response_model=DogDB, response_model_exclude_unset=True)
async def dog_name(name: str):
    dog = await get_dog(name)

    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    
    return dog

# update
@router.put("/{name}", dependencies=[Depends(JWTBearer())], response_model=DogDB, response_model_exclude_unset=True)
async def update_dog(name: str, payload: DogSchema):
    dog = await get_dog(name)
    dog = dict(dog.items())

    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")

     # validate foreign key
    if await get_user_id(payload.id_user) is None:
        raise HTTPException(status_code=404, detail="User not found")

    dog_id = await put_dog(name, payload)

    response_object = {
        "id": dog_id,
        "id_user": payload.id_user,
        "name": name,
        "picture": dog["picture"],
        "is_adopted": payload.is_adopted,
        "create_date": dog["create_date"],
    }

    return response_object

# delete
@router.delete("/{name}", response_model=DogDB, response_model_exclude_unset=True)
async def delete_dog(name: str):
    dog = await get_dog(name)

    if not dog:
        raise HTTPException(status_code=404, detail="Dog not found")

    await delete_dog(name)

    return dog
