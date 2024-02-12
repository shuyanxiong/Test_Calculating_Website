
# import libraries
import numpy as np
from scipy.optimize import fsolve
import plotly.graph_objects as go


############################################################################
############################################################################
############################################################################

def demo_main(v_cut_2, a_max_cut_blade, d_blade, t_blade): # m2/hr, m^2, m, mm
    # User input for blade parameters
    span_blade = a_max_cut_blade / v_cut_2
    w_blade = np.pi * np.square(d_blade/2) * t_blade * 7.8 # kg (steel density 7800 kg/m3)

    # @ parameters for materials 
    # density of materials
    rho_light_reinforced_concrete = 2500
    rho_hard_reinforced_concrete = 2770
    rho_brick =900
    rho_concrete = 2150 # kg/m3 lean concrete

    # @ CO2 emission of materials
    light_reinforced_concrete_emission = 0.204 # kgCO2eq/kg from KBOB for Switzerland
    hard_reinforced_concrete_emission = 0.358 # kgCO2eq/kg from KBOB for Switzerland
    brick_emission = 0.267 # kgCO2eq/kg from KBOB for Switzerland
    concrete_emission = 0.063 # kgCO2eq/kg from KBOB for Switzerland
    steel_CO2_emission = 2.79 # kgCO2eq/kg from KBOB 06.010 Sheet steel, blank, hot rolled, uncoated, thickness 3 mm
    electricity_CO2_emission = 0.01057 # 0.01057285 # kgCO2eq/kWh from KBOB for Switzerland
    generator_CO2_emission = 69.97803127071934 # kgCO2eq/kW from Ecoinvent
    diamond_blade_CO2_emission = (334.123*80/35)/span_blade # kgCO2/h # reference: https://ieeexplore.ieee.org/document/10021341

    # @ wall saw parameters
    # power = 20 # kW, Hilti wall saw DST 20-CA 
    power = 32 # kW, Hilti wall saw DST 20-CA (or 40kVA generator using diesel fuel which is around 32kW)
    span_machine = 1000 # hr
    w_machine = 32 # kg

    # @ parameters for cutting
    fast_cut_speed_area = 6 # m2/hour
    slow_cut_speed_area = 3 # m2/hour
    cutting_speed = 2-(2-0.7)/(15-5)*(12-5) # 1.08m/min @ 12cm depth

    # @ dimensional parameters for a concrete beam
    cutting_length = beam_width = 0.4 # meters
    cutting_depth = beam_depth = 0.4
    beam_length = 4  # meters

    # @ transportation parameters
    distance_factory_b = 100 # km
    # the reuse distance is a times the distance from factory to site
    a = 1 
    distance_a_storage_b_total = a * distance_factory_b # km
    # carbon emission of different transportation methods
    lorry_CO2_emission = 0.144 # kgCO2eq/tonkm
    truck_CO2_emission = 0.183 # kgCO2eq/tonkm, 16-32 ton truck, assuming 8m|3 of concrete of 32 ton
    # load capacity of lorry or concrete truck
    size_truck = 9 # m3
    weight_concrete_truck = size_truck * rho_concrete # 19.35 ton
    lorry_load_capacity = 12e3 # ton
    lorry_space_capacity = 9
    # Additional information:
    # max cutting depth 73 cm
    # guide cut at half power consumption at 4cm depth

    # calculate the maximum number of concrete beam to be transported for reuse
    def max_concrete_beam(v_concrete_beam,rho):
        # cutting_length = v_concrete_beam / (beam_width * beam_depth)
        weight_concrete_beam = v_concrete_beam * rho
        max_num_concrete_beam = np.minimum(np.floor(lorry_space_capacity / v_concrete_beam),np.floor(lorry_load_capacity / weight_concrete_beam))
        return max_num_concrete_beam

    # calculate the total weight of concrete beam to be transported for reuse
    def total_weight_concrete_beam(v_concrete_beam, rho):
        # v_concrete_beam = cutting_length * beam_width * beam_depth
        weight_concrete_beam = v_concrete_beam * rho
        max_num_concrete_beam = np.minimum(np.floor(lorry_space_capacity / v_concrete_beam),np.floor(lorry_load_capacity / weight_concrete_beam)) #7
        total_weight_concrete_beam = max_num_concrete_beam * weight_concrete_beam
        return total_weight_concrete_beam

    # calculate the carbon emission for manufacturing the concrete beam
    def manufacturing_cost_beam(carbon_emission, v_concrete_beam, rho):
        weight_concrete_beam = v_concrete_beam * rho
        manufacturing_CO2_cost = carbon_emission * weight_concrete_beam
        return manufacturing_CO2_cost

    # calculate the carbon emission for manufacturing the concrete wall
    def manufacturing_cost_wall(carbon_emission, wall_volume, rho):
        # wall_volume = wall_thickness * wall_width * wall_height
        manufacturing_CO2_cost = carbon_emission * wall_volume * rho
        return manufacturing_CO2_cost

    # calculate the carbon emission for cutting the concrete beam
    def cut_impact(electricity_CO2_emission, cutting_time):
        # impact_energy = (power * cutting_time) * (electricity_CO2_emission) # impact of electricity consumption 
        impact_energy = (cutting_time) * (generator_CO2_emission) # impact of generator consumption 
        impact_blade = diamond_blade_CO2_emission * cutting_time
        impact_machine = cutting_time / span_machine * steel_CO2_emission * w_machine
        cut_impact = impact_energy + impact_blade + impact_machine
        return cut_impact

    # calculate the cutting time for the concrete beam
    def cutting_time_beam(cutting_depth, cut_speed_area):
        cutting_pass = np.ceil(cutting_depth/0.12) * 2 # back and forth cut @12cm depth
        cutting_time_speed = 2 * (cutting_length /cutting_speed * cutting_pass + cutting_length/(cutting_speed/2))/60 # hours # two cuts
        cutting_time_area = 2 * ( cutting_length * cutting_depth/ cut_speed_area  + cutting_length/(cutting_speed/2)/60)
        return max(cutting_time_speed, cutting_time_area)

    # calculate the cutting time for the concrete wall
    def cutting_time_wall(wall_width, wall_height, wall_thickness, cut_speed_area):
        cutting_length = 2*(wall_width+wall_height)
        cutting_depth = wall_thickness
        # number of passes
        cutting_pass = np.ceil(cutting_depth/0.12) * 2 # back and forth cut @12cm depth
        # cutting time depending on speed or area
        cutting_time_speed = (cutting_length /cutting_speed * cutting_pass + cutting_length/(cutting_speed/2))/60 # hours 
        cutting_time_area = ( cutting_length * cutting_depth/ cut_speed_area  + cutting_length/(cutting_speed/2)/60)  
        return max(cutting_time_speed, cutting_time_area)

    # calculate the carbon emission for transportation of reused concrete beam
    def transport_impact_lorry(total_weight_concrete_beam,distance_a_storage_b_total): # assume fully loaded lorry
        transport_impact_lorry = distance_a_storage_b_total * total_weight_concrete_beam/1000 * lorry_CO2_emission
        return transport_impact_lorry

    # calculate the carbon emission for transportation of new concrete
    def transport_impact_truck(distance_factory_b, weight_concrete_truck):
        transport_impact_truck = distance_factory_b * weight_concrete_truck/1000 * truck_CO2_emission 
        # transport_impact_truck = concrete_truck_transport * truck_CO2_emission
        return transport_impact_truck

    # Define the range of size
    v_concrete_beam_range = np.linspace(0.1*beam_depth*beam_width, 10*beam_depth*beam_width, 100)  # Example range for cutting length

    # Initialize arrays to store the reuse impact and new impact values
    reuse_impact_values = []
    new_impact_values = []

    # Set constant transportation distances
    transportation_distance = 20 # km, assumed constant distance from factory to site

    # Define the range of transportation distances, cutting length, and 'a' values
    transportation_distance_range = np.linspace(10, 200, 50)
    v_concrete_beam_range = np.linspace(0.5*beam_depth*beam_width, 10*beam_depth*beam_width, 100)
    a_values = np.linspace(0.5, 10, 50)

    # Initialize a 2D array to store the intersection points for different combinations of 'a' and transportation distance
    intersection_points = np.zeros((len(a_values), len(transportation_distance_range)))

    # Loop through all 'a' values and calculate the intersection points
    for i, a in enumerate(a_values):
        for j, transportation_distance in enumerate(transportation_distance_range):
            # Initialize arrays to store the reuse impact and new impact values for the current 'a' and transportation distance
            reuse_impact_values = []
            new_impact_values = []

            for v_concrete_beam in v_concrete_beam_range:
        
                # Calculate cutting time and other necessary parameters

                cutting_time = cutting_time_beam(cutting_depth, fast_cut_speed_area)
                max_num_concrete_beam = max_concrete_beam(v_concrete_beam, rho_light_reinforced_concrete)
                total_weight_beam = total_weight_concrete_beam(v_concrete_beam, rho_light_reinforced_concrete)

                # Calculate reuse impact and new impact
                reuse_impact =  cut_impact(electricity_CO2_emission, cutting_time) * max_num_concrete_beam \
                            + transport_impact_lorry(total_weight_beam, a * transportation_distance) 
                new_impact = manufacturing_cost_beam(light_reinforced_concrete_emission, v_concrete_beam, rho_light_reinforced_concrete) * max_num_concrete_beam \
                        + transport_impact_truck(transportation_distance, total_weight_beam) 
                        
                # Store the impact values
                reuse_impact_values.append(reuse_impact)
                new_impact_values.append(new_impact)
                
            # Find the intersection point with tolerance
            tolerance = 1e-5
            intersection_func = lambda x: np.interp(x, v_concrete_beam_range, new_impact_values) - np.interp(x, v_concrete_beam_range, reuse_impact_values)
            intersection, = fsolve(intersection_func, v_concrete_beam_range[0], xtol=tolerance)
            intersection_points[i, j] = intersection

    # Create a 3D surface plot using Plotly
    fig = go.Figure(data=[go.Surface(z=intersection_points, x=a_values, y=transportation_distance_range)])

    # Set plot layout
    fig.update_layout(
        scene=dict(
            xaxis_title='Ratio of Transportation Distances D_reuse/D_new',
            yaxis_title='Transportation Distance in km',
            zaxis_title='Optimal Solution: Concrete Beam Volume in m^3',
        ),
        title='3D Surface Plot: Optimal Solution vs. Ratio and Transportation Distance',
        autosize=False,
        width=600,
        height=400,
        margin=dict(l=65, r=50, b=65, t=90)
    )
    fig.update_layout(template="simple_white")
    return fig

if __name__ == "__main__":
    demo_main(6, 30, 0.8, 2.2)
