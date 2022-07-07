import streamlit as st
from datetime import date, timedelta

from lib_visual import *


def params():

    dates = st.sidebar.columns([1, 1])
    with dates[0]:
        date_from = st.date_input('Дата с', date.today() - timedelta(days=30))
    with dates[1]:
        date_to = st.date_input('по', date.today())
    basin = st.sidebar.multiselect('Бассейн', basins(), 'Дальневосточный бассейн')
    ship_type = st.sidebar.multiselect('Тип судна', ship_types(),  '60 / General cargo/multi-purpose ship')
    ship_flag = st.sidebar.multiselect('Флаг судна', ship_flags(), 'RU - RUSSIAN FEDERATION')

    return date_from, date_to, basin, ship_type, ship_flag

def visualize_data(date_from, date_to, basin, ship_type, ship_flag):
    #график динамики
    st.subheader('Динамика судозаходов по выбранным бассейнам')
    st.plotly_chart(ship_call_dynamics(date_from, date_to, basin, ship_type, ship_flag), use_container_width=True)

    #Тепловая карта
    st.subheader('Тепловая карта судозаходов по всем бассейнам')
    st.caption('Цветом обозначена частота судозаходов. Учитываются все праметры, кроме параметра "Бассейн"')
    st.plotly_chart(heat_map_ship_call_dynamics(date_from, date_to, ship_type, ship_flag), use_container_width=True)

    #валовая вместимость в тоннах, возраст судна
    histogram01,  histogram02 = st.columns([1, 1])
    histogram01.subheader('Вместимость, в тоннах')
    histogram01.plotly_chart(tonnage_histogram(date_from, date_to, basin, ship_type, ship_flag), use_container_width=True)

    histogram02.subheader('Возраст судна')
    histogram02.plotly_chart(age__histogram(date_from, date_to, basin, ship_type, ship_flag), use_container_width=True)
    
    #типы судна и возраст судна
    pie1, pie2  = st.columns([1, 1])
    pie1.subheader('Типы судов')
    pie1.caption('Внешний круг - типы судов по заданным параметрам (Параметр "Тип судна" не учитывается).<br>'
                    'Внутренний круг - информация за аналогичный период в прошлом году<br>'
                    'Точность - сколько типов кораблей показать в графике', unsafe_allow_html=True)
    pie1.plotly_chart(ship_type_pie(date_from, date_to, basin, ship_flag, pie1),  use_container_width=True)

    pie2.subheader('Флаги судов')
    pie2.caption('Внешний круг - флаги судов по заданным параметрам (Параметр "Флаг судна" не учитывается).<br>'
                    'Внутренний круг - информация за аналогичный период в прошлом году<br>'
                    'Точность - сколько типов флагов показать в графике', unsafe_allow_html=True)
    pie2.plotly_chart(ship_flag_pie(date_from, date_to, basin, ship_type, pie2),  use_container_width=True)
        
    #длина судна, ширина судна
    histogram11,  histogram12 = st.columns([1, 1])
    histogram11.subheader('Длина судов')
    histogram11.plotly_chart(length_histogram(date_from, date_to, basin, ship_type, ship_flag), use_container_width=True)

    histogram12.subheader('Ширина судов')
    histogram12.plotly_chart(width_histogram(date_from, date_to, basin, ship_type, ship_flag), use_container_width=True)

    #самые популярные корабли
    st.subheader('Самые популярные корабли')
    st.caption('Информация о ТОП-10 кораблях по частоте заходов в порты по выбранным параметрам<br>Таблица листается вправо', unsafe_allow_html=True)
    st.write(most_popular(date_from, date_to, basin, ship_type, ship_flag, 10))


def main():
    st.write(**st.secrets["postgres"])
    st.header('Судозаходы в порты РФ')
    st.caption(time_upd())
    st.sidebar.title('Параметры')

    date_from, date_to, basin, ship_type, ship_flag = params()

    btn = st.sidebar.button('Применить')

    make_excel(date_from, date_to, basin, ship_type, ship_flag)
    st.sidebar.info('Данные взяты с сайта: [portcalltable.marinet.ru](https://portcalltable.marinet.ru/index.php)')

    visualize_data(date_from, date_to, basin, ship_type, ship_flag) 
    """ if btn:
        visualize_data(date_from, date_to, basin, ship_type, ship_flag)    
    else:
        st.markdown('<br><br>Необходимо нажать кнопку "Применить" или "Скачать Excel"', unsafe_allow_html=True)
        st.caption('Кнопки находятся внизу параметров') """


if __name__ == "__main__":
    main()




