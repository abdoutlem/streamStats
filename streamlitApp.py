# %%
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
import pandas as pd
import time
import plotly_express as px
import streamlit as st

st.set_page_config(page_title="Dashboard", layout="wide")



#def formatDate(file):
#    jour = file[36:38]
#    mois = file[33:35]
#    annee = file[28:32]
#    date = jour + '/' + mois + '/' + annee
#    return date

def date_to_minutes(date):

    horaire = date[11:]
    heure = int(horaire[:2])
    minutes = int(horaire[3:5])
    return heure * 60 + minutes

def format(excelFile):
    df = pd.read_excel(excelFile)
    writer = pd.ExcelWriter(excelFile, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Make the columns wider for clarity.
    worksheet.set_column(0, max_col - 1, 12)
    # Set the autofilter.
    worksheet.autofilter(0, 0, max_row, max_col - 1)
    writer.save()

@st.cache
def get_data_from_csv():
    file = 'C:/Users/arhmaritlemcani/Downloads/sensors_messages_2022-07-18.csv'
    #file  = 'inputFiles/sensors_messages_2022-07-17 (1).csv'
    df = pd.read_csv(file,delimiter=';',encoding='ISO-8859-1',dtype=str).sort_values(['Code','Heure de message'])

    return df
df = get_data_from_csv()

#file1 = 'C:/Users/arhmaritlemcani/Downloads/sensors_messages_2022-07-08.csv'
#file2 = 'C:/Users/arhmaritlemcani/Downloads/sensors_messages_2022-07-17.csv'
#df1 = pd.read_csv(file1,delimiter=';',encoding='ISO-8859-1',dtype=str).sort_values(['Code','Heure de message'])
#df2 = pd.read_csv(file2,delimiter=';',encoding='ISO-8859-1',dtype=str).sort_values(['Code','Heure de message'])
#df = pd.concat([df1,df2],ignore_index=True).sort_values(['Code','Heure de message'])

if( 'Europ' in df['Client'].iloc[0]):
    client = 'EuropAssistance'
elif(df['Client'].iloc[0] == 'AXA'):
    client = 'Axa'
    sousClient = 'AxaTSN' # C'est à nous de choisir (Choix possibles: AxaTSN / AxaMAJ / )
elif('CD92' in df['Client'].iloc[0]):
    client = 'CD92'


def recupPaquetsPerdus(df):
    wxData = df.to_numpy()
    print(isinstance(wxData[18117][14],float))
    paquetsRécuperes = 0

    for i in range(len(wxData) - 1):
        if (wxData[i][0] == wxData[i + 1][0]):
            if (wxData[i][6] != 'MCEO' and wxData[i + 1][6] == 'MCEL'):
                wxData = np.insert(wxData, i + 1, wxData[i + 1], 0)
                wxData[i + 1][6] = 'MCEO'  # wxData[i+1][14]
                wxData[i + 1][8] = wxData[i + 1][15] if isinstance(wxData[i+1][15],str) else (wxData[i][8])  # Pour eviter de recuperer des paquets aves des manques d'informations
                wxData[i + 1][14] = 'RECUP'
                wxData[i + 1][15] = ''
                paquetsRécuperes += 1
                # print("2 MCEL se suivent")
            elif (wxData[i][6] == 'MCEO' and wxData[i + 1][6] == 'MCEO'):
                wxData = np.insert(wxData, i + 1, wxData[i + 1], 0)
                wxData[i + 1][6] = 'MCEL'  # wxData[i + 1][14]
                wxData[i + 1][8] = wxData[i + 1][15] if isinstance(wxData[i+1][15],str) else wxData[i][8]
                wxData[i + 1][14] = 'RECUP'
                wxData[i + 1][15] = ''
                paquetsRécuperes += 1
                # print("2 MCEO se suivent")
    print(paquetsRécuperes, " paquets récuperés")
    return pd.DataFrame(wxData, columns=df.columns)


df = recupPaquetsPerdus(df=df)

# %% [markdown]
# Creation de la Table utilisation

# %%
def tableUtilisations(df):
    wxData = df.to_numpy()

    sensors = []
    sensorType = []
    path = []
    date = []
    dateDebut = []
    dateFin = []
    durees = []
    bat = []
    etg = []

    for i in range(len(wxData) - 1):
        if (wxData[i][0] == wxData[i + 1][0]):
            if (wxData[i][6] == 'MCEO' and 'MCEL' in wxData[i + 1][6]):
                sensors.append(wxData[i][0])
                date.append(wxData[i][8][:10])
                durees.append(date_to_minutes(wxData[i + 1][8]) - date_to_minutes(wxData[i][8]))
                dateDebut.append(wxData[i][8][11:])
                dateFin.append(wxData[i + 1][8][11:])
                path.append(wxData[i][1])
                sensorType.append(wxData[i][5])

    table1 = pd.DataFrame(list(zip(sensors, sensorType, path, date, dateDebut, dateFin, durees)),
                          columns=['SigfoxID', 'sensorType', 'path', 'date', 'dateDebut', 'dateFin', 'Duree'])

    # on suprime les lignes avec 12min d'occupation
    # table1 = table[~(table['Duree'] == 12)]

    table1['OccupationTotale'] = table1.groupby(['SigfoxID'])['Duree'].cumsum()
    # table1['OccupationTotaleParetg'] = table1.groupby(['etg'])['Duree'].cumsum()
    # table1['OccupationTotaleParBatiment'] = table1.groupby(['bat'])['Duree'].cumsum()

    return table1


tableUtilisations = tableUtilisations(df)


# %% [markdown]
# Nettoyage des durées erronnées (3,6 et 12 minutes)

# %%
tableUtilisations.drop(tableUtilisations[tableUtilisations['Duree'] == 3].index, inplace=True)
tableUtilisations.drop(tableUtilisations[tableUtilisations['Duree'] == 6].index, inplace=True)
tableUtilisations.drop(tableUtilisations[tableUtilisations['Duree'] == 9].index, inplace=True)
tableUtilisations.drop(tableUtilisations[tableUtilisations['Duree'] == 12].index, inplace=True)

# %% [markdown]
# Correction des colonnes Batiments et etg et sensorType (en fonction des clients)

# %%
tableUtilisations['bat'] = tableUtilisations['path']
tableUtilisations['etg'] = tableUtilisations['path']
tableUtilisations['nbrePostesEtg'] = tableUtilisations['path']
tableUtilisations['zone'] = tableUtilisations['path'].str[22:24]
tableUtilisations['trancheHoraire'] = tableUtilisations['dateDebut']
# tranches horaires :
tableUtilisations.loc[(tableUtilisations['dateDebut'] < '07:00:00'), 'trancheHoraire'] = 't-7'
tableUtilisations.loc[(tableUtilisations['dateDebut'] >= '07:00:00') & (tableUtilisations['dateDebut'] < '12:00:00'), 'trancheHoraire'] = 't7_12'
tableUtilisations.loc[(tableUtilisations['dateDebut'] >= '12:00:00') & (tableUtilisations['dateDebut'] < '14:00:00'), 'trancheHoraire'] = 't12_14'
tableUtilisations.loc[(tableUtilisations['dateDebut'] >= '14:00:00') & (tableUtilisations['dateDebut'] < '21:00:00'), 'trancheHoraire'] = 't14_21'
tableUtilisations.loc[(tableUtilisations['dateDebut'] >= '21:00:00'), 'trancheHoraire'] = 't21+'

# %%
if (client == 'EuropAssistance'):
    # Batiments :
    tableUtilisations.loc[(tableUtilisations['bat'].str.contains('WIL')), 'bat'] = 'WILO'
    # Etages :
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('F03')), 'etg'] = '3'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('F04')), 'etg'] = '4'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('F05')), 'etg'] = '5'
    # nbreDeCapteursParEtage
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('F03')), 'nbrePostesEtg'] = '521'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('F04')), 'nbrePostesEtg'] = '344'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('F05')), 'nbrePostesEtg'] = '159'


