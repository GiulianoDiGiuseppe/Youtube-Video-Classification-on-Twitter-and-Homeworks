import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import os
from datetime import date ,datetime,timedelta
import streamlit as st
import json
import re
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap


# column multistring
column_analytic=['Research Organization - standardized','Keywords','Researchers','City of Research organization', 'State of Research organization',
        'Country of Research organization', 'Fields of Research (ANZSRC 2020)', 'RCDC Categories',
        'HRCS HC Categories', 'HRCS RAC Categories', 'Cancer Types',
        'CSO Categories', 'Units of Assessment',
        'Sustainable Development Goals']

## Consento la modifica su copie di un df
pd.options.mode.chained_assignment = None

## Configurazione pagina Streamlit
st.set_page_config(
    page_title = "Dashboard Federico II",
    page_icon = ":man_student:",
    layout = "wide",
    initial_sidebar_state="expanded",
)

## Main Page
st.title("Dashboard Federico II")


###########
# variable
##########

# read dataframe
df=pd.read_csv('./dataset_header.csv',delimiter="|")
df_city=pd.read_csv("./test_cities.csv")


#Open the JSON file for reading field of different filter
with open("./filt_file.json", "r") as file:
    # Load the contents of the file into a dictionary
    filter_dic = json.load(file)

# covnersion column in datetime
df['Start Date'] = pd.to_datetime(df['Start Date'])
df['End Date'] = pd.to_datetime(df['End Date'])
df['Start Year'] = pd.to_datetime(df['Start Year'], format='%Y').dt.year
df['End Year'] = pd.to_datetime(df['End Year'], format='%Y').dt.year



###########
## Sidebar
##########
#Title of sidebar
st.sidebar.title(body = "Filtri")

# Filter of date and conversion in datetime
start_date = st.sidebar.date_input("data d'inizio",value=df['Start Date'].min())
start_date = pd.to_datetime(start_date)
end_date = st.sidebar.date_input("data di fine",value=df['Start Date'].max())
end_date = pd.to_datetime(end_date)

# Filter dataframe for date
df_filtrato=df[(df['Start Date']>start_date) & (df['Start Date']<end_date)]

# create all filter option
selected_options={}
for i in column_analytic:
    selected_options[i] = st.sidebar.multiselect(
        "Filter by " + i,
        filter_dic[i]
    )

# True: if exist all element in valore in a string
# False : if element in list of valore not exist in a strin
def check_string(valore, stringa):
    for v in valore:
        if v not in stringa:
            return False
    return True

# lista di campi che danno un dataframe nullo
valori_assenti=[]

# Scorrere le chiavi e i valori del dizionario
# per ogni filtro_option effettuo il filtraggio del dataframe
for chiave, valore in selected_options.items():
    if len(valore)!=0:
        df_filtrato = df_filtrato[df_filtrato[chiave].apply(lambda x: check_string(valore, x) if type(x) == str else False)]
    if (df_filtrato.shape[0]==0):
        valori_assenti.append(chiave)


###########
## Easier Operation
##########
# se il df_filtrato è nullo da errore
if (df_filtrato.shape[0]==0):
    st.warning("No entry was found for filtering "+str(valori_assenti[0]))#,icon="🚨")valori_assenti[0] 


