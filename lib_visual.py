from lib_database import *
from sqlalchemy import func, desc
from sqlalchemy.orm import  Session
from datetime import  date, timedelta

import numpy as np
import pandas as pd

import plotly.graph_objects as go
import streamlit as st
import io


#параметры

@st.experimental_memo(ttl=24*60*60)
def time_upd():
    with Session(engine) as session:
        q = session.query(PortCall.arrival).order_by(desc(PortCall.arrival)).first()
    return 'Дата последней подгрузки данных: **' + str(q[0]).split(' ')[0] + '**'


@st.experimental_memo(ttl=24*60*60)
def basins():
    with Session(engine) as session:
        q = session.query(Port.basin).group_by(Port.basin).all()
        df = pd.DataFrame(q)
    return df


@st.experimental_memo(ttl=24*60*60)
def ship_types():
    with Session(engine) as session:
        q = session.query(Ship.type).group_by(Ship.type).order_by(Ship.type).all()
        df = pd.DataFrame(q)
    return df


@st.experimental_memo(ttl=24*60*60)
def ship_flags():
    with Session(engine) as session:
        q = session.query(Ship.flag).group_by(Ship.flag).order_by(Ship.flag).all()
        df = pd.DataFrame(q)
    return df

#визуализация

@st.experimental_memo(ttl=24*60*60)
def ship_call_dynamics(date_from, date_to, basin, ship_type, ship_flag):
    with Session(engine) as session:
        query = session.query(
                            Port.basin, 
                            func.date_trunc('day', PortCall.arrival).label('day'),
                            func.count(PortCall.arrival).label('Количество судозаходов')).\
                        join(Port, PortCall.port_id == Port.id).\
                        join(Ship, PortCall.ship_id == Ship.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(PortCall.ship_id != None).\
                        group_by(Port.basin, 'day').\
                        order_by('day')

        df = pd.read_sql(query.statement, query.session.bind)

    piv = pd.pivot_table(
        df,
        index=['day'],
        values=['Количество судозаходов'],
        columns=['Бассейн',],
        aggfunc=[np.sum],
        fill_value=0
    )

    df = pd.DataFrame(piv)

    fig = go.Figure()
    fig.update_xaxes(range=[date_from, date_to])
    for i in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[i],
                name=i[2]
            )
        )

    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01),
        margin=dict(l=0, r=0, t=20, b=20),
        height = 350
        )
    fig.update_traces(hoverinfo="text", hovertemplate="Дата: %{x}<br>Кол-во судов: %{y}")
    
    return fig


@st.experimental_memo(ttl=24*60*60)
def heat_map_ship_call_dynamics(date_from, date_to, ship_type, ship_flag):
    with Session(engine) as session:
        query = session.query(
                            Port.basin, 
                            func.date_trunc('day', PortCall.arrival).label('day'),
                            func.count(PortCall.arrival).label('Количество судозаходов')
                        ).\
                        join(Ship, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to).\
                        group_by(Port.basin, 'day').\
                        order_by('day')

        df = pd.read_sql(query.statement, query.session.bind)

    piv = pd.pivot_table(
        df,
        index=['day'],
        values=['Количество судозаходов'],
        columns=['Бассейн',],
        aggfunc=[np.sum],
        fill_value=0
    )

    df = pd.DataFrame(piv)
    
    fig = go.Figure(
        go.Heatmap(
                z = df.T,
                x = df.index,
                y=[c[2] for c in df.columns],
                name = ''
            )
        )
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=20),
        height = 300
        )
    fig.update_traces(hoverinfo="text", hovertemplate="Дата: %{x}<br>Бассейн: %{y}<br>Кол-во судов: %{z}")

    return fig


@st.experimental_memo(ttl=24*60*60)
def tonnage_histogram(date_from, date_to, basin, ship_type, ship_flag):
    with Session(engine) as session:
        query = session.query(Ship.tonnage).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(Ship.tonnage != None).\
                        filter(Ship.tonnage != 0).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to)

        df = pd.read_sql(query.statement, query.session.bind)

    fig = go.Figure(go.Histogram(x=df['Регист. вместим. валовая [т]']))
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis_title="Регист. вместим. валовая [т]",
        yaxis_title="частота заданной вместимости", 
        )
    
    return fig


@st.experimental_memo(ttl=24*60*60)
def age__histogram(date_from, date_to, basin, ship_type, ship_flag):
    with Session(engine) as session:
        query = session.query((date.today().year - Ship.year).label('Возраст')).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(Ship.year != None).\
                        filter(Ship.year != 0).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to)

        df = pd.read_sql(query.statement, query.session.bind)
    fig = go.Figure(go.Histogram(x=df['Возраст']))
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis_title="возраст корабля",
        yaxis_title="частота заданного возраста", 
        )
    
    return fig