elif (client == 'Axa'):
    if (sousClient == 'AxaTSN'):
        tableUtilisations = tableUtilisations[~tableUtilisations.path.str.contains('JAVA|JOY|MAJ')]

        # Batiments :
        tableUtilisations.loc[(tableUtilisations['bat'].str.contains('EDR')), 'bat'] = 'EDR'
        tableUtilisations.loc[(tableUtilisations['bat'].str.contains('NEW')), 'bat'] = 'NewPim'
        tableUtilisations.loc[(tableUtilisations['bat'].str.contains('TRS')), 'bat'] = 'TRS'
        # Etages EDR :
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('R/0')), 'etg'] = '0'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('R/1')), 'etg'] = '1'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('R/2')), 'etg'] = '2'
        # Etages NewPim :
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('F01')), 'etg'] = '1'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('F03')), 'etg'] = '3'
        # Etages terrasses :
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('/1/')), 'etg'] = '1'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('/2/')), 'etg'] = '2'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('/3/')), 'etg'] = '3'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('/4/')), 'etg'] = '4'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('/5/')), 'etg'] = '5'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('/6/')), 'etg'] = '6'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('/7/')), 'etg'] = '7'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('/8/')), 'etg'] = '8'

    elif (sousClient == 'AxaMAJ'):
        tableUtilisations = tableUtilisations[tableUtilisations.path.str.contains('MAJ')]

        # Batiments Majunga :
        tableUtilisations.loc[(tableUtilisations['bat'].str.contains('MAJ')), 'bat'] = 'MAJ'
        # Etages Majunga :
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E14')), 'etg'] = '14'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E15')), 'etg'] = '15'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E16')), 'etg'] = '16'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E17')), 'etg'] = '17'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E18')), 'etg'] = '18'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E19')), 'etg'] = '19'
        tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E20')), 'etg'] = '20'

    # sensorType:
    tableUtilisations.loc[(tableUtilisations['sensorType'].str.contains('DESK')), 'sensorType'] = 'DESK'
    tableUtilisations.loc[(tableUtilisations['sensorType'].str.contains('CEILING')), 'sensorType'] = 'CEILING'
