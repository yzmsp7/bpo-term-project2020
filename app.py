from Simulation import Simulation
import dash
import dash_table
import pandas as pd


app = dash.Dash(__name__)

if __name__ == '__main__':

    sim = Simulation(50, 30, 2)
    sim.run_sim()
    df = pd.DataFrame(sim.get_records())

    app.layout = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
    )

    app.run_server(debug=True)
