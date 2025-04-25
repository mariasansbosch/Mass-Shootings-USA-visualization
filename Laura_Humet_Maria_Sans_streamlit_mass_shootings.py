import streamlit as st
import altair as alt
from vega_datasets import data
import pandas as pd
st.set_page_config(layout='wide')

st.write("""
    # Analysis of Mass Shootings across the US
        By Laura Humet and Maria Sans
""")

shootings = pd.read_csv('Q1_final.csv')

# Extracting the state id, which is the first two numbers of its FIPS:
shootings['id'] = shootings['FIPS'].astype(str).str[:-3].astype(int)

# Extracting the keys we need for creating the charts:
info_states = shootings[['State', 'id', 'Population per State', 'Shootings Per State', 'Shootings per 100k Citizens']].drop_duplicates()

# Extracting and sorting the 15 top states with more shootings per 100k citizen:
top_15_states = info_states.sort_values('Shootings per 100k Citizens', ascending=False).head(15)
top_15_states['State'] = pd.Categorical(top_15_states['State'], categories=top_15_states['State'], ordered=True)

# Creating the Bar Chart:
bar_chart_states = alt.Chart(top_15_states).mark_bar().encode(
    x = alt.X('Shootings per 100k Citizens:Q',
          title='Shootings per 100k Citizens'
    ),
    y = alt.Y('State:N', title='State', sort=list(top_15_states['State'])),
    color=alt.value('#D73027')
).transform_lookup(
    lookup='State',
    from_=alt.LookupData(top_15_states, 'State', ['Shootings_per_100k_citizens'])
).properties(
    title="Top 15 States with Highest Mass Shootings per 100k Citizens",
    width=500,
    height=400
)

text = bar_chart_states.mark_text(
    align='left',
    baseline='middle',
    dx=5
).encode(
    text=alt.Text('Shootings per 100k Citizens:Q', format='.2f'),
    color=alt.value('grey')
)

Q1 = bar_chart_states + text

#################################

col1, col2 = st.columns(2)

## CODE PREPARATION ##
q2_source = pd.read_csv('Q2_dataset.csv')

# Extracting the keys necessary for this Chart:
q2 = q2_source[['State', 'County Name', 'County FIPS', 'population']]

# Adding a new column to count the mass shootings in each county and grouping the rows by the county's FIPS:
q2['Shootings_count'] = 1
shootings_count = q2.groupby('County FIPS').agg({'State':'first', 'County Name':'first', 'population':'first', 'Shootings_count':'count'}).reset_index()
shootings_count['Shootings_per_100k_citizens'] = shootings_count['Shootings_count']/shootings_count['population']*100
shootings_count = shootings_count.rename(columns={'County FIPS':'id'}) # Changing the name of the key so it coincides with the one in the map dataset

## FINAL VISUALIZATION ##
counties = alt.topo_feature(data.us_10m.url, 'counties')

map_counties = alt.Chart(counties).mark_geoshape(
    stroke='white'
).encode(
    color= alt.Color(
        'Shootings_per_100k_citizens:Q',
        scale=alt.Scale(scheme='reds', domain=[0, shootings_count['Shootings_per_100k_citizens'].max()]),
        legend=alt.Legend(
            title='Mass Shootings per 100k Citizens',
            orient='right',
            titleFontSize=12,
            labelFontSize=10)
    ),
    tooltip=[alt.Tooltip('County Name:N', title='County Name'), alt.Tooltip('Shootings_per_100k_citizens:Q', title='Mass Shootings')]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(shootings_count, 'id', ['County Name','Shootings_per_100k_citizens'])
).properties(
    title='Mass Shootings per 100k Citizens across the US Counties',
    width=500,
    height=300
).project(
    type='albersUsa'
)

map_background = alt.Chart(counties).mark_geoshape().encode(
    color=alt.value('white'),
    stroke=alt.value('lightgray')
).properties(
    title='Mass Shootings per 100k Citizens across the US Counties',
    width=500,
    height=300
).project(
    type='albersUsa'
)

Q2_counties = alt.layer(map_background, map_counties)

####################################

## FINAL VISUALIZATION ##
info_states = info_states.drop(info_states[info_states['State']=='DISTRICT OF COLUMBIA'].index)
map_states = alt.topo_feature(data.us_10m.url, 'states')

Q2_states = alt.Chart(map_states).mark_geoshape().encode(
    color=alt.Color('Shootings per 100k Citizens:Q',
        scale=alt.Scale(scheme='reds', domain=[0, info_states['Shootings per 100k Citizens'].max()]),
        legend=alt.Legend(
            title='Mass Shootings per 100k Citizens',
            orient='right',
            titleFontSize=12,
            labelFontSize=10)
        ),
    stroke=alt.value('white'),
    tooltip=[alt.Tooltip('State:N', title='State'), alt.Tooltip('Shootings per 100k Citizens:Q', title='Mass Shootings per citizen')]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(info_states, 'id', ['State','Shootings per 100k Citizens']),
    default='0'
).properties(
    title='Mass Shootings per 100k Citizens across the US States',
    width=500,
    height=300
).project(
    type='albersUsa'
)