elif(client == 'CD92'):
    # Batiments :
    tableUtilisations.loc[(tableUtilisations['bat'].str.contains('UAR')), 'bat'] = 'UArena'
    # Etages :
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('SS')), 'etg'] = '-1'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E00')), 'etg'] = '0'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E01')), 'etg'] = '1'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E02')), 'etg'] = '2'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E03')), 'etg'] = '3'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E04')), 'etg'] = '4'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E05')), 'etg'] = '5'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E06')), 'etg'] = '6'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E07')), 'etg'] = '7'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E08')), 'etg'] = '8'
    tableUtilisations.loc[(tableUtilisations['etg'].str.contains('E09')), 'etg'] = '9'
    # nbreDeCapteursParEtage
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('SS')), 'nbrePostesEtg'] = '3'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E00')), 'nbrePostesEtg'] = '3'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E01')), 'nbrePostesEtg'] = '1'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E02')), 'nbrePostesEtg'] = '12'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E03')), 'nbrePostesEtg'] = '15'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E04')), 'nbrePostesEtg'] = '12'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E05')), 'nbrePostesEtg'] = '15'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E06')), 'nbrePostesEtg'] = '15'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E07')), 'nbrePostesEtg'] = '9'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E08')), 'nbrePostesEtg'] = '19'
    tableUtilisations.loc[(tableUtilisations['nbrePostesEtg'].str.contains('E09')), 'nbrePostesEtg'] = '1'


tableUtilisations.reset_index(drop='True', inplace=True)


