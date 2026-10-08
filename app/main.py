from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
import os

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base, engine, get_db, async_session_factory
from .models import Advertisement, User
from .schemas import (
    AdvertisementCreate, 
    AdvertisementResponse, 
    AdvertisementUpdate,
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

from .auth import create_access_token, verify_password, get_current_user, get_current_user_optional, hash_password, get_current_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    admin_username = os.getenv(
        "ADMIN_USERNAME",
        "admin",
    )

    admin_password = os.getenv(
        "ADMIN_PASSWORD",
        "admin12345",
    )

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(
                User.username == admin_username
            )
        )

        admin = result.scalar_one_or_none()

        if admin is None:
            admin = User(
                username=admin_username,
                password_hash=hash_password(
                    admin_password
                ),
                group="admin",
            )

            session.add(admin)
            await session.commit()

    yield

    await engine.dispose()


app = FastAPI(
    title="Advertisement API",
    description="REST API для объявлений",
    version="2.0.0",
    lifespan=lifespan,
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "Advertisement API работает"
    }


# ============================================================
# AUTHENTICATION
# ============================================================

@app.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.username == login_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None or not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    token = create_access_token(user)

    return {
        "token": token,
    }


# ============================================================
# USERS
# ============================================================

@app.post("/user", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(
        get_current_user_optional
    ),
):
    
    # Обычный пользователь или неавторизованный клиент
    # может создать только пользователя группы user.
    #
    # Создать admin может только существующий admin.

    if (
        user_data.group.value == "admin"
        and (
            current_user is None
            or current_user.group != "admin"
        )
    ):
        raise HTTPException(
            status_code=403,
            detail="Only admin can create admin users",
        )

    result = await db.execute(
        select(User).where(
            User.username == user_data.username
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    user = User(
        username=user_data.username,
        password_hash=hash_password(
            user_data.password
        ),
        group=user_data.group.value,
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


@app.get("/user", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    result = await db.execute(select(User))

    return result.scalars().all()


@app.get("/user/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


@app.patch("/user/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # user может менять только себя
    # admin может менять любого пользователя

    if (
        current_user.group != "admin"
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can update only yourself",
        )

    update_data = user_data.model_dump(exclude_unset=True)      
    # При изменении данных пользователя, мы используем метод model_dump с параметром exclude_unset=True, 
    # чтобы получить только те поля, которые были изменены в запросе. 
    # Это позволяет нам обновлять только те поля, которые были предоставлены в запросе, 
    # и оставлять остальные поля без изменений.          
    
    # Только admin может менять группу пользователя
    if (
        "group" in update_data
        and current_user.group != "admin"
    ):
        
        raise HTTPException(
            status_code=403,
            detail="Only admin can change user group",
        )

    # Пароль хранится только в виде хеша
    if "password" in update_data:
        user.password_hash = hash_password(
            update_data.pop("password")
        )

    # Enum UserGroup превращаем в строку
    if "group" in update_data:
        update_data["group"] = (
            update_data["group"].value
        )

    # Проверяем, что новый username не конфликтует
    # с уже существующим пользователем.
    if "username" in update_data:
        result = await db.execute(
            select(User).where(
                User.username
                == update_data["username"],
                User.id != user_id,
            )
        )

        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )
        

    # Обновляем данные
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


@app.delete("/user/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.group == "admin":
        admins = await db.execute(select(User).where(User.group == "admin"))
        if len(admins.scalars().all()) <= 1:
            raise HTTPException(
                status_code=403,
                detail="Cannot delete the last admin",
            )

    if (
        current_user.group != "admin"
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can delete only yourself",
        )

    await db.delete(user)
    await db.commit()

    return {
        "message": "User deleted"
    }


# ============================================================
# ADVERTISEMENTS
# ============================================================

@app.get("/advertisement/{advertisement_id}", response_model=AdvertisementResponse)
async def get_advertisement(
    advertisement_id: int,
    db: AsyncSession = Depends(get_db)):

    advertisement = await db.get(Advertisement, advertisement_id)
    if not advertisement:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    return advertisement


@app.post("/advertisement", response_model=AdvertisementResponse, )
async def create_advertisement(
    advertisement: AdvertisementCreate,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)):

    new_advertisement = Advertisement(
        title=advertisement.title,
        description=advertisement.description,
        price=advertisement.price,
        author=advertisement.author,
        owner_id=current_user.id,
    )

    db.add(new_advertisement)

    await db.commit()
    await db.refresh(new_advertisement)
    return new_advertisement


@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(
    advertisement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    
    advertisement = await db.get(
        Advertisement,
        advertisement_id,
    )

    if advertisement is None:
        raise HTTPException(
            status_code=404,
            detail="Advertisement not found",
        )

    if (
        current_user.group != "admin"
        and advertisement.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can delete only your own advertisements",
        )

    await db.delete(advertisement)
    await db.commit()

    return {
        "message": "Advertisement deleted",
    }


@app.patch("/advertisement/{advertisement_id}", response_model=AdvertisementResponse)
async def update_advertisement(
    advertisement_id: int,
    advertisement_data: AdvertisementUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)):
    
    advertisement = await db.get(
        Advertisement,
        advertisement_id,
    )

    if advertisement is None:
        raise HTTPException(
            status_code=404,
            detail="Advertisement not found",
        )

    if (
        current_user.group != "admin"
        and advertisement.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can update only your own advertisements",
        )

    update_data = advertisement_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(advertisement, field, value)

    await db.commit()
    await db.refresh(advertisement)

    return advertisement


@app.get("/advertisement", response_model=list[AdvertisementResponse])
async def search_advertisements(
    title: str | None = None,
    description: str | None = None,
    author: str | None = None,
    price: int | None = None,
    created_at: date | None = None,
    db: AsyncSession = Depends(get_db)):

    query = select(Advertisement)

    if title is not None:
        query = query.where(
            Advertisement.title.ilike(
                f"%{title}%"
            )
        )

    if description is not None:
        query = query.where(
            Advertisement.description.ilike(
                f"%{description}%"
            )
        )

    if author is not None:
        query = query.where(
            Advertisement.author.ilike(
                f"%{author}%"
            )
        )

    if price is not None:
        query = query.where(
            Advertisement.price == price
        )


    if created_at is not None:
        start_of_day = datetime.combine(
            created_at,
            time.min,
            tzinfo=timezone.utc,
        )

        start_of_next_day = start_of_day + timedelta(days=1)

        query = query.where(
            Advertisement.created_at >= start_of_day,
            Advertisement.created_at < start_of_next_day,
        )


    result = await db.execute(query)

    return result.scalars().all()