import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import plotly.express as px
import os
import warnings
import csv
import folium
import plotly
import matplotlib.pyplot as plt 
import plotly.figure_factory as ff
warnings.filterwarnings('ignore')

st.set_page_config(page_title = "SuperSklep", 
                   page_icon = ":chart_with_upwards_trend:", layout= "wide")
st.title(" :bar_chart: Dashboard finansowy SuperSklepu")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', 
            unsafe_allow_html = True)

plik = st.file_uploader(":file_folder: Wybierz plik",
                         type =(["csv", "txt", "xlsx", "xls"]))
if plik is not None:
    nazwa_pliku = plik.name
    st.write(nazwa_pliku)
    df = pd.read_csv(nazwa_pliku, encoding = "ISO-8859-1", sep=';')
else:
    os.chdir(r"C:\Users\Laptop\Desktop\Dashboard")   
    df = pd.read_csv("Sample - Superstore.csv", encoding = "ISO-8859-1", sep=';')


kolumna1, kolumna2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d.%m.%Y")
df['Sales'] = df['Sales'].str.replace(',', '.').astype(float)

data_początkowa = pd.to_datetime(df["Order Date"], format="%d.%m.%Y").min()
data_końcowa = pd.to_datetime(df["Order Date"], format="%d.%m.%Y").max()

with kolumna1:
    data1 = pd.to_datetime(st.date_input("Data początkowa", data_początkowa))

with kolumna2:
    data2 = pd.to_datetime(st.date_input("Data końcowa", data_końcowa))

df = df[(df["Order Date"] >= data1) & (df["Order Date"] <= data2)].copy()

st.sidebar.header("Wybierz swój filtr: ")
#filtr dla Regionu
region = st.sidebar.multiselect("Wybierz Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]
#filtr dla Stanu
stan = st.sidebar.multiselect("Wybierz Stan", df2["State"].unique())
if not stan:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(stan)]
#filtr dla Miasta
miasto = st.sidebar.multiselect("Wybierz Miasto",df3["City"].unique())

# Filtruj dane na podstawie Regionu, Stanu i Miasta
if not region and not stan and not miasto:
    dane_filtr = df
elif not stan and not miasto:
    dane_filtr = df[df["Region"].isin(region)]
elif not region and not miasto:
    dane_filtr = df[df["State"].isin(stan)]
elif stan and miasto:
    dane_filtr = df3[df["State"].isin(stan) & df3["City"].isin(miasto)]
elif region and miasto:
    dane_filtr = df3[df["Region"].isin(region) & df3["City"].isin(miasto)]
elif region and stan:
    dane_filtr = df3[df["Region"].isin(region) & df3["State"].isin(stan)]
elif miasto:
    dane_filtr = df3[df3["City"].isin(miasto)]
else:
    dane_filtr = df3[df3["Region"].isin(region) & df3["State"].isin(stan) & df3["City"].isin(miasto)]

st.text(" ")

