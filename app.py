from Simulation import Simulation
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

DEFUALT_LAMBDA = 50
DEFUALT_MU = 30
DEFUALT_SERVER = 2

sim = Simulation(DEFUALT_LAMBDA, DEFUALT_MU, DEFUALT_SERVER)
sim.run_sim()
df = pd.DataFrame(sim.get_records())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# dash

NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(
                        dbc.NavbarBrand("Group 8 Assignment3: Share Tea Simulation", className="ml-2")
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://github.com/yzmsp7/bpo-term-project2020",
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

app.layout = html.Div(
    [
        NAVBAR,
        dbc.Container(
            [
                html.Span(
                    "Arrival Rate(λ) /min:",
                ),
                dcc.Input(id="arrival_rate", type="number", value=DEFUALT_LAMBDA, debounce=True,
                          placeholder="Arrival Rate(λ)", min=0.01, max=100),
                html.Span(
                    "Service Rate(μ) /min: ",
                ),
                dcc.Input(
                    id="service_rate", type="number", value=DEFUALT_MU, debounce=True,
                    placeholder="Service Rate(μ)",
                ),
                html.Span(
                    "Servers Numbers: ",
                ),
                dcc.Input(
                    id="servers", type="number", value=DEFUALT_SERVER, debounce=True, placeholder="Servers",
                ),
                html.Button(id='submit', type='submit', children='confirm'),
                html.Hr(),
                html.Div(id="average-output"),
            ],
            style={"marginTop": 30}
        ),
        html.H2('Waiting Time Line Plot'),
        html.Div(
            [
                dcc.Graph(id='live-update-graph', animate=True),
                # dcc.Interval(
                #     id='interval-component',
                #     interval=1 * 1000,
                #     n_intervals=0
                # ),
            ]
        ),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
        ),
    ]
)


# Multiple components can update everytime interval gets fired.
@app.callback(
    Output('live-update-graph', 'figure'),
    [Input("arrival_rate", "value"), Input("service_rate", "value"), Input("servers", "value")]
)
def update_graph_live(ar, sr, s):
    data = {
        'time': [],
        'value': [],
    }
    sim = Simulation(ar, sr, s)
    sim.run_sim()
    waiting = sim.get_waiting()

    # Collect some data
    for i in range(len(waiting)):
        data['value'].append(waiting[i])
        data['time'].append(i)

    fig = make_subplots(rows=1, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['value'],
        'name': 'waiting time',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig


@app.callback(
    [Output("table", "data"), Output('table', 'columns'), Output("average-output", "children")],
    [Input("arrival_rate", "value"), Input("service_rate", "value"), Input("servers", "value")]
)
def update_table(ar, sr, s):
    sim = Simulation(ar, sr, s)
    sim.run_sim()
    df = pd.DataFrame(sim.get_records())
    df = df.sort_values(by='customer')
    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')
    avg_wait = np.around(df.waiting_time.mean(), 3)
    avg_sys = np.around(df.system_time.mean(), 3)

    return data, columns, "average waiting time: {}(s); average system time: {}(s)".format(avg_wait, avg_sys)


if __name__ == '__main__':
    app.run_server(debug=True)
