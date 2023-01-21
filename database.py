import datetime
import random
import string

from aiogram import types
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, MetaData, ForeignKey, select, delete, \
    update
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref, Session

from config import MANAGER_ID

engine = create_engine(f"sqlite:///sqlitedb")

Base = declarative_base()
meta = MetaData(engine)
DBSession = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(String)
    membership_activate = Column(Date, nullable=True)


class Search(Base):
    __tablename__ = 'searches'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    search = Column(String)
    resent_seen_title = Column(String, nullable=True)
    creator_id = Column(Integer)


class PromoCode(Base):
    __tablename__ = 'promo_codes'

    id = Column(Integer, autoincrement=True, primary_key=True)
    key = Column(String(24))
    work_days = Column(Integer)
    used = Column(Boolean, default=False)


def create_db():
    """
    Create database
    """
    Base.metadata.create_all(engine)


async def get_searches_db():
    stmt = select(User).where(User.membership_activate >= datetime.date.today())
    members = [i.user_id for i in engine.connect().execute(stmt).fetchall()]
    members.append(MANAGER_ID)

    stmt = select(Search).where(Search.creator_id.in_(members))
    return engine.connect().execute(stmt).fetchall()


async def get_user_searches_db(user_id: int):
    stmt = select(Search).where(Search.creator_id == user_id)
    return engine.connect().execute(stmt).fetchall()


async def get_user_search_db(search_id: [int, str]):
    stmt = select(Search).where(Search.id == search_id)
    return engine.connect().execute(stmt).fetchone()


async def get_user_searches_paginate_db(user_id: int, page: int = 1, page_size: int = 10):
    stmt = select(Search).where(Search.creator_id == user_id).offset((page - 1) * page_size).limit(page_size)
    return engine.connect().execute(stmt).fetchall()


async def delete_search_db(search_id: [int, str]):
    stmt = delete(Search).where(Search.id == search_id)
    return engine.connect().execute(stmt)


async def add_search_db(search: str, user_id, name: str):
    with Session(engine) as session:
        search = Search(name=name, creator_id=user_id, search=search)
        session.add(search)
        session.commit()


async def update_resent_seen_db(search_id: int, resent_seen_title: str):
    with Session(engine) as session:
        stmt = select(Search).where(Search.id == search_id)
        search = session.scalars(stmt).one()
        if search:
            search.resent_seen_title = resent_seen_title
        session.add(search)
        session.commit()


async def get_user_db(user_id: [int, str]):
    stmt = select(User).where(User.user_id == user_id)
    return engine.connect().execute(stmt).fetchone()


async def create_user_db(user_id: int):
    with Session(engine) as session:
        user = User(user_id=user_id)
        session.add(user)
        session.commit()


async def active_promo_code(user_id: int, promo: PromoCode):
    with Session(engine) as session:
        stmt = select(User).where(User.user_id == user_id)
        user = session.scalars(stmt).one()

        if user:
            new_date = datetime.date.today() + datetime.timedelta(int(promo.work_days))
            user.membership_activate = new_date
        session.add(user)

        promo.used = True
        session.add(promo)

        session.commit()
        return new_date


async def add_promo_code_db(days: int):
    with Session(engine) as session:
        key = ''.join(random.choice(f'{string.ascii_letters}{string.digits}') for i in range(24))
        promo = PromoCode(work_days=days, key=key)
        session.add(promo)
        session.commit()

        stmt = select(PromoCode).where(PromoCode.key == key)
        promo = session.scalars(stmt).one()

    return promo


async def get_promo_codes_db():
    stmt = select(PromoCode).where(PromoCode.used == False)
    return engine.connect().execute(stmt).fetchall()


async def get_promo_code_db(promo: str):
    stmt = select(PromoCode).where(PromoCode.key == promo)
    return engine.connect().execute(stmt).fetchone()


async def get_promo_code_scalars_db(promo: str):
    with Session(engine) as session:
        stmt = select(PromoCode).where(PromoCode.key == promo)
        return session.scalars(stmt).one()