@st.experimental_memo(ttl=24*60*60)
def ship_type_pie(date_from, date_to, basin, ship_flag, pie):
    with Session(engine) as session:
        query = session.query(
                            Ship.type,
                            func.count(Ship.type).label('Количество')
                            ).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to).\
                        group_by(Ship.type).\
                        order_by(desc('Количество')) #                      

        df1 = pd.read_sql(query.statement, query.session.bind)

        query = session.query(
                            Ship.type,
                            func.count(Ship.type).label('Количество')
                            ).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from - timedelta(days=365)).\
                        filter(PortCall.arrival <= date_to - timedelta(days=365)).\
                        group_by(Ship.type).\
                        order_by(desc('Количество'))

        df2 = pd.read_sql(query.statement, query.session.bind)

    num_types = min(df1['Тип судна'].unique().shape[0], df2['Тип судна'].unique().shape[0])
    n = pie.selectbox('Точность', list(range(1, num_types+1)), min (5, num_types)-1)

    df1 = df1.dropna().head(n).append(df1.tail(df1.shape[0] - n).sum(), ignore_index=True)
    df1.at[n, 'Тип судна'] = 'ДРУГОЕ'

    df2 = df2.dropna().head(n).append(df2.tail(df2.shape[0] - n).sum(), ignore_index=True)
    df2.at[n, 'Тип судна'] = 'ДРУГОЕ'

    #внешний, сейчас
    trace1 =  go.Pie(
            values=df1['Количество'],
            labels=df1['Тип судна'],
            name="(сейчас)",
            marker = dict(line =dict(color='#000000', width=1)),
            hole=0.52,
            hoverinfo="text",
            hovertemplate="Тип судна: %{label}<br>Кол-во судов: %{value}<br>Процент: %{percent}"
    )

    #внутренний, год назад
    trace0 = go.Pie(
            values=df2['Количество'],
            labels=df2['Тип судна'],
            domain = {'x': [0.24, 0.76]},
            name="(год назад)",
            marker = dict(line =dict(color='#000000', width=1)),
            hoverinfo="text",
            hovertemplate="Тип судна: %{label}<br>Кол-во судов: %{value}<br>Процент: %{percent}",
            #hole=0.02
            )

    data = [trace1, trace0]
    fig = go.Figure(data=data)
    fig.update_layout(
        margin=dict(l=20, r=20, t=0, b=0)
    )
    fig.update(
        layout_showlegend=False
    )

    return fig


@st.experimental_memo(ttl=24*60*60)
def ship_flag_pie(date_from, date_to, basin, ship_type, pie):
    with Session(engine) as session:
        query = session.query(
                            Ship.flag,
                            func.count(Ship.flag).label('Количество')
                            ).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to).\
                        group_by(Ship.flag).\
                        order_by(desc('Количество'))

        df1 = pd.read_sql(query.statement, query.session.bind)
    
    with Session(engine) as session:
        query = session.query(
                            Ship.flag,
                            func.count(Ship.flag).label('Количество')
                            ).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from - timedelta(days=365)).\
                        filter(PortCall.arrival <= date_to - timedelta(days=365)).\
                        group_by(Ship.flag).\
                        order_by(desc('Количество'))

        df2 = pd.read_sql(query.statement, query.session.bind)

    num_types = min(df1['Флаг судна'].unique().shape[0], df2['Флаг судна'].unique().shape[0])
    n = pie.selectbox('Точность', list(range(1, num_types+1)), min (5, num_types)-1)

    df1 = df1.dropna().head(n).append(df1.tail(df1.shape[0] - n).sum(), ignore_index=True)
    df1.at[n, 'Флаг судна'] = 'ДРУГОЕ'

    df2 = df2.dropna().head(n).append(df2.tail(df2.shape[0] - n).sum(), ignore_index=True)
    df2.at[n, 'Флаг судна'] = 'ДРУГОЕ'

    #внешний, сейчас
    trace1 =  go.Pie(
            values=df1['Количество'],
            labels=df1['Флаг судна'],
            name="(сейчас)",
            marker = dict(line =dict(color='#000000', width=1)),
            hole=0.52,
            hoverinfo="text",
            hovertemplate="Флаг  судна: %{label}<br>Кол-во судов: %{value}<br>Процент: %{percent}"
    )

    #внутренний, год назад
    trace0 = go.Pie(
            values=df2['Количество'],
            labels=df2['Флаг судна'],
            domain = {'x': [0.24, 0.76]},
            name="(год назад)",
            marker = dict(line =dict(color='#000000', width=1)),
            hoverinfo="text",
            hovertemplate="Флаг судна: %{label}<br>Кол-во судов: %{value}<br>Процент: %{percent}",
            )

    data = [trace1, trace0]
    fig = go.Figure(data=data)
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10)
    )
    fig.update(
        layout_showlegend=False
    )

    return fig