kategoria_df = dane_filtr.groupby(by = ["Category"], as_index = False)["Sales"].sum()
with kolumna1:
    st.subheader("Sprzedaż według kategorii")
    fig = px.bar(kategoria_df, x = "Category", y = "Sales", 
                 text = ['${:,.2f}'.format(x) for x in kategoria_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)

with kolumna2:
    st.subheader("Sprzedaż według Regionu")
    fig = px.pie(dane_filtr, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = dane_filtr["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

kolumna3, kolumna4 = st.columns((2))
with kolumna3:
    with st.expander("Wyświetl Dane Kategorii"):
        st.write(kategoria_df.style.background_gradient(cmap="Blues"))
        csv = kategoria_df.to_csv(index = False).encode('utf-8')
        st.download_button("Pobierz Dane", data = csv, file_name = "Kategorie.csv", mime = "text/csv",
                            help = 'Kliknij tutaj, aby pobrać dane jako plik CSV')

with kolumna4:
    with st.expander("Wyświetl Dane Regionów"):
        region = dane_filtr.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Pobierz Dane", data = csv, file_name = "Regiony.csv", mime = "text/csv",
                        help = 'Kliknij tutaj, aby pobrać dane jako plik CSV')
        
st.text(" ")
st.text(" ")


#wykres z szereniem czasowym 
st.subheader('Analiza Szeregu Czasowego')
dane_filtr["miesiąc_rok"] = dane_filtr["Order Date"].dt.to_period("M")
wykres_liniowy = pd.DataFrame(dane_filtr.groupby(dane_filtr["miesiąc_rok"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()

fig2 = px.line(wykres_liniowy, x = "miesiąc_rok", y="Sales", 
               labels = {"Sales": "Kwota"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("Wyświetl Dane Szeregu Czasowego:"):
    st.write(wykres_liniowy.T.style.background_gradient(cmap="Blues"))
    csv = wykres_liniowy.to_csv(index=False).encode("utf-8")
    st.download_button('Pobierz Dane', data = csv, file_name = "SzeregCzasowy.csv", mime ='text/csv')

st.text(" ")
st.text(" ")
# Tworzenie drzewa na podstawie Regionu, kategorii, pod-kategorii
st.subheader("Drzewo hierarchiczne sprzedaży według Regionu, Kategorii i Podkategorii")
fig3 = px.treemap(dane_filtr, path=["Region", "Category", "Sub-Category"],
                   values="Sales", hover_data=["Sales"],color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)


wykres1, wykres2 = st.columns((2))
with wykres1:
    st.subheader('Sprzedaż według segmentów')
    fig = px.pie(dane_filtr, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=dane_filtr["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with wykres2:
    st.subheader('Sprzedaż według kategorii')
    fig = px.pie(dane_filtr, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=dane_filtr["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

st.text(" ")
# wykres z marżą
dane_filtr['Profit'] = dane_filtr['Profit'].str.replace(',', '.').astype(float)
dane_filtr['Profit Margin'] = (dane_filtr['Profit'] / dane_filtr['Sales']) * 100
dane_filtr['Gross Margin'] = ((dane_filtr['Sales'] - 
                               dane_filtr['Profit']) / dane_filtr['Sales']) * 100
# Wykres marży zysku dla każdej kategorii
fig_profit_margin = px.bar(dane_filtr, x='Sub-Category', y='Profit Margin',
                            title='Marża zysku dla każdej kategorii',
                            labels={'Profit Margin': 'Marża zysku (%)',
                                     'Sub-Category': 'Kategoria'})
# Wykres marży brutto dla każdej kategorii
fig_gross_margin = px.bar(dane_filtr, x='Sub-Category', y='Gross Margin', 
                          title='Marża brutto dla każdej kategorii',
                           labels={'Gross Margin': 'Marża brutto (%)', 
                                   'Sub-Category': 'Kategoria'})

st.subheader('Analiza opłacalności produktów')
st.plotly_chart(fig_profit_margin, use_container_width=True)
st.plotly_chart(fig_gross_margin, use_container_width=True)

grouped_data = dane_filtr.groupby('Sub-Category').agg({
    'Profit Margin': 'sum',
    'Gross Margin': 'sum'
}).reset_index()

with st.expander("Wyświetl dane marż:"):
    st.write(grouped_data.style.background_gradient(cmap="Blues"))
    csv = grouped_data.to_csv(index=False).encode("utf-8")
    st.download_button('Pobierz Dane', data = csv,
                        file_name = "Marża.csv", mime ='text/csv')


st.text(" ")



#wykres z miesięcznym zyskiem 
st.subheader('Średni zysk z danych segmentów w poszczególnych miesiącach')
dane_filtr['Month'] = dane_filtr['Order Date'].dt.strftime('%B')
kolejnosc_miesiecy = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
pivot_data = pd.pivot_table(dane_filtr, values='Profit', index='Month', columns='Segment', 
                            aggfunc='mean').reset_index()
fig6 = px.bar(pivot_data, x='Month', y=['Consumer', 'Home Office', 'Corporate'],
               color_discrete_map={"Consumer": "#1f77b4", "Home Office": "#ff7f0e", 
                "Corporate": "#2ca02c"},category_orders={'Month': kolejnosc_miesiecy})
fig6.update_layout(xaxis_title='Miesiąc', yaxis_title='Średni Profit', legend_title='Segment')
st.plotly_chart(fig6)

st.text(" ")
st.text(" ")

#Tabela zmian cen
st.subheader('Zmiana ceny produktów względem poprzedniego roku')
available_years = dane_filtr['Order Date'].dt.year.unique()
available_years.sort()
chosen_year = st.selectbox("Wybierz rok", available_years[1:])

data_selected_year = dane_filtr[dane_filtr['Order Date'].dt.year == chosen_year]
data_previous_year = dane_filtr[dane_filtr['Order Date'].dt.year == chosen_year - 1]

grouped_data_selected_year = data_selected_year.groupby('Sub-Category')['Sales'].sum().reset_index()
grouped_data_previous_year = data_previous_year.groupby('Sub-Category')['Sales'].sum().reset_index()

merged_data = pd.merge(grouped_data_selected_year, grouped_data_previous_year, 
                       on='Sub-Category', suffixes=('', '_previous'))
merged_data['Sales Change (%)'] = ((merged_data['Sales'] - merged_data['Sales_previous']) / 
                                   merged_data['Sales_previous']) * 100
def highlight_changes(val):
    color = 'red' if val < 0 else 'green'
    return 'color: %s ' % color
merged_data.rename(columns={'Sales_previous': 'Sales ' + str(chosen_year - 1), 
                            'Sales': 'Sales ' + str(chosen_year)}, inplace=True)
styled_table = merged_data[['Sub-Category', 'Sales ' + str(chosen_year - 1), 'Sales ' + str(chosen_year),
                             'Sales Change (%)']].style.applymap(highlight_changes, subset=['Sales Change (%)'])
st.table(styled_table)



# zestawienie sprzedaży z zyskiem 
dane1 = px.scatter(dane_filtr, x="Sales", y="Profit", size="Quantity")
dane1['layout'].update(title="Zależność między sprzedażą a zyskiem na wykresie punktowym.",
                       titlefont=dict(size=20), xaxis=dict(title="Sprzedaż", titlefont=dict(size=19)),
                       yaxis=dict(title="Zysk", titlefont=dict(size=19)))
st.plotly_chart(dane1, use_container_width=True)

combined_data = dane_filtr[['Profit', 'Sales', 'Quantity']].copy()
with st.expander("Wyświetl Dane"):
     st.write(combined_data.style.background_gradient(cmap="Oranges"))
     csv = combined_data.to_csv(index=False).encode('utf-8')
     st.download_button('Pobierz Dane', data=csv, file_name="Dane.csv", mime="text/csv")


#Mapa 
state = dane_filtr.groupby(by = "State", as_index = False)["Sales"].sum()
states = gpd.read_file('us-state-boundaries.geojson')
merged_data = states.merge(state, left_on = "name",right_on='State', how='left')

def draw_map(data, color_column, title):
    fig = px.choropleth_mapbox(
        data,
        geojson=data.geometry,
        locations=data.index,
        color=color_column,
        mapbox_style="carto-positron",
        hover_name='name',
        center={"lat": 37.0902, "lon": -95.7129},
        zoom=3,
        height=600,
        title=title,
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig)
st.title("Interaktywna mapa sprzedaży według stanów")
display_option = st.radio(" ", ["Pokaż mapę", "Pokaż dane"])
if display_option == "Pokaż mapę":
    draw_map(merged_data, 'Sales', 'Sprzedaż w Stanach Zjednoczonych')

elif display_option == "Pokaż dane":
    st.write(merged_data[['State', 'Sales']])

st.text(" ")

#Podsumowanie 
st.subheader(":point_right: Podsumowanie sprzedaży podkategorii w poszczególnych miesiącach")
with st.expander("Tabela podsumowania"):
    df_przykład = df[0:5][["Region", "State", "City", "Category", 
                           "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_przykład, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Tabela sprzedaży podkategorii w poszczególnych miesiącach")
    dane_filtr["miesiąc"] = dane_filtr["Order Date"].dt.month_name()
    podkategoria_m = pd.pivot_table(data=dane_filtr, values="Sales", 
                                    index=["Sub-Category"], columns="miesiąc")
    st.write(podkategoria_m.style.background_gradient(cmap="Blues"))
