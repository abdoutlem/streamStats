import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
import time
#import plotly_express as px
import streamlit as st

file2 = 'C:/Users/arhmaritlemcani/Downloads/sensors_messages_2022-07-18 (7).csv'
#file2 = 'inputFiles/sensors_messages_2022-07-17 (2).csv'
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
dfDiag.loc[(dfDiag['nbrePostesEtg'].str.contains('F03')),'nbrePostesEtg']='524'
dfDiag.loc[(dfDiag['nbrePostesEtg'].str.contains('F04')),'nbrePostesEtg']='349'
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

zone = st.sidebar.multiselect("Zone :",
    options =  dfDiag['zone'].unique(),
    default =  dfDiag['zone'].unique()
)

dfDiag_selection = dfDiag.query(
    "bat == @Batiment & etg == @Etage & sensorType == @sensorType & date == @Date & Recupere == @Recupere & trancheHoraire == @trancheHoraire & zone == @zone"
)

# Diagnostic part
st.markdown('---')
st.title(":dart: Diagnostic")
#st.dataframe(dfDiag_selection)


st.markdown('---')
#Nombre de Capteurs arrachés
nbreCaptArraches = dfDiag_selection.groupby(['Type de message']).describe().iloc[3]['Code'][0]
captLePlusArrache = dfDiag_selection.groupby(['Type de message']).describe().iloc[3]['Code'][2]
nbreArrachementDuCapteur = dfDiag_selection.groupby(['Type de message']).describe().iloc[3]['Code'][3]

st.header("Messages d'arrachement : ")
st.text("Description: Capteur subissant une secousse ou décollé")

st.subheader("Le nombre de messages d'arrachement : ")
st.text(nbreCaptArraches)

st.subheader('Le capteur le plus arrcahé est  : ')
st.text(captLePlusArrache)
st.subheader("Nombre d'arrachement du capteur :")
st.text(nbreArrachementDuCapteur)



#Taux de couverture
totalCapteursWiloParEtage = sum(dfDiag_selection['nbrePostesEtg'].astype(int).unique())

st.markdown('---')
st.header('Taux de couverture (sur tout le parc) :')
st.text('Description: Taux de couverture sur le nombre total de capteurs par étage')

st.text(str(round(dfDiag_selection['Code'].unique().shape[0]/totalCapteursWiloParEtage,4)*100) + " %")




#Nombre de paquets perdus par tranche horaire

#Pourcentage de paquets perdus par tranche horaire

#Les 3 capteurs avec le plus de perte de paquets
st.markdown('---')
st.header("Pertes de paquets : ")

totalCapteursWilo = 1031
tauxPaquetsPerdus = round(len(dfDiag_selection[dfDiag_selection['Recupere'] == 1]) / len(dfDiag_selection),4) * 100

zoneLaPlusImpactee = 0
pertePaquetsParTH = 0


try:
    nbrePaquetsPerdusTotal = dfDiag_selection.groupby(['Recupere']).describe()['Code']['count'][1]
    captAcLePlusDePertes = dfDiag_selection.groupby(['Recupere']).describe()['Code']['top'][1]
    nbrePaquetsPerdusCapteur = dfDiag_selection.groupby(['Recupere']).describe()['Code']['freq'][1]
except:
    nbrePaquetsPerdusTotal = 0
    captAcLePlusDePertes = 0
    nbrePaquetsPerdusCapteur = 0

#tauxPaquetsPerdusParCapt = round(len((dfDiag_selection[dfDiag_selection['Code'] == captAcLePlusDePertes]) & (dfDiag_selection[dfDiag_selection['Recupere'] == 1]) ) / len((dfDiag_selection[dfDiag_selection['Code'] == captAcLePlusDePertes]) ),2) * 100

#st.dataframe(captAcLePlusDePertes)
st.subheader("Nombre de paquets perdus :")
st.text(nbrePaquetsPerdusTotal)

st.subheader("Nombre de paquets envoyés :")
st.text("Description : Décompte uniquement des messages d'occupation, de libération et d'arrachement" )
st.text(len(dfDiag_selection))

st.subheader("Taux de paquets perdus :")
st.text(str(tauxPaquetsPerdus) + "%")

st.subheader("Capteur avec le plus de perte :")
st.text(captAcLePlusDePertes)
st.subheader("Nombre de paquets perdus :")
st.text(nbrePaquetsPerdusCapteur)