@st.experimental_memo(ttl=24*60*60)
def length_histogram(date_from, date_to, basin, ship_type, ship_flag):
    with Session(engine) as session:
        query = session.query(Ship.length).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(Ship.length != None).\
                        filter(Ship.length != 0).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to)

        df = pd.read_sql(query.statement, query.session.bind)

    fig = go.Figure(go.Histogram(x=df['Длина наибольшая [м]']))
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis_title="Длина наибольшая [м]",
        yaxis_title="частота заданной длины", 
        )
    
    return fig


@st.experimental_memo(ttl=24*60*60)
def width_histogram(date_from, date_to, basin, ship_type, ship_flag):
    with Session(engine) as session:
        query = session.query(Ship.width).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(Ship.width != None).\
                        filter(Ship.width != 0).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to)

        df = pd.read_sql(query.statement, query.session.bind)

    fig = go.Figure(go.Histogram(x=df['Ширина наибольшая [м]']))
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=20),
        xaxis_title="Ширина наибольшая [м]",
        yaxis_title="частота заданной ширины", 
        )
    
    return fig


@st.experimental_memo(ttl=24*60*60)
def most_popular(date_from, date_to, basin, ship_type, ship_flag, head=5):
    with Session(engine) as session:
        query = session.query(
                            Ship.imo,
                            Ship.name_en,
                            Ship.name_ru,
                            Ship.name_call,
                            Ship.type,
                            Ship.year,
                            Ship.flag,
                            Ship.port_reg,
                            Ship.length,
                            Ship.width,
                            Ship.tonnage,
                            Ship.mmsi,
                            Ship.proprietors,
                            Ship.owners,
                            func.count(PortCall.arrival).label('Количество судозаходов')
                        ).\
                        join(PortCall, PortCall.ship_id == Ship.id).\
                        join(Port, PortCall.port_id == Port.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(Ship.isnt_none_ship == True).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to).\
                        group_by(
                            Ship.imo,
                            Ship.type,
                            Ship.name_en,
                            Ship.name_call,
                            Ship.name_ru,
                            Ship.year,
                            Ship.flag,
                            Ship.port_reg,
                            Ship.length,
                            Ship.width,
                            Ship.tonnage,
                            Ship.mmsi,
                            Ship.proprietors,
                            Ship.owners,
                        ).\
                        order_by(desc('Количество судозаходов'))
        df = pd.read_sql(query.statement, query.session.bind)

    return df.head(head)
                        
#другое

def make_excel(date_from, date_to, basin, ship_type, ship_flag):
    buffer = io.BytesIO()

    with Session(engine) as session:
        query = session.query(
                            Ship.imo,
                            Ship.type,
                            Ship.name_en,
                            Ship.name_call,
                            Ship.name_ru,
                            Ship.year,
                            Ship.flag,
                            Ship.port_reg,
                            Ship.length,
                            Ship.width,
                            Ship.tonnage,
                            Ship.mmsi,
                            Ship.proprietors,
                            Ship.owners,
                            Port.basin,
                            PortCall.port_call,
                            func.date_trunc('day', PortCall.arrival).label('day'),
                            func.count(PortCall.arrival).label('Количество судозаходов')).\
                        join(Port, PortCall.port_id == Port.id).\
                        join(Ship, PortCall.ship_id == Ship.id).\
                        filter(Port.basin.in_(tuple(basin))).\
                        filter(Ship.flag.in_(tuple(ship_flag))).\
                        filter(Ship.type.in_(tuple(ship_type))).\
                        filter(PortCall.ship_id != None).\
                        filter(PortCall.arrival >= date_from).\
                        filter(PortCall.arrival <= date_to).\
                        group_by(
                            'day',
                            Ship.imo,
                            Ship.type,
                            Ship.name_en,
                            Ship.name_call,
                            Ship.name_ru,
                            Ship.year,
                            Ship.flag,
                            Ship.port_reg,
                            Ship.length,
                            Ship.width,
                            Ship.tonnage,
                            Ship.mmsi,
                            Ship.proprietors,
                            Ship.owners,
                            Port.basin,
                            PortCall.port_call
                         ).\
                        order_by('day')

        df = pd.read_sql(query.statement, query.session.bind)

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    st.sidebar.download_button(
        label="скачать Excel",
        data=buffer,
        file_name="portcall.xlsx",
        mime="application/vnd.ms-excel"
    )