# Import Dependencies
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback

# use pandas to read in data
df = pd.read_csv("gdp_pcap.csv")

# pivot gdp data long so that we can graph it
gdp_long = df.melt(id_vars = 'country', 
                          value_vars = [str(year) for year in range(1800, 2101)], # generate a list of strings for each year from 1800 to 2100
                          var_name = 'year',
                          value_name = 'gdp')

# Define a function that parses through the 'gdp' column to look for values containing the string 'k' and replace
# those strings with an empty space, converting to float, and multiplying by 1000.
# Referenced: https://stackoverflow.com/questions/39684548/convert-the-string-2-90k-to-2900-or-5-2m-to-5200000-in-pandas-dataframe
def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'k' in x:
        if len(x) > 1:
            return float(x.replace('k', '')) * 1000
        return 1000.0
    else:
        return int(x)

gdp_long['gdp'] = gdp_long['gdp'].apply(value_to_float)

stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet

app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app

server = app.server

#Define Layout
app.layout = html.Div([
     html.Div([
        html.H1("GDP Analysis Dashboard"),  # Title
        html.P("This dashboard allows a user to explore the GDP per Capita data of different countries from 1800 to 2100." 
               "The dashboard contains a dropdown and a slider feature that allow a user to select multiple different "
                 "countries (or just one) that they wish the focus on, as well as a range slider for a specific time period with"
                 "which to analyze the selected countries. It is important to note that the data extends past present day,"
                 "these values serve as estimates based on current growth rates."),  # Description
    ]),

    html.Div([],
             style={'height': '20px'}),  # Add space between description and slider/dropdown

    html.Div(dcc.RangeSlider(
        min=int(gdp_long["year"].min()), # selects the minimum year value from the melted dataset
        max=int(gdp_long["year"].max()), # selects the maximum year value from the melted dataset
        step=25, #sets step values of 25 (to fit everything and not look too messy)
        value=[1900,2000],  # Default value range
        marks={year: str(year) for year in list(range(1800, 2101,25))},  # Set marks for slider labels
        id='year-select'
    ), className="six columns"), # takes up half a row


    html.Div(dcc.Dropdown(
            id = 'country-dropdown',
            options = df.country,
            value =  [''], # Default of nothing selected
            multi = True # this makes dropdown multi-select
            ), className="five columns"), # had to make it five instead of six because otherwise the dashboard
                                            # had the dropdown on the next line, not sure why

    html.Div(dcc.Graph(
        id='graph-with-slider-and-dropdown'
    ), className = 'twelve columns' # takes up entire row
    ),
], className = 'row')


# define callbacks
@app.callback(
    Output('graph-with-slider-and-dropdown','figure'),
    Input('country-dropdown','value'),
    Input('year-select','value'))

def update_figure(selected_countries,selected_years):
    filtered_df = gdp_long #this is probably redundant
    
 # Convert 'year' column to integers
    filtered_df['year'] = filtered_df['year'].astype(int)

    # Filter by selected countries
    if selected_countries:
        filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
    
    # Filter by selected years
    if selected_years:
        filtered_df = filtered_df[(filtered_df['year'] >= selected_years[0]) & (filtered_df['year'] <= selected_years[1])]
    
    # Create line chart with filtered data
    fig = px.line(filtered_df, x='year', y='gdp', color='country', title='GDP Per Capita of Selected Countries')
    
    # Update layout
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="GDP Per Capita"
    )
    
    return fig


# run app
if __name__ == '__main__':
    app.run_server(debug=True)
