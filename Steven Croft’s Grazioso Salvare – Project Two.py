#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# ProjectTwoDashboard.ipynb

# --- Imports ---
from jupyter_dash import JupyterDash
import dash_leaflet as dl
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Import CRUD module
from animal_shelter import AnimalShelter

# --- Database Connection ---
username = "aacuser1"
password = "SNHU1234"   
shelter = AnimalShelter(username, password)

# --- Helper: Convert Mongo cursor to DataFrame ---
def load_data(query={}):
    data = pd.DataFrame(list(shelter.read(query)))
    if "_id" in data.columns:
        data.drop(columns=["_id"], inplace=True)
    return data

# Initial full dataset
df = load_data()

# --- Dash App Setup ---
app = JupyterDash(__name__)

# Grazioso Salvare logo 
logo = "grazioso_logo.png"

app.layout = html.Div([
    html.Div([
        html.Img(src=logo, style={"height":"100px"}),
        html.H3("Grazioso Salvare Dashboard - [Steven Croft]")
    ], style={"textAlign":"center"}),

    # Filter Options
    html.Div([
        html.Label("Select Rescue Type:"),
        dcc.RadioItems(
            id="rescue-type",
            options=[
                {"label":"All", "value":"reset"},
                {"label":"Water Rescue", "value":"water"},
                {"label":"Mountain/Wilderness Rescue", "value":"mountain"},
                {"label":"Disaster/Individual Tracking", "value":"disaster"}
            ],
            value="reset",
            labelStyle={"display":"block"}
        )
    ], style={"width":"20%", "float":"left"}),

    # Data Table
    html.Div([
        dash_table.DataTable(
            id="datatable",
            columns=[{"name":i, "id":i} for i in df.columns],
            data=df.to_dict("records"),
            page_size=10,
            style_table={"overflowX":"auto"},
            filter_action="native",
            sort_action="native"
        )
    ], style={"width":"75%", "float":"right"}),

    html.Div(style={"clear":"both"}),

    # Charts
    html.Div([
        dcc.Graph(id="breed-chart"),
        dl.Map(center=[30.27,-97.74], zoom=10, children=[dl.TileLayer(), dl.LayerGroup(id="map-points")],
               style={"width":"100%","height":"500px"})
    ])
])

# --- Callbacks ---

@app.callback(
    [Output("datatable", "data"),
     Output("breed-chart", "figure"),
     Output("map-points", "children")],
    [Input("rescue-type", "value")]
)
def update_dashboard(rescue_type):
    # Define queries based on rescue type
    if rescue_type == "water":
        query = {"$and":[
            {"animal_type":"Dog"},
            {"age_upon_outcome_in_weeks":{"$lte":104}},
            {"breed":{"$in":["Labrador Retriever Mix","Chesapeake Bay Retriever","Newfoundland"]}}
        ]}
    elif rescue_type == "mountain":
        query = {"$and":[
            {"animal_type":"Dog"},
            {"age_upon_outcome_in_weeks":{"$lte":156}},
            {"breed":{"$in":["German Shepherd","Alaskan Malamute","Old English Sheepdog",
                             "Siberian Husky","Rottweiler"]}}
        ]}
    elif rescue_type == "disaster":
        query = {"$and":[
            {"animal_type":"Dog"},
            {"age_upon_outcome_in_weeks":{"$lte":300}},
            {"breed":{"$in":["Doberman Pinscher","German Shepherd","Golden Retriever",
                             "Bloodhound","Rottweiler"]}}
        ]}
    else:  # reset
        query = {}

    # Load data
    df_new = load_data(query)

    # Breed chart
    if len(df_new) > 0:
        fig = px.histogram(df_new, x="breed", title="Breed Distribution")
    else:
        fig = px.histogram(title="No data found")

    # Map points
    map_points = []
    if "location_lat" in df_new.columns and "location_long" in df_new.columns:
        for _, row in df_new.iterrows():
            if pd.notnull(row["location_lat"]) and pd.notnull(row["location_long"]):
                map_points.append(
                    dl.Marker(position=[row["location_lat"], row["location_long"]])
                )

    return df_new.to_dict("records"), fig, map_points


# --- Run App ---
app.run_server(mode="inline")


# In[ ]:


#


# In[ ]:




