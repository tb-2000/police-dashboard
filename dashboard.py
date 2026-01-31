import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Crime Data Dashboard",
    layout="wide"
)

# Title
st.title("Crime Data Dashboard")

# Create sidebar for controls
st.sidebar.header("Controls")

# File upload section
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or JSON file",
    type=["csv", "json"],
    help="Upload a file containing crime data with the specified columns."
)

# Function to load data based on file type
def load_data(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.json'):
            df = pd.read_json(uploaded_file)
        
        # Convert data types according to specifications
        df['INCIDENT_NUMBER'] = df['INCIDENT_NUMBER'].astype(str)
        df['OFFENSE_CODE'] = df['OFFENSE_CODE'].astype('int64')
        df['OFFENSE_CODE_GROUP'] = df['OFFENSE_CODE_GROUP'].astype(str)
        df['OFFENSE_DESCRIPTION'] = df['OFFENSE_DESCRIPTION'].astype(str)
        df = df.dropna(subset=['DISTRICT'])
        df['DISTRICT'] = df['DISTRICT'].astype(str)
        df['REPORTING_AREA'] = df['REPORTING_AREA'].astype(str)
        df['SHOOTING'] = df['SHOOTING'].astype(str)
        df['OCCURRED_ON_DATE'] = pd.to_datetime(df['OCCURRED_ON_DATE'])
        df['YEAR'] = df['YEAR'].astype('int64')
        df['MONTH'] = df['MONTH'].astype('int64')
        df['DAY_OF_WEEK'] = df['DAY_OF_WEEK'].astype(str)
        df['HOUR'] = df['HOUR'].astype('int64')
        df = df.dropna(subset=['UCR_PART'])
        df['UCR_PART'] = df['UCR_PART'].astype(str)
        df['STREET'] = df['STREET'].astype(str)
        df['Lat'] = df['Lat'].astype('float64')
        df['Long'] = df['Long'].astype('float64')
        df['Location'] = df['Location'].astype(str)
        
        return df
    return None

# Function to create gauge chart
def create_gauge(value, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, value * 1.2]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, value * 0.5], 'color': "lightgray"},
                {'range': [value * 0.5, value * 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value * 0.9
            }
        }
    ))
    return fig

