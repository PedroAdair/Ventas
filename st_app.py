import streamlit as st
import  pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import datetime
from style import palette_deepaxiom

# ----- App config ----- #
st.set_page_config(
page_title = 'Pedro Adair Avila Forecast',
page_icon = 'Active',
layout = 'wide',
)

angle = 20


# ----- Load Data ----- #
@st.cache_data
def load_data():
    return pd.read_csv('BaseDatosCSV.csv')

data = load_data()

@st.cache_data
def load_data2(tienda):
    x = pd.read_csv(
        f'forecast_{tienda}.csv',
        names=['date','pred','low','upp','pred_r','SKU','LOC','venta'],
    ).drop(0)

    x['pred'] = pd.to_numeric(x['pred'])
    x['low'] = pd.to_numeric(x['low'])
    x['upp'] = pd.to_numeric(x['upp'])
    x['pred_r'] = pd.to_numeric(x['pred_r'])
    x['venta'] = pd.to_numeric(x['venta'])

    return x

# ----- Process Data ----- #
# Split date
@st.cache_data
def process_data(data):
    date_df = data['FECHA'].str.split(pat='/', expand=True)

    data['day'] = date_df[0]
    data['month'] = date_df[1]
    data['year'] = date_df[2]
    data['DATE'] = pd.to_datetime(data[['year','month','day']])
    data['DAY_NAME']= [date.day_name() for date in data['DATE']]
    return data

data = process_data(data)

# ===== App implementation ===== #

st.write('# Pronostico de ventas (Pedro Adair Avila)')

tabs = st.tabs([
    'Productos vendidos', 'Proporción de ventas totales', 'Ventas promedio', 'Pronóstico de ventas'
])

# ----- Productos ----- #
with tabs[0]:
    with st.container():
        col1, col2 = st.columns([0.5,0.5])
        with col1:
            # Filtrar mes
            meses = {
                'Abril':4,
                'Mayo':5,
                'Junio':6
            }

            mes = st.selectbox(
                'Elegir mes',
                ('Abril', 'Mayo', 'Junio'),
                key=0
            )
            mes_num = meses.get(mes)
            # Filtrar tienda
            tienda = st.selectbox(
                'Elegir tienda',
                sorted(tuple(data['LOC'].unique())),
                key=1
            )
        with col2:
            # Filtrar articulos
            options = sorted(tuple(data['SKU'].unique()))
            articulos = st.multiselect(
                'Elegir artículos',
                options,
                default=options[0],
                key=2
            )
        
    if len(articulos) > 0:
        # Generar dataframe
        df =  data[
            (data['month'] == str(mes_num)) & (data['SKU'].isin(articulos))
        ]
        df = df.reset_index(drop=True)

        # Graficar
        col1, col2 = st.columns([0.5, 0.5])

        with col1:
            st.write(f'### Unidades vendidas por día de la semana en tienda {tienda}')
            st.write(f'Se consideran los artículos ' + ', '.join(articulos)+'.')

            # Generar dataframe
            d = df[df['LOC'] == tienda]
            d = d.reset_index(drop=True)

            # Grafica dias de la semana
            day_names = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
            dataframe = pd.DataFrame(
                data={
                    'day_names':day_names,
                    'counts':[len(d[d['DAY_NAME']==name]) for name in day_names]
                }
            )

            fig = px.bar(
                data_frame=dataframe,
                x='day_names', y='counts',
                labels={
                    'day_names':'Día de la semana',
                    'counts':'Unidades vendidas'
                },
                color_discrete_sequence=palette_deepaxiom
            )
            fig.update_layout(
                xaxis = dict(
                    titlefont = dict(size=20),
                    tickfont = dict(size=16),
                    tickmode = 'array',
                    tickvals = day_names,
                    ticktext = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
                ),
                yaxis = dict(
                    titlefont = dict(size=20),
                    tickfont = dict(size=16)
                )
            )
            fig.update_xaxes()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write('### Top 10 tiendas con respecto a las unidades vendidas')
            st.write(f'Se consideran los artículos ' + ', '.join(articulos)+'.')

            # Filtrar top 10 tiendas
            d = (df[['LOC', 'UNI']]).groupby('LOC').sum().sort_values(by='UNI',ascending=False)

            # Generar dataframe
            d = d.head(10).reset_index()

            # Grafica top 10 tiendas
            fig = px.bar(
                data_frame=d,
                x='LOC', y='UNI',
                labels={
                    'LOC':'Tienda',
                    'UNI':'Unidades vendidas'
                },
                color_discrete_sequence=palette_deepaxiom
            )
            fig.update_layout(
                xaxis = dict(
                    titlefont = dict(size=20),
                    tickfont = dict(size=16)
                ),
                yaxis = dict(
                    titlefont = dict(size=20),
                    tickfont = dict(size=16)
                )
            )
            # fig.update_xaxes(tickangle=angle)

            st.plotly_chart(fig, use_container_width=True)