with col1:
    st.altair_chart(Q2_counties, use_container_width=True)

with col2:
    st.altair_chart(Q2_states, use_container_width=True)

##########################################
    
col3, col4 = st.columns(2)

## CODE PREPARATION ##
school_incidents = pd.read_csv('School-incidents-csv.csv')
school_incidents['FIPS'] = school_incidents['FIPS'].astype('Int64')

mass_shootings = pd.read_csv('dataset-crimes-usa.csv')
mass_shootings['FIPS_State'] = mass_shootings['FIPS_State'].astype('Int64')

vermont_row = pd.DataFrame({
    'FIPS_State': [50],
    'Incident ID': [None],
    'Incident Date': [None],
    'Incident Month': [None],
    'Incident Year': [None],
    'State': ['Vermont'],
    'population': [647464],
    'City Or County': [None],
    'Direction': [None],
    'Latitude': [None],
    'Longitude': [None],
    'Address': [None],
    'Victims Killed': [0],
    'Victims Injured': [0],
    'Suspects Killed': [0],
    'Suspects Injured': [0],
    'Suspects Arrested': [0]
})

# Adding into the DataFrame of mass_shootings the state of Vermont:
mass_shootings = pd.concat([mass_shootings, vermont_row], ignore_index=True)

# Grouping the schools shootings by the State FIPS:
school_counts = school_incidents.groupby('FIPS').size().reset_index(name='School Incidents')

# Grouping the total mass shootings by the State FIPS:
mass_shooting_counts = mass_shootings.groupby('FIPS_State').size().reset_index(name='Mass Shootings')

# Merging the two previous DataFrames:
merged_data = pd.merge(school_counts, mass_shooting_counts, left_on='FIPS', right_on='FIPS_State', how='inner')

# Adding the population of each State:
populations = mass_shootings[['FIPS_State', 'population', 'State']].drop_duplicates()
merged_data = pd.merge(merged_data, populations, left_on='FIPS', right_on='FIPS_State', how='left')

# Computing the proportion of mass shootings per million of citizens for each DataFrame:
merged_data['Mass Shootings per Million'] = (merged_data['Mass Shootings'] / merged_data['population']) * 1_000_000
merged_data['School Incidents per Million'] = (merged_data['School Incidents'] / merged_data['population']) * 1_000_000

## FINAL VISUALUZATION ##
scatter_plot = alt.Chart(merged_data).mark_circle().encode(
    x=alt.X('Mass Shootings per Million', title='Mass Shootings per Million Inhabitants'),
    y=alt.Y('School Incidents per Million', title='School Incidents per Million Inhabitants'),
    size=alt.Size('population:Q', title='Population', legend=alt.Legend(orient='left', labelFontSize=10, symbolSize=15)),
    color=alt.Color('State:N', title='State', legend=alt.Legend(orient='right', columns=2, labelFontSize=10, symbolSize=15)),
    tooltip=['State', 'Mass Shootings', 'School Incidents', 'population',
             'Mass Shootings per Million', 'School Incidents per Million']
).properties(
    title=alt.Title(
        'Correlation between Mass Shootings and School Incidents by State',
        subtitle='Per Million Inhabitants'),
    width=500,
    height=400
)

regression_line = alt.Chart(merged_data).transform_regression(
    'Mass Shootings per Million', 'School Incidents per Million'
).mark_line(color='#D73027').encode(
    x='Mass Shootings per Million:Q',
    y='School Incidents per Million:Q'
)

Q3 = (scatter_plot + regression_line).configure_mark(
    color='steelblue'
)

with col3:
    st.altair_chart(Q1, use_container_width=True)

with col4:
    st.altair_chart(Q3, use_container_width=True)

##############################################

## CODE PREPARATION ##
shootings['Incident Date'] = pd.to_datetime(shootings['Incident Date'])
filtered_data = shootings[(shootings['Incident Date'] >= '2019-01-01') & (shootings['Incident Date'] <= '2023-12-31')]
filtered_data['Year_Month'] = filtered_data['Incident Date'].dt.to_period('M')

monthly_counts = filtered_data.groupby('Year_Month').size().reset_index(name='Mass Shootings')

monthly_counts['Year_Month'] = monthly_counts['Year_Month'].astype(str)

# Extracting the minimum and maximum number of mass shootings per month to represent it in the chart:
monthly_counts['Value_Category'] = 'medium'
monthly_counts.loc[monthly_counts['Mass Shootings'].idxmax(), 'Value_Category'] = 'max'
monthly_counts.loc[monthly_counts['Mass Shootings'].idxmin(), 'Value_Category'] = 'min'

# Calculate the mean number of shootings
mean_shootings = monthly_counts['Mass Shootings'].mean()

