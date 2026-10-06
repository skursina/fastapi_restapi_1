from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base, engine, get_db
from .models import Advertisement
from .schemas import (AdvertisementCreate, AdvertisementResponse, AdvertisementUpdate)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    yield

    await engine.dispose()


app = FastAPI(
    title="Advertisement API",
    description="REST API для объявлений",
    version="1.0.0",
    lifespan=lifespan,
)


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
    db: AsyncSession = Depends(get_db), ):

    new_advertisement = Advertisement(
        title=advertisement.title,
        description=advertisement.description,
        price=advertisement.price,
        author=advertisement.author,
    )

    db.add(new_advertisement)

    await db.commit()
    await db.refresh(new_advertisement)
    return new_advertisement


@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(
    advertisement_id: int,
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

    await db.delete(advertisement)
    await db.commit()

    return {
        "message": "Advertisement deleted",
    }


@app.patch("/advertisement/{advertisement_id}", response_model=AdvertisementResponse)
async def update_advertisement(
    advertisement_id: int,
    advertisement_data: AdvertisementUpdate,
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