import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import time
#import plotly_express as px
import streamlit as st

#file2 = 'C:/Users/arhmaritlemcani/Downloads/sensors_messages_2022-07-17 (2).csv'
file2 = 'inputFiles/sensors_messages_2022-07-17 (2).csv'
dfDiag = pd.read_csv(file2,delimiter=';',encoding='ISO-8859-1',dtype=str).sort_values(['Code','Heure de message'])

def recupPaquetsPerdus(df):
    wxData = df.to_numpy()
    paquetsRécuperes = 0

    for i in range(len(wxData) - 1):
        if (wxData[i][0] == wxData[i + 1][0]):
            if (wxData[i][6] != 'MCEO' and wxData[i + 1][6] == 'MCEL'):
                wxData = np.insert(wxData, i + 1, wxData[i + 1], 0)
                wxData[i + 1][6] = 'MCEO'  # wxData[i+1][14]
                wxData[i + 1][8] = wxData[i + 1][15]
                wxData[i + 1][14] = 'RECUP'
                wxData[i + 1][15] = ''
                wxData[i+1][-3] = 1
                paquetsRécuperes += 1
                # print("2 MCEL se suivent")
            elif (wxData[i][6] == 'MCEO' and wxData[i + 1][6] == 'MCEO'):
                wxData = np.insert(wxData, i + 1, wxData[i + 1], 0)
                wxData[i + 1][6] = 'MCEL'  # wxData[i + 1][14]
                wxData[i + 1][8] = wxData[i + 1][15]
                wxData[i + 1][14] = 'RECUP'
                wxData[i + 1][15] = ''
                wxData[i + 1][-3] = 1

                paquetsRécuperes += 1
                # print("2 MCEO se suivent")
    print(paquetsRécuperes, " paquets récuperés")
    return pd.DataFrame(wxData, columns=df.columns)



dfDiag.rename(columns= {'Path Localisation' : 'Path'}, inplace=True)
dfDiag.rename(columns= {'Type de Capteur' : 'sensorType'}, inplace=True)

dfDiag['bat'] = dfDiag['Path']
dfDiag['etg'] = dfDiag['Path']
dfDiag['nbrePostesEtg'] = dfDiag['Path']
dfDiag['date'] = dfDiag['Heure de message'].str[:10]
dfDiag['Heure de message'] = dfDiag['Heure de message'].str[11:]
dfDiag['Recupere'] =  0 * len(dfDiag)
dfDiag['zone'] = dfDiag['Path'].str[22:24]
dfDiag['trancheHoraire'] = dfDiag['Heure de message']


#Batiments :
dfDiag.loc[(dfDiag['bat'].str.contains('WIL')),'bat']='WILO'
#Etages : 
dfDiag.loc[(dfDiag['etg'].str.contains('F03')),'etg']='3'
dfDiag.loc[(dfDiag['etg'].str.contains('F04')),'etg']='4'
dfDiag.loc[(dfDiag['etg'].str.contains('F05')),'etg']='5'
#tranches horaires :
dfDiag.loc[(dfDiag['Heure de message'] < '07:00:00'),'trancheHoraire']='t-7'
dfDiag.loc[(dfDiag['Heure de message'] >= '07:00:00') & (dfDiag['Heure de message'] < '12:00:00'),'trancheHoraire']='t7_12'
dfDiag.loc[(dfDiag['Heure de message'] >= '12:00:00') & (dfDiag['Heure de message'] < '14:00:00'),'trancheHoraire']='t12_14'
dfDiag.loc[(dfDiag['Heure de message'] >= '14:00:00') & (dfDiag['Heure de message'] < '21:00:00'),'trancheHoraire']='t14_21'
dfDiag.loc[(dfDiag['Heure de message'] >= '21:00:00'),'trancheHoraire']='t21+'


#nbreDeCapteursParEtage
dfDiag.loc[(dfDiag['nbrePostesEtg'].str.contains('F03')),'nbrePostesEtg']='521'
dfDiag.loc[(dfDiag['nbrePostesEtg'].str.contains('F04')),'nbrePostesEtg']='344'
dfDiag.loc[(dfDiag['nbrePostesEtg'].str.contains('F05')),'nbrePostesEtg']='159'

dfDiag = recupPaquetsPerdus(dfDiag)

#dfDiag['Heure de message'] = dfDiag['Heure de message'].str[11:]

Batiment = st.sidebar.multiselect("Selectionner le batiment :",
    options =  dfDiag['bat'].unique(),
    default =  dfDiag['bat'].unique()
)

Etage = st.sidebar.multiselect("Selectionner l'étage:",
    options =  dfDiag['etg'].unique(),
    default =  dfDiag['etg'].unique()
)

sensorType = st.sidebar.multiselect("Selectionner le type de capteur:",
    options =  dfDiag['sensorType'].unique(),
    default =  dfDiag['sensorType'].unique()
)

Date = st.sidebar.multiselect("Selectionner les Date:",
    options =  dfDiag['date'].unique(),
    default =  dfDiag['date'].unique()
)

Recupere = st.sidebar.multiselect("messages recuperes ou non :",
    options =  dfDiag['Recupere'].unique(),
    default =  dfDiag['Recupere'].unique()
)

trancheHoraire = st.sidebar.multiselect("Tranche Horaire :",
    options =  dfDiag['trancheHoraire'].unique(),
    default =  dfDiag['trancheHoraire'].unique()
)

dfDiag_selection = dfDiag.query(
    "bat == @Batiment & etg == @Etage & sensorType == @sensorType & date == @Date & Recupere == @Recupere & trancheHoraire == @trancheHoraire"
)

# Diagnostic part
st.markdown('---')
st.title(":dart: Diagnostic")
st.dataframe(dfDiag_selection)


st.markdown('---')
#Nombre de Capteurs arrachés
nbreCaptArraches = dfDiag_selection.groupby(['Type de message']).describe().iloc[3]['Code']

st.title("Nombre de capteurs arrachés")
st.text("(Quand un capteur est décollé ou subit une secousse celui-ci envoi un message d'arrachement)")
#st.dataframe(nbreCaptArraches)
st.text(nbreCaptArraches)

#Taux de couverture

#Nombre de paquets perdus par tranche horaire

#Pourcentage de paquets perdus par tranche horaire

#Les 3 capteurs avec le plus de perte de paquets
captAcLePlusDePertes = dfDiag_selection.groupby(['Code'])['Recupere'].sum().to_frame().nlargest(2,['Recupere'])

st.title("Capteurs avec le plus de perte")
#st.dataframe(captAcLePlusDePertes)
st.text(captAcLePlusDePertes)





