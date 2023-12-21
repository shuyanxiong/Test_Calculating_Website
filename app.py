from flask import Flask, render_template, request, jsonify
import plotly
import plotly.graph_objs as go
import json
from demo_main import demo_main

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/update_plot', methods=['POST'])
def update_plot():
    # Get user input
    user_input = request.json
    # Process input and update Plotly plot
    print(user_input)
    processed_input = [float(user_input[f"input{i}"]) for i in range(1,5)]
    plot = demo_main(*processed_input)
    plot_json = json.dumps(plot, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(plot_json)

if __name__ == '__main__':
    app.run(debug=True)