# ----- Proporcion ----- #
with tabs[1]:
    cols = st.columns([0.05, 0.4, 0.5, 0.05])
    with cols[1]:
        # Filtrar mes
        meses = {
            'Abril':4,
            'Mayo':5,
            'Junio':6
        }
        mes = st.selectbox(
            'Elegir mes',
            ('Abril', 'Mayo', 'Junio'),
            key=3
        )

        mes_num = meses.get(mes)
        # Filtrar tienda
        tienda = st.selectbox(
            'Elegir tienda',
            sorted(tuple(data['LOC'].unique())),
            key=4
        )
        
        # Generar dataframe
        df =  data[
            (data['month'] == str(mes_num)) & (data['LOC'] == tienda)
        ]
        if len(df) > 0:
            d = df.groupby('SKU').count()['LOC']
            d2 = (d / d.sum()).sort_values(ascending=False)

            st.write('### Información relevante')
            st.write(f'Se tiene que los **tres** productos con **más ventas** en la tienda **{tienda}** y sus respectivos porcentajes de ventas en el mes de **{mes}** son:')
            for i in range(3):
                st.write(f'- **{d2.index[i]}** : {d2[i]*100:.2f}%')

            st.write(f'Se tiene que el producto con **menos ventas** en la tienda **{tienda}** y su respectivo porcentaje de ventas en el mes de **{mes}** es:')
            st.write(f'- **{d2.index[-1]}** : {d2[-1]*100:.2f}%')
        
    
    # Graficar
    with cols[2]:
        if len(df) > 0:
            st.write('### Porcentajes de ventas por artículo')
            st.write(f'#### Tienda {tienda} - mes de {mes}')
            
            d = d.sort_index()

            dataframe = pd.DataFrame(
                data={
                    'values':d,
                    'names':d.index
                }
            )

            fig = px.pie(
                data_frame=dataframe,
                values='values',
                names='names',
                color_discrete_sequence=palette_deepaxiom
            )
            fig.update_layout(
                uniformtext_minsize=14, uniformtext_mode='hide',
                showlegend=True, 
                legend=dict(
                    font=dict(
                        size=14
                    ),

                )
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write('### No hay datos disponibles')
        

# ----- Ventas ----- #
with tabs[2]:
    with st.container():
        col1, col2 = st.columns([0.5,0.5])
        with col1:
            # Filtrar tienda
            tienda = st.selectbox(
                'Elegir tienda',
                sorted(tuple(data['LOC'].unique())),
                key=5
            )
            # Filtrar articulos
            options = sorted(tuple(data['SKU'].unique()))
            articulos = st.multiselect(
                'Elegir artículos',
                options,
                default=options[0],
                key=6
            )
        with col2:
            # Filtrar mes
            unidades = {
                '1 día':0,
                '7 días':1,
                '14 días':2,
                '1 mes':3
            }

            unidad = st.selectbox(
                'Elegir unidad de tiempo',
                ('1 día', '7 días', '14 días', '30 días'),
                key=7
            )
            unidad_key = unidades.get(unidad)

            # Filtar fechas
            min_date = None
            max_date =None
            dates = None
            time_delta = 1

            if unidad_key == 0:
                time_delta = 1
            elif unidad_key == 1:
                time_delta = 7
            elif unidad_key == 2:
                time_delta = 14
            else:
                time_delta = 30

            
            min_date = data['DATE'].min().to_pydatetime()
            max_date =data['DATE'].max().to_pydatetime()
            min_date, max_date = st.slider(
                'Elegir periodo',
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                step=datetime.timedelta(days=time_delta)
            )
    
    if len(articulos) > 0:
        # Generar dataframe
        df =  (data[
            (data['LOC'] == tienda) & (data['SKU'].isin(articulos)) &\
            (data['DATE'] >= min_date) & (data['DATE'] <= max_date)
        ]).sort_values('DATE')
        df = df.reset_index(drop=True)

        df_new = df[['DATE', 'UNI', 'SKU']]

        df_new = df_new.groupby('SKU')

        # Transform data
        new_dates = pd.date_range(start=min_date, end=max_date, freq='D')
        def reindex_dates(dataframe):
            sku = dataframe['SKU'].iloc[0]
            # Daily time series
            df_dates = dataframe.set_index('DATE', drop=True)
            df_dates = df_dates.reindex(new_dates)
            df_dates = df_dates.rename_axis('date')
            df_dates['UNI'] = df_dates['UNI'].fillna(0)
            df_dates['SKU'] = df_dates['SKU'].fillna(sku)

            # Aggregate data
            total_days = (max_date- min_date).days
            steps = total_days // time_delta
            dates = []
            units = []
            for step in range(steps):
                df_aux = df_dates.iloc[
                    step * time_delta:(step + 1) * time_delta,:
                ]
                units.append(df_aux['UNI'].sum())
                dates.append(df_aux.index[-1])
            if total_days % time_delta != 0:
                df_aux = df_dates.iloc[
                    steps * time_delta:,:
                ]
                units.append(df_aux['UNI'].sum())
                dates.append(df_aux.index[-1])
            
            # Create aggregated dataframe
            df_dates = pd.DataFrame(
                data={
                    'UNI':units,
                    'SKU':[sku]*len(units)
                },
                index=dates
            )

            return df_dates

        df_new = df_new.apply(reindex_dates)
        
        flag = False
        min_date_str = min_date.strftime('%Y-%m-%d')
        max_date_str = max_date.strftime('%Y-%m-%d')
        
        new_data = {
                item:(df_new[df_new['SKU']==item]).reset_index(drop=True)['UNI'] for item in articulos
            }
        
        for i in range(len(articulos)):
            try:
                new_data.update({'date':list(df_new[df_new['SKU']==articulos[i]].index.droplevel())})
                df_last = pd.DataFrame(
                    data=new_data
                )
                flag = True
                break
            except Exception as e:
                pass

        if len(df_new)> 0 and flag:
            st.write(f'#### Unidades vendidas cada {time_delta} días del {min_date_str} al {max_date_str}')

            fig = px.line(
                df_last, x='date', y=df_last.columns[:-1],
                labels={
                    'date':'Fecha',
                    'value':'Unidades vendidas'
                },
                color_discrete_sequence=palette_deepaxiom
            )
            fig.update_layout(
                xaxis = dict(
                    titlefont = dict(size=20),
                    tickfont = dict(size=16)
                ),
                yaxis = dict(
                    titlefont = dict(size=20),
                    tickfont = dict(size=16)
                )
            )
            fig.update_xaxes(tickformat='%Y-%m-%d')
            st.plotly_chart(fig, use_container_width =True)
        else:
            st.write('#### Datos no disponibles')


# ----- Pronostico ----- #
with tabs[3]:
    with st.container():
        col1, col2 = st.columns([0.5,0.5])

        with col2:
            tienda = st.selectbox(
                'Elegir tienda',
                ('LOC_001','LOC_002')
            )
            data2 = load_data2(tienda)
            articulo = st.selectbox(
                'Elegir artículo',
                sorted(data2['SKU'].unique())
            )
        
        with col1:
            st.write(f'## Pronósticos en tienda {tienda}')
            st.write('Se consideran intervalos de confianza del 90% para los pronósticos, además de que estos son realizados con ventanas de tiempo a 7 días y una historia de 10 días. Se utiliza un Modelo Auto-Regresivo con Regresión Lasso, donde se le aplica un estandarización a la variable objetivo.')

            st.write()

    with st.container():
        cols = st.columns([0.45,0.05,0.5])
        with cols[0]:
            st.dataframe(data2.sort_values(['SKU','date'], ascending=True),use_container_width=True)
        
        with cols[-1]:
            # Generar dataframe
            df2 = data2[data2['SKU'] == articulo]

            ventas = df2['venta'].sum()
            pronostico = df2['pred'].sum()

            st.write('#### Unidades vendidas *vs* Pronóstico a 7 días')
            col1, col2 = st.columns([0.5,0.5])
            with col1:
                st.write(f'##### Unidades vendidas: **{ventas}**')
            with col2:
                st.write(f'##### Pronóstico: **{pronostico:.2f}**')

            fig = go.Figure()

            fig.add_trace(go.Scatter(x=df2['date'], y=df2['low'],
                fill=None,
                mode='lines',
                line_color=palette_deepaxiom[8],
                name='Cota inferior'
            ))

            fig.add_trace(go.Scatter(
                x=df2['date'], 
                y=df2['upp'],
                fill='tonexty', # fill area between trace0 and trace1
                fillcolor='rgba(244,165,59,0.2)',
                mode='lines', line_color=palette_deepaxiom[5],
                name='Cota superior'
            ))

            fig.add_trace(go.Scatter(
                x=df2['date'],
                y=df2['pred'],
                fill=None,
                mode='lines', line_color=palette_deepaxiom[2], 
                line=dict(width=3),
                name='Predicción'
            ))
            fig.add_trace(go.Scatter(
                x=df2['date'],
                y=df2['venta'],
                fill=None,
                mode='lines', line_color=palette_deepaxiom[3], 
                line=dict(width=3),
                name='Unidades vendidas'
            ))
            fig.update_layout(
                margin=dict(t=0)
            )
            fig.update_xaxes(tickformat='%Y-%m-%d')
            st.plotly_chart(fig, use_container_width=True, theme='streamlit')