def tableOccupations(df):
    wxData = df.to_numpy()

    sigfoxID = []
    t7_8, t8_9, t9_10, t10_11, t11_12, t12_13, t13_14, t14_15, t15_16, t16_17, t17_18, t18_19, t19_20, t20_21 = [
                                                                                                                    0] * len(
        wxData), [0] * len(wxData), [0] * len(wxData), [0] * len(wxData), [0] * len(wxData), [0] * len(wxData), [
                                                                                                                    0] * len(
        wxData), [0] * len(wxData), [0] * len(wxData), [0] * len(wxData), [0] * len(wxData), [0] * len(wxData), [
                                                                                                                    0] * len(
        wxData), [0] * len(wxData)

    for i in range(len(wxData)):
        sigfoxID.append(wxData[i][0])
        if (wxData[i][4] >= '07:00:00' and wxData[i][4] < '08:00:00'):
            t7_8[i] = 1
        if (wxData[i][4] >= '08:00:00' and wxData[i][4] < '09:00:00'):
            t8_9[i] = 1
        if (wxData[i][4] >= '09:00:00' and wxData[i][4] < '10:00:00'):
            t9_10[i] = 1
        if (wxData[i][4] >= '10:00:00' and wxData[i][4] < '11:00:00'):
            t10_11[i] = 1
        if (wxData[i][4] >= '11:00:00' and wxData[i][4] < '12:00:00'):
            t11_12[i] = 1
        if (wxData[i][4] >= '12:00:00' and wxData[i][4] < '13:00:00'):
            t12_13[i] = 1
        if (wxData[i][4] >= '13:00:00' and wxData[i][4] < '14:00:00'):
            t13_14[i] = 1
        if (wxData[i][4] >= '14:00:00' and wxData[i][4] < '15:00:00'):
            t14_15[i] = 1
        if (wxData[i][4] >= '15:00:00' and wxData[i][4] < '16:00:00'):
            t15_16[i] = 1
        if (wxData[i][4] >= '16:00:00' and wxData[i][4] < '17:00:00'):
            t16_17[i] = 1
        if (wxData[i][4] >= '17:00:00' and wxData[i][4] < '18:00:00'):
            t17_18[i] = 1
        if (wxData[i][4] >= '18:00:00' and wxData[i][4] < '19:00:00'):
            t18_19[i] = 1
        if (wxData[i][4] >= '19:00:00' and wxData[i][4] < '20:00:00'):
            t19_20[i] = 1
        if (wxData[i][4] >= '20:00:00' and wxData[i][4] < '21:00:00'):
            t20_21[i] = 1

    table = pd.DataFrame(list(
        zip(sigfoxID, t7_8, t8_9, t9_10, t10_11, t11_12, t12_13, t13_14, t14_15, t15_16, t16_17, t17_18, t18_19, t19_20,
            t20_21)),
                         columns=['SigfoxID', 't7_8', 't8_9', 't9_10', 't10_11', 't11_12', 't12_13', 't13_14', 't14_15',
                                  't15_16', 't16_17', 't17_18', 't18_19', 't19_20', 't20_21'])

    return table


tableOccupations = tableOccupations(tableUtilisations)




#st.set_page_config(page_title="Dashboard", layout="wide")


st.sidebar.header("Filtres :")

Batiment = st.sidebar.multiselect("Selectionner le batiment :",
    options =  tableUtilisations['bat'].unique(),
    default =  tableUtilisations['bat'].unique()
)

Etage = st.sidebar.multiselect("Selectionner l'étage:",
    options =  tableUtilisations['etg'].unique(),
    default =  tableUtilisations['etg'].unique()
)

sensorType = st.sidebar.multiselect("Selectionner le type de capteur:",
    options =  tableUtilisations['sensorType'].unique(),
    default =  tableUtilisations['sensorType'].unique()
)

Date = st.sidebar.multiselect("Selectionner les Date:",
    options =  tableUtilisations['date'].unique(),
    default =  tableUtilisations['date'].unique()
)

trancheHoraire = st.sidebar.multiselect("Tranche Horaire :",
    options =  tableUtilisations['trancheHoraire'].unique(),
    default =  tableUtilisations['trancheHoraire'].unique()
)

if(client != 'CD92'):
    zone = st.sidebar.multiselect("Zone :",
        options =  tableUtilisations['zone'].unique(),
        default =  tableUtilisations['zone'].unique()
    )

    tableUtilisations_selection = tableUtilisations.query(
            "bat == @Batiment & etg == @Etage & sensorType == @sensorType & date == @Date & trancheHoraire == @trancheHoraire & zone == @zone"
        )


if(client=='CD92'):
    tableUtilisations_selection = tableUtilisations.query(
        "bat == @Batiment & etg == @Etage & sensorType == @sensorType & date == @Date & trancheHoraire == @trancheHoraire"  # Car pas de zones dans CD92
    )

tableOccupations['bat'] = tableUtilisations['bat']
tableOccupations['etg'] = tableUtilisations['etg']
tableOccupations['sensorType'] = tableUtilisations['sensorType']

tableOccupations_selection = tableOccupations.query(
    "bat == @Batiment & etg == @Etage & sensorType == @sensorType"
)

d1 = np.ceil(tableOccupations_selection.groupby(['SigfoxID']).sum() / 20 )
d1['etg'] = list(tableOccupations_selection.groupby(['SigfoxID','etg','bat']).sum().reset_index()['etg'])
d1['bat'] = list(tableOccupations_selection.groupby(['SigfoxID','etg','bat']).sum().reset_index()['bat'])




