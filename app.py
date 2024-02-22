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
    
    try:
        processed_input = [float(user_input.get(f"input{i}", 0)) for i in range(1, 6)]  # Default to 0 if not found
    except ValueError:
        return jsonify({"error": "Invalid input"}), 400  # Bad Request
    # processed_input = [float(user_input[f"input{i}"]) for i in range(1,6)]
    
    response_data = demo_main(*processed_input)
    # plot_json = json.dumps(response_data, cls=plotly.utils.PlotlyJSONEncoder)
    plot_json = json.dumps(response_data["plot"], cls=plotly.utils.PlotlyJSONEncoder)
    # Include intersection points in the response
    return jsonify(plot=plot_json, intersection_point=response_data["intersection_point"].tolist())
    # return jsonify(plot_json)

if __name__ == '__main__':
    app.run(debug=True)