# Load data if file is uploaded
if uploaded_file is not None:
    crime_data = load_data(uploaded_file)
    
    # Add date filter
    st.sidebar.subheader("Date Filter")
    min_date = crime_data['OCCURRED_ON_DATE'].min().to_pydatetime()
    max_date = crime_data['OCCURRED_ON_DATE'].max().to_pydatetime()
    
    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        [min_date.date(), max_date.date()],
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    # Add district filter
    st.sidebar.subheader("District Filter")
    all_districts = crime_data['DISTRICT'].unique()
    selected_districts = st.sidebar.multiselect(
        "Select Districts",
        options=all_districts,
        default=all_districts
    )
    
    # Filter data based on selections
    crime_data_filtered = crime_data.copy()
    
    # Apply date filter
    if len(selected_dates) == 2:
        start_date = pd.to_datetime(selected_dates[0])
        end_date = pd.to_datetime(selected_dates[1])
        crime_data_filtered = crime_data_filtered[
            (crime_data_filtered['OCCURRED_ON_DATE'] >= start_date) & 
            (crime_data_filtered['OCCURRED_ON_DATE'] <= end_date)
        ]
    
    # Apply district filter
    if selected_districts:
        crime_data_filtered = crime_data_filtered[
            crime_data_filtered['DISTRICT'].isin(selected_districts)
        ]
    
    # Calculate metrics for gauges
    total_crimes = len(crime_data_filtered)
    total_part_one = len(crime_data_filtered[crime_data_filtered['UCR_PART'] == 'Part One'])
    total_shootings = len(crime_data_filtered[crime_data_filtered['SHOOTING'] == 'Y'])
    
    # Display gauge metrics at the top (smaller)
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(create_gauge(total_part_one, "Serious Crimes (Part One)", "blue"), 
                       config={'displayModeBar': False, 'responsive': True,
                               'width': 'stretch', 'height': 200})
    
    with col2:
        st.plotly_chart(create_gauge(total_crimes, "Total Crimes", "green"), 
                       config={'displayModeBar': False, 'responsive': True,
                               'width': 'stretch', 'height': 200})
    
    with col3:
        st.plotly_chart(create_gauge(total_shootings, "Shooting Incidents", "red"), 
                       config={'displayModeBar': False, 'responsive': True,
                               'width': 'stretch', 'height': 200})
    
    # Display scatter map below gauges
    st.write("### Crime Locations")
    # Filter out rows with missing coordinates
    # Ungültige / fehlende Koordinaten → NaN machen
    # Replace -1 values in Lat/Long with Nan
    df_clean = crime_data_filtered.copy()
    df_clean.Lat = df_clean.Lat.replace(-1.0, np.nan)
    df_clean.Long = df_clean.Long.replace(-1.0, np.nan)
    df_clean.UCR_PART = df_clean.UCR_PART.replace('', np.nan)
    crime_locations = df_clean.dropna(subset=['Lat', 'Long', 'UCR_PART'])
    
    fig_map = px.scatter_mapbox(
        crime_locations,
        lat='Lat',
        lon='Long',
        hover_name='OFFENSE_DESCRIPTION',
        hover_data=['DISTRICT', 'OFFENSE_CODE_GROUP'],
        color='UCR_PART',
        color_discrete_map={
            'Part One': 'red',
            'Part Two': 'orange',
            'Part Three': 'yellow'
        },
        zoom=10,
        height=500,
        title="Crime Locations"
    )
    
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig_map, 
                   config={'displayModeBar': False, 'scrollZoom': True, 'doubleClick': 'reset+autoscale','responsive': True,
                           'width' : 'stretch'})
    
    # Display remaining plots in 2x2 grid
    st.subheader("Crime Analysis")
    
    # Create 2x2 grid
    col1, col2 = st.columns(2)
    
    # Plot 1: Top 10 Offense Code Groups (top-left)
    with col1:
        st.write("### Top 10 Offense Code Groups")
        top_offense_groups = crime_data_filtered['OFFENSE_CODE_GROUP'].value_counts().head(10)
        fig_offense_groups = px.bar(
            x=top_offense_groups.values,
            y=top_offense_groups.index,
            orientation='h',
            labels={'x': 'Number of Crimes', 'y': 'Offense Code Group'},
            title="Top 10 Offense Code Groups"
        )
        fig_offense_groups.update_layout(height=400)
        st.plotly_chart(fig_offense_groups, 
                       config={'displayModeBar': False, 'responsive': True,
                               'width': 'stretch'})
    
    # Plot 2: Crimes by District (top-right) - with NaN values removed
    with col2:
        st.write("### Crimes by District")
        # Remove rows with NaN in DISTRICT
        df_clean = crime_data_filtered.copy()
        df_clean.DISTRICT = df_clean.DISTRICT.replace('', np.nan)
        df_clean = df_clean.dropna(subset=['DISTRICT'])

        district_counts = df_clean['DISTRICT'].value_counts().sort_values(ascending=False)
        fig_district = px.bar(
            x=district_counts.index,
            y=district_counts.values,
            labels={'x': 'District', 'y': 'Number of Crimes'},
            title="Crimes by District"
        )
        fig_district.update_layout(height=400)
        st.plotly_chart(fig_district, 
                       config={'displayModeBar': False, 'responsive': True,
                               'width': 'stretch'})
    
    # Create second row of 2x2 grid
    col3, col4 = st.columns(2)
    
    # Plot 3: Crimes by Day (bottom-left)
    with col3:
        st.write("### Crimes Committed by Day")
        day_counts = crime_data_filtered['DAY_OF_WEEK'].value_counts()
        # Ensure days are in order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = day_counts.reindex(day_order, fill_value=0)
        
        fig_bar = px.bar(
            x=day_counts.index,
            y=day_counts.values,
            labels={'x': 'Day of Week', 'y': 'Number of Crimes'},
            title="Crimes Committed by Day"
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, 
                       config={'displayModeBar': False, 'responsive': True,
                               'width': 'stretch'})
    
    # Plot 4: Crimes per Hour by UCR Part (bottom-right)
    with col4:
        st.write("### Crimes Per Hour by UCR Part")
        filtered_data = crime_data_filtered[
            (crime_data_filtered.UCR_PART == "Part One") | 
            (crime_data_filtered.UCR_PART == "Part Two") |
            (crime_data_filtered.UCR_PART == "Part Three")
        ]
        
        hourly_crime = filtered_data.groupby(['HOUR', 'UCR_PART']).size().reset_index(name='count')
        
        fig_line = px.line(
            hourly_crime,
            x='HOUR',
            y='count',
            color='UCR_PART',
            labels={'HOUR': 'Hour of Day', 'count': 'Number of Crimes', 'UCR_PART': 'Crime Severity'},
            title="Crimes Per Hour by UCR Part",
            markers=True
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, 
                       config={'displayModeBar': False, 'responsive': True,
                               'width' : 'stretch'})
    
    # Display basic information about the filtered dataset
    st.sidebar.subheader("Dataset Information")
    st.sidebar.write(f"Total Records: {len(crime_data_filtered)}")
    st.sidebar.write(f"Date Range: {crime_data_filtered['OCCURRED_ON_DATE'].min().date()} to {crime_data_filtered['OCCURRED_ON_DATE'].max().date()}")
else:
    st.write("Please upload a CSV or JSON file to begin the analysis.")