## FINAL VISUALIZATION ##
# Create the line chart for mass shootings
line_chart = alt.Chart(monthly_counts).mark_line(point=True, color='#D73027').encode(
    x=alt.X('Year_Month:T',
            title='Month-Year',
            axis=alt.Axis(
                labelAngle=45,
                tickCount=14,
                labelFontSize=10,
                labelPadding=10,
                format='%b %Y'
            )
    ),
    y=alt.Y('Mass Shootings:Q', title='Number of Mass Shootings'),
    tooltip=['Mass Shootings']
).properties(
    title="Evolution of Mass Shootings in the US (2019-2023)",
    width=500,
    height=300,
)

points = alt.Chart(monthly_counts).mark_point(
    #color='darkred'
).encode(
    x='Year_Month:T',
    y='Mass Shootings:Q',
    color=alt.Color(
        'Value_Category:N',
        scale=alt.Scale(
            domain=['min', 'medium', 'max'],
            range=['darkred', '#D73027', 'darkred']
        ),
        legend=None
    ),
    tooltip=['Mass Shootings']
)

# Combinar la línea y los puntos
evolution_chart = line_chart + points

highlight_points = alt.Chart(monthly_counts).mark_point(filled=True).encode(
    x='Year_Month:T',
    y='Mass Shootings:Q',
    size=alt.Size(
        'Value_Category:N',
        scale=alt.Scale(
            domain=['min', 'max'],
            range=[200, 200]
        ),
        legend=None
    ),
    color=alt.Color(
        'Value_Category:N',
        scale=alt.Scale(
            domain=['min', 'max'],
            range=['red', 'red']
        ),
        legend=None
    ),
    tooltip=[
        alt.Tooltip('Year_Month:T', title='Month'),
        alt.Tooltip('Mass Shootings:Q', title='Shootings'),
        alt.Tooltip('Value_Category:N', title='Category')
    ]
)

text_labels = monthly_counts[monthly_counts['Value_Category'].isin(['min', 'max'])]

max_min_text = alt.Chart(text_labels).mark_text(
    align='center',
    dy=-20,
    fontSize=12,
    color='red'
).encode(
    x='Year_Month:T',
    y='Mass Shootings:Q',
    text='Value_Category:N'
)

# Add a mean line at the average number of mass shootings
mean_line = alt.Chart(pd.DataFrame({'y': [mean_shootings]})).mark_rule(color='#D73027', size=2).encode(
    y='y:Q'
)

mean_text = alt.Chart(pd.DataFrame({'y': [mean_shootings], 'text': [f'Mean: {mean_shootings:.2f}']})).mark_text(
    align='left',
    dx=25,
    dy=-10,
    fontSize=12,
    color='#D73027'
).encode(
    y='y:Q',
    text='text:N'
)

year_starts = monthly_counts[monthly_counts['Year_Month'].str.endswith('01')].copy()
year_starts['x'] = year_starts['Year_Month']

# Create vertical lines at the start of each year
discontinuity_lines = alt.Chart(year_starts).mark_rule(color='gray', strokeDash=[5, 5]).encode(
    x='x:T',
    size=alt.value(2)
)

Q4 = evolution_chart + highlight_points + max_min_text + mean_line + mean_text + discontinuity_lines

##########################

col5, col6 = st.columns(2)

## CODE PREPARATION ##
# Group by year and calculate the total suspects killed and injured
df = pd.read_csv('Q2_dataset.csv')

by_year = df.groupby('Incident Year').agg(
    total_suspects_killed=('Suspects Killed', 'sum'),
    total_suspects_injured=('Suspects Injured', 'sum')
).reset_index()

# Reshape the data for plotting
by_year_long = by_year.melt(
    id_vars=['Incident Year'],
    value_vars=['total_suspects_killed', 'total_suspects_injured'],
    var_name='Category',
    value_name='Count'
)

## FINAL VISUALIZATION ##
# Create a grouped bar chart with closer spacing
additional_chart = alt.Chart(by_year_long).mark_bar(size=30).encode(
    x=alt.X('Incident Year:O', title='Year'),  # Grouped by year
    xOffset=alt.XOffset('Category:N'),  # Offset within each year for categories
    y=alt.Y('Count:Q', title='Number of Suspects'),  # Total counts
    color=alt.Color(
        'Category:N',
        title='Category',
        scale=alt.Scale(
            domain=['total_suspects_killed', 'total_suspects_injured'],
            range=['#D73027', '#ff9999']  # Two shades of red
        ),
        legend = alt.Legend(
            labelFontSize=10,
            symbolSize=10
        )
    ),
    tooltip=[
        alt.Tooltip('Incident Year:O', title='Year'),
        alt.Tooltip('Count:Q', title='Count'),
        alt.Tooltip('Category:N', title='Category')
    ]
).configure_axis(
    grid=False
).properties(
    title='Total Suspects Killed and Injured by Year',
    width=500,
    height=300
)

with col5:
    st.altair_chart(Q4, use_container_width=True)

with col6:
    st.altair_chart(additional_chart, use_container_width=True)