else:
    # Raggruppamento per "Funding Amount" e somma su "Funder Country"
    dic_group={}
    dic_group['Funder Country'] = df_filtrato.groupby('Funder Country')['Funding Amount'].sum().sort_values(ascending=False)
    dic_group['Start Year'] = df_filtrato.groupby('Start Year')['Funding Amount'].sum().sort_index(ascending=False)

    # calcolo count della durata progetti e salvataggio in dic_group['duration Year]
    serie_durata = (df_filtrato['End Year'] - df_filtrato['Start Year']).apply(lambda x: f'{x} years')
    dic_group['Duration Year'] = serie_durata.groupby(serie_durata).size()

    ###########
    ## Advanced Operation
    ##########
    master_dic={}

    for Field in column_analytic: # per ogni colonna determinata prima
        dictionary = {}
        cnt=0
        lista_valori=[]
        # per ogni elemento della colonna
        for e in df_filtrato[df_filtrato[Field].notna()][Field].apply(lambda x: re.split(';|,', x)).apply(lambda x: [y.strip() for y in x]):
            s=list(set(e))# elimino i doppioni
            while '' in s:
                s.remove('')
            for elem in s: # inserisco gli elementi in una lista
                lista_valori.append(elem)

        new_naples_df = pd.DataFrame(lista_valori,columns=[Field])# creo il dataframe
        tmp=new_naples_df.value_counts() # questa è una series la salvo in una var tmp
        master_dic[Field]=tmp.loc[~tmp.index.get_level_values(0).str.contains('Napoli|Naples')] # filtro gli elemnti che contengono naples o napoli

    dic_group['Start Year']=dic_group['Start Year'].dropna()

    city_find=list(master_dic['City of Research organization'].index.get_level_values(0))
    df_city = df_city[df_city['City'].isin(city_find)]
    for index, row in df_city.iterrows():
        df_city.at[index, "Count"]=master_dic['City of Research organization'][df_city.at[index, "City"]]    


    ###########
    ## Graphs
    ##########


    # Stampo il dataframe
    st.header("Table")
    st.dataframe(df_filtrato)


    #with st.container():
        # trovo il count massimo tra le città
    max_count = df_city['Count'].max()

    # creo la mappa
    m = folium.Map(location=[41.9028, 12.4964], zoom_start=4)

    # aggiungo i marker per ogni città
    for i, row in df_city.iterrows():
        folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
                            radius=row['Count'] / 70,  # dimensione del marker in base al count
                            fill=True,
                            fill_opacity=0.7,
                            tooltip=f"{row['City']}: {row['Count']}"
                            ).add_to(m)

    # integro la mappa in un'applicazione Streamlit
    st.header("Map of collaborations")
    folium_static(m)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
        # graph Funding amount for country
            st.header("Pie chart of funds invested by different states")
            fig1 = px.pie(dic_group['Funder Country'], values='Funding Amount', names=dic_group['Funder Country'].index)
            fig1.update_layout(width=500, height=500)
            st.plotly_chart(fig1)

        with col2:
            st.header("Pie chart of duration projects")
        # pie chart od duration year of project
            fig3 = px.pie(dic_group['Duration Year'], values=0, names=dic_group['Duration Year'].index)
            fig3.update_layout(width=500, height=500)
            st.plotly_chart(fig3)

    st.header("Bar graph of total money invested in projects")
    fig7=px.bar(x=dic_group['Start Year'].index,y=dic_group['Start Year'].values)
    fig7.update_layout(xaxis={'range': ['1990', '2024']})

    st.plotly_chart(fig7, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header("Distribution Units of Assessment")
            fig8=px.bar(x=master_dic['Units of Assessment'].index.get_level_values(0),y=master_dic['Units of Assessment'].values)
            st.plotly_chart(fig8, use_container_width=True)
        with col2:
            st.header("Distribution Sustainable Development Goals")
            fig9=px.bar(x=master_dic['Sustainable Development Goals'].index.get_level_values(0),y=master_dic['Sustainable Development Goals'].values)
            st.plotly_chart(fig9, use_container_width=True)
    
    # with st.container():
    #     col1, col2 = st.columns(2)

    #     with col1:

        
    #     with col2:

    column_table=['Researchers', 'State of Research organization',
            'Country of Research organization', 'Fields of Research (ANZSRC 2020)', 
            'CSO Categories',
            'Sustainable Development Goals']

    with st.container():
        col1, col2,col3 = st.columns(3)
        with col1:
            st.header("Table Researchers")
            st.dataframe(master_dic[ column_analytic[0]])
        with col2:
            st.header("Table State of Research organization")
            st.dataframe(master_dic[ column_analytic[1]])
        with col3:
            st.header("Table Country of Research organization")
            st.dataframe(master_dic[ column_analytic[2]])

    with st.container():
        col1, col2,col3 = st.columns(3)
        with col1:
            st.header("Table Fields of Research (ANZSRC 2020)")
            st.dataframe(master_dic[ column_analytic[3]])
        with col2:
            st.header("Table CSO Categories'")
            st.dataframe(master_dic[ column_analytic[4]])
        with col3:
            st.header("Table Sustainable Development Goals")
            st.dataframe(master_dic[ column_analytic[5]])
        