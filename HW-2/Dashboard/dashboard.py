import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import os
from datetime import date ,datetime,timedelta
import streamlit as st
import json
import matplotlib.pyplot as plt
import numpy as np

def filter_log_file(input_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    filtered_lines = [line for line in lines if line.startswith('launchv5')]

    # with open(output_file, 'w') as file:
    #     file.writelines(filtered_lines)
    return filtered_lines

def convert_to_dict(line):
    # Rimuovi il prefisso "launchv5" dalla riga
    line = line.replace('launchv5', '')

    # Effettua la conversione in un dizionario
    try:
        data = eval(line)
        if isinstance(data, dict):
            return data
    except SyntaxError:
        pass

    # Restituisci None se la riga non può essere convertita in un dizionario
    return None

def convert_log_file(list_dict):
    # Converti le righe in un dizionario
    dicts = [convert_to_dict(line) for line in list_dict]

    # Rimuovi eventuali elementi None dalla lista dei dizionari
    dicts = [d for d in dicts if d is not None]

    # Crea un DataFrame pandas dal dizionario
    df = pd.DataFrame(dicts)

    # Salva il DataFrame in un file CSV
    return df

def rimuovi_unita_misura(valore):
    unita_misura = {
        'GB': 1e9,
        'MB': 1e6,
        'KB': 1e3,
        'B': 1,
        'TB': 1e12
    }
    for unita, fattore in unita_misura.items():
        if unita in valore:
            valori_numerici = ''.join(filter(str.isdigit, valore))
            return int(valori_numerici) * fattore
    return None  # Restituisco None se la stringa non contiene una delle unità di misura specificate

# Funzione per la conversione delle dimensioni
def converti_dimensione(dim):
    # Estrae la parte numerica e il suffisso dalla stringa
    num = float(''.join(filter(str.isdigit, dim)))
    suffisso = ''.join(filter(str.isalpha, dim)).upper()

    # Converte la dimensione in byte
    if suffisso == 'B':
        return num
    elif suffisso == 'KB':
        return num * 1024
    elif suffisso == 'MB':
        return num * 1024**2
    elif suffisso == 'GB':
        return num * 1024**3
    elif suffisso == 'TB':
        return num * 1024**4
    else:
        return None  # Ritorna None se il suffisso non è valido
    
def get_dataframe(input_file):
    # Esempio di utilizzo
    filtered_lines=filter_log_file(input_file)
    df=convert_log_file(filtered_lines)

    type_search=type(df['RAM Total'][0])

    # Itera su tutte le colonne del dataframe
    for colonna in df.columns:
        # Verifica se la colonna contiene il testo finale da rimuovere
        if type(df[colonna][0]) == type_search and colonna!='timestamp' :  # Assumendo che le colonne da modificare siano di tipo "object"

            df[colonna] = df[colonna].apply(converti_dimensione)
    df['New timestamp'] = pd.to_datetime(df['timestamp'])
    # Conversione del timestamp in datetime
    return df

def get_graph(df, col, n=9):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df['timestamp'], df[str(col)])
    ax.set_xlabel('Data e ora')
    ax.set_ylabel('Percentuale ' + str(col))
    ax.set_title(str(col))

    x_ticks = df['timestamp'][::len(df['timestamp']) // (n-1)]
    ax.set_xticks(x_ticks)
    ax.tick_params(axis='x', rotation=45)

    y_ticks = np.linspace(df[str(col)].min(), df[str(col)].max(), n)
    ax.set_yticks(y_ticks)

    return fig

def get_graph2(df, col, n=9):
    fig = px.line(df, x='timestamp', y=col, title=col)

    # Customize the x-axis and y-axis ticks
    x_ticks = df['timestamp'][::len(df['timestamp']) // (n-1)]
    fig.update_xaxes(tickmode='array', tickvals=x_ticks, tickangle=90)

    y_ticks = np.linspace(df[col].min(), df[col].max(), n)
    fig.update_yaxes(tickmode='array', tickvals=y_ticks)

    return fig # Display the plot as an image


def get_bar_chart(df, col, n=9):
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(df['timestamp'], df[str(col)])
    ax.set_xlabel('Data e ora')
    ax.set_ylabel('Percentuale ' + str(col))
    ax.set_title(str(col))

    x_ticks = df['timestamp'][::len(df['timestamp']) // (n-1)]
    ax.set_xticks(x_ticks)
    ax.tick_params(axis='x', rotation=45)

    y_ticks = np.linspace(df[str(col)].min(), df[str(col)].max(), n)
    ax.set_yticks(y_ticks)

    return fig

## Configurazione pagina Streamlit

st.set_page_config(
    page_title = "Dashboard PC information",
    page_icon = "",
    layout = "wide",
    initial_sidebar_state="expanded",
)

        
## Main Page
st.title("Homework 3")


###########
# variable
##########
input_file = 'hadoop-parallels-namenode-ubuntu-linux-22-04-desktop.log.txt'
df =get_dataframe(input_file)

colum=['CPU Core0','CPU Core1', 'RAM Total', 'RAM Available', 'RAM Used', 'RAM Percentage',
       'RAM SWAPTotal', 'RAM SWAPFree', 'RAM SWAPUsed', 'RAM SWAPPercentage',
       'DISK  Total read', 'DISK  Total write']


###########
## Sidebar
##########
st.sidebar.title(body = "Filtri")

min_date = df['New timestamp'].min().date()
selected_date = st.sidebar.date_input("Seleziona una data", min_date)

hour_start = st.sidebar.time_input("Seleziona l'ora d'inizio", datetime.combine(df['New timestamp'].min().date(), datetime.time(df['New timestamp'].min())))
hour_end = st.sidebar.time_input("Seleziona l'ora di fine", datetime.combine(df['New timestamp'].max().date(), datetime.time(df['New timestamp'].max())))


try:
    df_filter = df[(df['New timestamp'].dt.hour > hour_start.hour) & (df['New timestamp'].dt.hour < hour_end.hour) & (df['New timestamp'].dt.date == selected_date)]

    # Visualizzazione del DataFrame filtrato
    st.write("DataFrame filtrato:")
    st.write(df_filter)

    colum=['CPU Core0','CPU Core1',  'RAM Available', 'RAM Used', 'RAM Percentage',
            'RAM SWAPFree', 'RAM SWAPUsed', 'RAM SWAPPercentage',
        'DISK  Total read', 'DISK  Total write']

    col_delete=['RAM Total','RAM SWAPTotal',]

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[0], n=9))
        with col2:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[1], n=9))

    with st.container():
        col3, col4 = st.columns(2)
        with col3:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[2], n=9))
        with col4:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[3], n=9))

    with st.container():
        col5, col6 = st.columns(2)
        with col5:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[4], n=9))
        with col6:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[5], n=9))


    with st.container():
        col7, col8 = st.columns(2)
        with col1:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[7], n=9))
        with col2:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[8], n=9))

    with st.container():
        col8, col9 = st.columns(2)
        with col8:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[9], n=9))
        with col9:
            st.header('')
            st.pyplot(get_graph(df_filter,colum[9], n=9))
except:
    st.warning("Nessun valore corrisponde ai filtri selezionati.")
    st.write("DataFrame:")
    st.write(df)