# ---- Main Page ------

st.title(":bar_chart: Sensor Data Analysis")
st.markdown('---')

#st.dataframe(tableUtilisations_selection)

# Durée moyenne d'occupation des postes par étage

dureeMoyOccupPostes = (
    tableUtilisations_selection.groupby(['etg'])['Duree'].mean()
)

fig_dureeMoyOccupPostes = px.bar(
    dureeMoyOccupPostes,
    title="<b>Durée moyenne occupation des postes</b>",
    color_discrete_sequence=["#0083B8"] * len(dureeMoyOccupPostes),
    template="plotly_white",

)

st.plotly_chart(fig_dureeMoyOccupPostes)




st.markdown('---')
# Nombre de postes occupés par heure



nbrePostesOccupParHeure = (
    d1.groupby(['etg']).sum().reset_index().transpose()[2:]
)

if(client=='CD92'):
    nbrePostesOccupParHeure = nbrePostesOccupParHeure.rename(columns={0:'-1',1:0,2:1,3:2,4:3,5:4,6:5,7:6,8:7,9:8})

fig_nbrePostesOccupParHeure = px.line(
    nbrePostesOccupParHeure,
    title="<b>Nombre de postes occupés par heure</b>",
    color_discrete_sequence=["#0083B8"] * len(nbrePostesOccupParHeure),
    template="plotly_white",labels=
    {
        "variable":"Etage"
    }

)

st.plotly_chart(fig_nbrePostesOccupParHeure)
st.text(nbrePostesOccupParHeure)


#Taux d'occupation par heure

st.markdown('---')
d1 = d1.groupby(['etg']).sum()
d1['nbrePostesEtg'] = tableUtilisations_selection.groupby(['etg']).first()['nbrePostesEtg'].astype(int)



try:
    TxOccupParHeureEtg3 = (
        np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['3']]
    )
except:
    TxOccupParHeureEtg3 = [0]

try:
    TxOccupParHeureEtg4 = (
        np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['4']]
    )
except:
    TxOccupParHeureEtg4 = [0]

try:
    TxOccupParHeureEtg5 = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['5']]
    )
except:
    TxOccupParHeureEtg5 = [0]
try:
    TxOccupParHeureEtg5 = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['5']]
    )
except:
    TxOccupParHeureEtg5 = [0]
try:
    TxOccupParHeureEtg6 = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['6']]
    )
except:
    TxOccupParHeureEtg6 = [0]
try:
    TxOccupParHeureEtg7 = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['7']]
    )
except:
    TxOccupParHeureEtg7 = [0]
try:
    TxOccupParHeureEtg8 = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['8']]
    )
except:
    TxOccupParHeureEtg8 = [0]
try:
    TxOccupParHeureEtgSS = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['-1']]
    )
except:
    TxOccupParHeureEtgSS = [0]
try:
    TxOccupParHeureEtg0 = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['0']]
    )
except:
    TxOccupParHeureEtg0 = [0]
try:
    TxOccupParHeureEtg1 = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['1']]
    )
except:
    TxOccupParHeureEtg1 = [0]
try:
    TxOccupParHeureEtg2 = (
    np.around((d1.iloc[:,0:14].transpose() / d1['nbrePostesEtg'])*100)[['2']]
    )
except:
    TxOccupParHeureEtg2 = [0]



fig_TxOccupParHeureEtg3 = px.bar(
    TxOccupParHeureEtg3,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>"  ,
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg3),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)

fig_TxOccupParHeureEtg4 = px.bar(
    TxOccupParHeureEtg4,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg4),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)
fig_TxOccupParHeureEtg5 = px.bar(
    TxOccupParHeureEtg5,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg5),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)

fig_TxOccupParHeureEtg6 = px.bar(
    TxOccupParHeureEtg6,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg6),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)

fig_TxOccupParHeureEtg7 = px.bar(
    TxOccupParHeureEtg7,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg7),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)

fig_TxOccupParHeureEtg8 = px.bar(
    TxOccupParHeureEtg8,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg8),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)

fig_TxOccupParHeureEtgSS = px.bar(
    TxOccupParHeureEtgSS,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtgSS),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)

