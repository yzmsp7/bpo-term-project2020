from Simulation import Simulation
import dash
import dash_table
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots


DEFUALT_LAMBDA = 50
DEFUALT_MU = 30
DEFUALT_SERVER = 2

sim = Simulation(DEFUALT_LAMBDA, DEFUALT_MU, DEFUALT_SERVER)
sim.run_sim()

app = dash.Dash(__name__)

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
    waiting = sim.get_wating()

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
    [Output("table", "data"), Output('table', 'columns')],
    [Input("arrival_rate", "value"), Input("service_rate", "value"), Input("servers", "value")]
)
def update_table(ar, sr, s):
    sim = Simulation(ar, sr, s)
    sim.run_sim()
    df = pd.DataFrame(sim.get_records())

    columns = [{"name": i, "id": i} for i in df.columns]
    data = df.to_dict('records')

    return data, columns


if __name__ == '__main__':
    # simulation

    df = pd.DataFrame(sim.get_records())

    # dash
    app.layout = html.Div(
        [
            html.H1('Share Tea Simulation'),
            html.Div(
                [
                    html.Span(
                        "Arrival Rate(λ):",
                    ),
                    dcc.Input(id="arrival_rate", type="number", value=DEFUALT_LAMBDA, debounce=True, placeholder="Arrival Rate(λ)",
                              min=1, max=100),
                    html.Span(
                        "Service Rate(μ): ",
                    ),
                    dcc.Input(
                        id="service_rate", type="number", value=DEFUALT_MU, debounce=True, placeholder="Service Rate(μ)",
                    ),
                    html.Span(
                        "Servers Numbers: ",
                    ),
                    dcc.Input(
                        id="servers", type="number", value=DEFUALT_SERVER, debounce=True, placeholder="Servers",
                    ),
                    html.Button(id='submit', type='submit', children='confirm'),
                    html.Hr(),
                ]
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

    app.run_server(debug=True)
