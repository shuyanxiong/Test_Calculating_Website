from flask import Flask, render_template, request, jsonify
import plotly
import plotly.graph_objs as go
import json
# from demo_main import demo_main
from demo_main import demo_main_beam, demo_main_wall  # Assuming separate functions for beam and wall


app = Flask(__name__, template_folder='templates')

from flask import Flask, render_template, request, jsonify
import plotly
import json
from demo_main import demo_main_beam, demo_main_wall

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/update_plot', methods=['POST'])
def update_plot():
    user_input = request.json
    structure_type = user_input.get('structureType')  # Assuming you send this from the front end

    # # Initialize a variable to hold the result from either function
    # result = None

    # Check for structure type and call the respective function with its needed parameters
    if structure_type == 'beam':
        # Assuming demo_main_beam takes parameters like (beam_depth, beam_width, cutting_speed_area, d_reuse, d_new)
        # Extract these parameters from user_input and convert them to the correct types
        beam_depth = float(user_input.get('beamDepth', 0))
        beam_width = float(user_input.get('beamWidth', 0))
        cutting_speed_area = float(user_input.get('cuttingSpeedArea', 0))
        d_reuse = float(user_input.get('dReuse', 0))
        d_new = float(user_input.get('dNew', 0))
        
        result = demo_main_beam(beam_depth, beam_width, cutting_speed_area, d_reuse, d_new)
        plot_json = json.dumps(result["plot"], cls=plotly.utils.PlotlyJSONEncoder)
        return jsonify(plot=plot_json, intersection_point=result["intersection_point"].tolist())
        
    elif structure_type == 'wall':
        # Assuming demo_main_wall takes parameters like (wall_thickness, cut_width, cut_length, cutting_speed_area, d_reuse, d_new)
        # Extract these parameters from user_input and convert them to the correct types
        wall_thickness = float(user_input.get('slabThickness', 0))
        cut_width = float(user_input.get('cutWidth', 0))
        cut_length = float(user_input.get('cutLength', 0))
        cutting_speed_area = float(user_input.get('cuttingSpeedArea', 0))
        d_reuse = float(user_input.get('dReuse', 0))
        d_new = float(user_input.get('dNew', 0))
        
        result = demo_main_wall(wall_thickness, cut_width, cut_length, cutting_speed_area, d_reuse, d_new)
        plot_json = json.dumps(result["plot"], cls=plotly.utils.PlotlyJSONEncoder)
        return jsonify(plot=plot_json, reuse_or_not=result["reuse_or_not"])
    
    else:
        # Handle the case where an invalid structure type is sent
        return jsonify({'error': 'Invalid structure type selected'}), 400

if __name__ == '__main__':
    app.run(debug=True)