fig_TxOccupParHeureEtg0 = px.bar(
    TxOccupParHeureEtg0,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg0),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)

fig_TxOccupParHeureEtg1 = px.bar(
    TxOccupParHeureEtg1,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg1),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)

fig_TxOccupParHeureEtg2 = px.bar(
    TxOccupParHeureEtg2,text_auto=True,
    title="<b>Taux d'occupation par heure du " + tableUtilisations_selection['date'].min() + " au " + tableUtilisations_selection['date'].max() + "</b>",
    color_discrete_sequence=["#0083B8"] * len(TxOccupParHeureEtg2),
    template="plotly_white",labels={
                     "value": "Taux d'occupation en %",
                     "index": "Tranches horaires",
                     "etg": "Etage"
                 }

)


st.plotly_chart(fig_TxOccupParHeureEtgSS)
st.plotly_chart(fig_TxOccupParHeureEtg0)
st.plotly_chart(fig_TxOccupParHeureEtg1)
st.plotly_chart(fig_TxOccupParHeureEtg2)
st.plotly_chart(fig_TxOccupParHeureEtg3)
st.plotly_chart(fig_TxOccupParHeureEtg4)
st.plotly_chart(fig_TxOccupParHeureEtg5)
st.plotly_chart(fig_TxOccupParHeureEtg6)
st.plotly_chart(fig_TxOccupParHeureEtg7)
st.plotly_chart(fig_TxOccupParHeureEtg8)



st.markdown('---')
#Durée moyenne d'utilisation des postes par étage
dureeMoyUtilPostes = (
    tableUtilisations_selection.groupby(['bat','etg','SigfoxID'])['Duree'].sum().to_frame().groupby(['etg']).mean()
)

fig_dureeMoyUtilPostes = px.bar(
    dureeMoyUtilPostes,
    title="<b>Durée moyenne d'utilisation des postes par étage</b>",
    color_discrete_sequence=["#0083B8"] * len(dureeMoyUtilPostes),
    template="plotly_white",

)

st.plotly_chart(fig_dureeMoyUtilPostes)

st.markdown('---')
#Plus longues durées d'occupations
postesLesPlusLgtpmsUtil = (
    tableUtilisations_selection.groupby(['SigfoxID']).last()['OccupationTotale'].nlargest(10).to_frame()
)


fig_postesLesPlusLgtpmsUtil = px.bar(
    postesLesPlusLgtpmsUtil,
    title="<b>Plus longues durées d'occupation</b>",
    color_discrete_sequence=["#0083B8"] * len(postesLesPlusLgtpmsUtil),
    template="plotly_white",

)

st.plotly_chart(fig_postesLesPlusLgtpmsUtil)

st.markdown('---')
#Postes les moins longtemps utilisés
postesLesMoinsLgtpmsUtil = (
    tableUtilisations_selection.groupby(['SigfoxID']).last()['OccupationTotale'].nsmallest(3).to_frame()
)


fig_postesLesMoinsLgtpmsUtil = px.bar(
    postesLesMoinsLgtpmsUtil,
    title="<b>Postes les moins longtemps utilisés</b>",
    color_discrete_sequence=["#0083B8"] * len(postesLesMoinsLgtpmsUtil),
    template="plotly_white",

)

st.plotly_chart(fig_postesLesMoinsLgtpmsUtil)

st.markdown('---')
#Postes les plus sollicités dans la journée
postesLesPlusSol = (
    tableUtilisations_selection.groupby(['SigfoxID'])['SigfoxID'].count().nlargest(5).to_frame()
)


fig_postesLesPlusSol = px.bar(
    postesLesPlusSol,
    title="<b>Postes les plus sollicités</b>",
    color_discrete_sequence=["#0083B8"] * len(postesLesPlusSol),
    template="plotly_white",

)

st.plotly_chart(fig_postesLesPlusSol)

st.markdown('---')
#Nombre d'occupations par tranche horaire par etage
nbreOccupParH = (
    tableOccupations_selection.groupby(['etg']).sum().transpose()
)


fig_nbreOccupParH = px.bar(
    nbreOccupParH,
    title="<b>Nombre d'occupations par tranche horaire par etage</b>",
    color_discrete_sequence=["#0083B8"] * len(nbreOccupParH),
    template="plotly_white",
)

st.plotly_chart(fig_nbreOccupParH)






