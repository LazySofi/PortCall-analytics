from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import Table
from sqlalchemy.orm import declarative_base
import streamlit as st

engine  = create_engine(
                        URL.create(**st.secrets["postgres"]),
                        )
Base = declarative_base()


class PortCall(Base):
    __table__ = Table('port display', Base.metadata,
                    autoload=True, autoload_with=engine, schema="ship_calls")
    id = __table__.c['id']
    name = __table__.c['Название судна']
    imo = __table__.c['ИМО номер']
    port_call = __table__.c['Порт захода']
    arrival = __table__.c['Дата/время захода']
    departure = __table__.c['Дата/время отхода']
    port_id = __table__.c['port_id']
    ship_id = __table__.c['ship_id']


class Port(Base):
    __table__ = Table('port', Base.metadata,
                    autoload=True, autoload_with=engine, schema="ship_calls")
    id = __table__.c['id']
    name = __table__.c['Название порта']
    code = __table__.c['Кодировка']
    basin = __table__.c['Бассейн']
    mention = __table__.c['Упоминание на сайте']


class Ship(Base):
    __table__ = Table('ship', Base.metadata,
                    autoload=True, autoload_with=engine, schema="ship_calls")
    id = __table__.c['id']
    imo = __table__.c['ИМО номер']
    type = __table__.c['Тип судна']
    name_en = __table__.c['Название судна (англ.)']
    name_call = __table__.c['Позывной']
    name_ru = __table__.c['Название судна (рус.)']
    year = __table__.c['Год постройки']
    flag = __table__.c['Флаг судна']
    port_reg = __table__.c['Порт регистрации']
    length = __table__.c['Длина наибольшая [м]']
    tonnage = __table__.c['Регист. вместим. валовая [т]']
    width = __table__.c['Ширина наибольшая [м]']
    mmsi = __table__.c['MMSI']
    proprietors = __table__.c['Собственники']
    owners = __table__.c['Владельцы']
    isnt_none_ship = __table__.c['isnt_none_ship']