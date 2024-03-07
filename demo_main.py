
# import libraries
import numpy as np
from scipy.optimize import fsolve
import plotly.graph_objects as go


############################################################################
############################################################################
############################################################################

def demo_main(cutting_depth, cutting_width, cutting_speed_area, d_reuse, d_new): # m2/hr, m^2, m, mm

    # @ parameters for blades
    # cutting speed of blade
    v_cut_2 = 6 # m2/hr
    # life time of blade
    a_max_cut_blade = 30 # m^2 for 6-8 m2/hr or 15 m^2 for 3-4 m2/hr
    span_blade = a_max_cut_blade/v_cut_2  # = 5hr 
    # diameter of blade
    d_blade = 0.8 # m (600 mm … 1,600 mm)
    # thickness of blade
    t_blade = 2.2/1000 # m
    # weight of blade
    w_blade = np.pi * np.square(d_blade/2) * t_blade * 7800 # kg (steel density 7800 kg/m3)

    # @ parameters for materials 
    # density of materials
    rho_light_reinforced_concrete = 2500
    rho_hard_reinforced_concrete = 2770
    rho_concrete = 2150 # kg/m3 lean concrete
    rho_steel = 7850 # kg/m3

    # @ CO2 emission of materials

    # light_reinforced_concrete_emission = 0.165 # kgCO2eq/kg from KBOB for Switzerland
    # hard_reinforced_concrete_emission = 0.358 # kgCO2eq/kg from KBOB for Switzerland
    # brick_emission = 0.267 
    concrete_emission = 0.0408 # kgCO2eq/kg IPCC2021 EcoInvent 3.10, lean concrete production, with cement CEM II/B | lean concrete | Cutoff, U
    civil_concrete_emission = 0.0903 # kgCO2eq/kg IPCC2021 EcoInvent 3.10, concrete production, 37MPa, for civil engineering, with cement, Portland | concrete, 37MPa | Cutoff, U
    steel_CO2_emission = 2.3173 # kgCO2eq/kg IPCC2021 EcoInvent 3.10, market for reinforcing steel | reinforcing steel | Cutoff, U

    # https://oneclicklca.zendesk.com/hc/en-us/articles/360020943800-Average-Quantities-of-Reinforcement-in-Concrete
    light_reinforce_ratio_beam_v = 0.025 # 2.5% of the volume of concrete
    # translated to mass ratio
    light_reinforce_ratio_beam = light_reinforce_ratio_beam_v*rho_steel/(light_reinforce_ratio_beam_v*rho_steel+(1-light_reinforce_ratio_beam_v)*rho_concrete)
    hard_reinforce_ratio_beam_v = 0.045 # 4.5% of the volume of concrete
    # translated to mass ratio
    hard_reinforce_ratio_beam = hard_reinforce_ratio_beam_v*rho_steel/(hard_reinforce_ratio_beam_v*rho_steel+(1-hard_reinforce_ratio_beam_v)*rho_concrete)
    light_reinforce_ratio_slab_v = 0.009 # 0.9% of the volume of concrete
    # translated to mass ratio
    light_reinforce_ratio_slab = light_reinforce_ratio_slab_v*rho_steel/(light_reinforce_ratio_slab_v*rho_steel+(1-light_reinforce_ratio_slab_v)*rho_concrete)
    hard_reinforce_ratio_slab_v = 0.017 # 1.7% of the volume of concrete
    # translated to mass ratio
    hard_reinforce_ratio_slab = hard_reinforce_ratio_slab_v*rho_steel/(hard_reinforce_ratio_slab_v*rho_steel+(1-hard_reinforce_ratio_slab_v)*rho_concrete)

    rho_light_reinforced_concrete_beam = (1-light_reinforce_ratio_beam)*rho_concrete + light_reinforce_ratio_beam*rho_steel # kg/m3, low strength concrete
    rho_hard_reinforced_concrete_beam = (1-hard_reinforce_ratio_beam)*rho_concrete + hard_reinforce_ratio_beam*rho_steel # kg/m3, high strength concrete
    rho_light_reinforced_concrete_slab = (1-light_reinforce_ratio_slab)*rho_concrete + light_reinforce_ratio_slab*rho_steel # kg/m3, low strength concrete
    rho_hard_reinforced_concrete_slab = (1-hard_reinforce_ratio_slab)*rho_concrete + hard_reinforce_ratio_slab*rho_steel # kg/m3, high strength concrete

    light_reinforced_concrete_emission_beam = (1-light_reinforce_ratio_beam)*concrete_emission + light_reinforce_ratio_beam*steel_CO2_emission  # kgCO2eq/kg, low strength concrete
    hard_reinforced_concrete_emission_beam = (1-hard_reinforce_ratio_beam)*civil_concrete_emission + hard_reinforce_ratio_beam*steel_CO2_emission # kgCO2eq/kg, high strength concrete
    light_reinforced_concrete_emission_slab = (1-light_reinforce_ratio_slab)*concrete_emission + light_reinforce_ratio_slab*steel_CO2_emission  # kgCO2eq/kg, low strength concrete
    hard_reinforced_concrete_emission_slab = (1-hard_reinforce_ratio_slab)*civil_concrete_emission + hard_reinforce_ratio_slab*steel_CO2_emission # kgCO2eq/kg, high strength concrete


    green_electricity_CO2_emission = 0.0023 # kgCO2eq/kWh IPCC2021 EcoInvent 3.10, market for electricity, medium voltage | electricity, medium voltage | Cutoff, U CH
    gray_electricity_CO2_emission = 0.9230 # kgCO2eq/kWh IPCC2021 EcoInvent 3.10, market for electricity, medium voltage | electricity, medium voltage | Cutoff, U CN
    generator_CO2_emission = 76.4400 # kgCO2eq/hour IPCC2021 EcoInvent 3.10, machine operation, diesel, >= 74.57 kW, generators | machine operation, diesel, >= 74.57 kW, generators | Cutoff, U

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

    # @ dimensional parameters for a concrete beam/wall
    cutting_width = beam_width = 0.4 # meters
    cutting_depth = beam_depth = 0.4

    # @ transportation parameters
    distance_factory_b = 100 # km
    # the reuse distance is a times the distance from factory to site
    a = 1 
    distance_a_storage_b_total = a * distance_factory_b # km
    # carbon emission of different transportation methods
    # lorry_CO2_emission = 0.144 # kgCO2eq/tonkm
    # truck_CO2_emission = 0.183 # kgCO2eq/tonkm, 16-32 ton truck, assuming 8m|3 of concrete of 32 ton
    lorry_CO2_emission = truck_CO2_emission = 0.15221 ## kgCO2eq/tonkm EURO6, IPCC2021 EcoInvent 3.10, , transport, freight, lorry, all sizes, EURO3 to generic market for transport, freight, lorry, unspecified | transport, freight, lorry, unspecified | Cutoff, U
    # 0.1577 # kgCO2eq/tonkm EURO3, IPCC2021 EcoInvent 3.10, , transport, freight, lorry, all sizes, EURO3 to generic market for transport, freight, lorry, unspecified | transport, freight, lorry, unspecified | Cutoff, U
    # load capacity of lorry or concrete truck
    size_truck = 9 # m3
    weight_concrete_truck = size_truck * rho_concrete # 19.35 ton
    lorry_load_capacity = 12e3 # ton
    lorry_space_capacity = 9
    # Additional information:
    # max cutting depth 73 cm
    # guide cut at half power consumption at 4cm depth

    # assume cutting concrete has 2% loss
    glue_roundup_ratio =0.02
    
    # calculate the maximum number of concrete beam to be transported for reuse
    def max_concrete_beam(cutting_length,cutting_depth, cutting_width,rho):
        v_concrete_beam = cutting_length * cutting_depth*cutting_width
        weight_concrete_beam = v_concrete_beam * rho
        max_num_concrete_beam = np.minimum(np.floor(lorry_space_capacity / v_concrete_beam),np.floor(lorry_load_capacity / weight_concrete_beam))
        return max_num_concrete_beam

    # calculate the maximum number of concrete beam to be transported for reuse
    def max_concrete_wall(cut_width,cut_height,wall_thickness,rho):
        v_concrete_wall = cut_width * cut_height * wall_thickness
        weight_concrete_wall = v_concrete_wall * rho
        max_num_concrete_wall = np.minimum(np.floor(lorry_space_capacity / v_concrete_wall),np.floor(lorry_load_capacity / weight_concrete_wall))
        return max_num_concrete_wall

    # calculate the total weight of concrete beam to be transported for reuse
    def total_weight_concrete_beam(cutting_length,cutting_depth, cutting_width, rho):
        v_concrete_beam = cutting_length *cutting_depth* cutting_width
        weight_concrete_beam = v_concrete_beam * rho
        max_num_concrete_beam = np.minimum(np.floor(lorry_space_capacity / v_concrete_beam),np.floor(lorry_load_capacity / weight_concrete_beam)) #7
        total_weight_concrete_beam = max_num_concrete_beam * weight_concrete_beam
        return total_weight_concrete_beam

    # calculate the carbon emission for manufacturing the concrete beam
    def manufacturing_cost_beam(carbon_emission, cutting_length, cutting_depth, cutting_width, rho):
        beam_volumne = cutting_length * cutting_depth* cutting_width
        manufacturing_CO2_cost = carbon_emission * beam_volumne * rho
        return manufacturing_CO2_cost

    # calculate the carbon emission for manufacturing the concrete wall
    def manufacturing_cost_wall(carbon_emission, wall_thickness, wall_width, wall_height, rho):
        wall_volume = wall_thickness * wall_width * wall_height
        manufacturing_CO2_cost = carbon_emission * wall_volume * rho
        return manufacturing_CO2_cost

    # calculate the carbon emission for cutting the concrete beam, generator
    def cut_impact(cutting_time):
        # impact_energy = (power * cutting_time) * (electricity_CO2_emission) # impact of electricity consumption 
        impact_energy = (cutting_time) * (generator_CO2_emission) # impact of generator consumption 
        impact_blade = diamond_blade_CO2_emission * cutting_time
        impact_machine = cutting_time / span_machine * steel_CO2_emission * w_machine
        cut_impact = impact_energy + impact_blade + impact_machine
        return cut_impact

    def reuse_glue_cost(weight,glue_roundup_ratio, carbon_emission):
        glue_cost = weight * glue_roundup_ratio * carbon_emission
        return glue_cost

    # calculate the carbon emission for cutting the concrete beam
    def cut_impact_electricity(electricity_CO2_emission, cutting_time):
        impact_energy = (power * cutting_time) * (electricity_CO2_emission) # impact of electricity consumption 
        # impact_energy = (cutting_time) * (generator_CO2_emission) # impact of generator consumption 
        impact_blade = diamond_blade_CO2_emission * cutting_time
        impact_machine = cutting_time / span_machine * steel_CO2_emission * w_machine
        cut_impact = impact_energy + impact_blade + impact_machine
        return cut_impact

    # calculate the cutting time for the concrete beam
    def cutting_time_beam(cutting_depth,cutting_width,cut_speed_area):
        cutting_pass = np.ceil(cutting_depth/0.12) * 2 # back and forth cut @12cm depth
        cutting_time_speed = 2 * (cutting_width /cutting_speed * cutting_pass + cutting_width/(cutting_speed/2))/60 # hours # two cuts
        cutting_time_area = 2 * ( cutting_width * cutting_depth/ cut_speed_area + cutting_width/(cutting_speed/2)/60)
        return max(cutting_time_speed, cutting_time_area)
        # return cutting_time_area

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
        # return cutting_time_area

    # calculate the carbon emission for transportation of reused concrete beam
    def transport_impact_lorry(total_weight_concrete_beam,distance): # assume fully loaded lorry
        transport_impact_lorry = distance * total_weight_concrete_beam/1000 * lorry_CO2_emission
        return transport_impact_lorry

    # calculate the carbon emission for transportation of new concrete
    def transport_impact_truck(distance,weight_concrete_truck):
        transport_impact_truck = distance * weight_concrete_truck/1000 * truck_CO2_emission 
        # transport_impact_truck = concrete_truck_transport * truck_CO2_emission
        return transport_impact_truck
  
    # @ start the calculation
    # Define the range of size
    cutting_length_range = np.linspace(0.01, 8, 100)  # Example range for cutting length
    # Initialize arrays to store the reuse impact and new impact values
    difference_values = []
    # Calculate reuse impact and new impact for each cutting length
    for cutting_length in cutting_length_range:
        # Calculate cutting time and other necessary parameters
        cutting_time = cutting_time_beam(cutting_depth, cutting_width, cutting_speed_area)
        max_num_concrete_beam = max_concrete_beam(cutting_length,cutting_depth, cutting_width,rho_light_reinforced_concrete_beam)
        total_weight_beam = total_weight_concrete_beam(cutting_length,cutting_depth, cutting_width, rho_light_reinforced_concrete_beam)
        # print(max_num_concrete_beam,total_weight_beam)
        
        # Calculate reuse impact and new impact
        reuse_impact =  transport_impact_lorry(total_weight_beam, d_reuse)\
                        + cut_impact(cutting_time) * max_num_concrete_beam\
                            + reuse_glue_cost(total_weight_beam, glue_roundup_ratio, light_reinforced_concrete_emission_beam)         
        new_impact = manufacturing_cost_beam(light_reinforced_concrete_emission_beam, cutting_length,cutting_depth, cutting_width, rho_light_reinforced_concrete) * max_num_concrete_beam\
                    + transport_impact_truck(d_new, total_weight_beam)
        difference = reuse_impact - new_impact
        
        # Store the impact values
        difference_values.append(difference)
        
    # Find the intersection point with tolerance
    tolerance = 1e-5
    intersection_func = lambda x: np.interp(x, cutting_length_range, difference_values)
    intersection, = fsolve(intersection_func, cutting_length_range[0], xtol=tolerance)
    print(intersection)
    # round to 2 decimal places
    intersection = round(intersection,2)
    
    # Create a line plot using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cutting_length_range, y=difference_values, name='Impact Difference'))    
    # fig.add_trace(go.Scatter(x=cutting_length_range, y=new_impact_values, name='New Impact'))

    # Add marker for the intersection point
    fig.add_trace(go.Scatter(x=[intersection], y=[np.interp(intersection, cutting_length_range, difference_values)],
                            mode='markers', name='Intersection Point'))

    # Set plot layout
    fig.update_layout(
        xaxis_title='Cutting Length in m',
        yaxis_title='Impact in kg CO2eq',
        title='Environmental Impact vs. Cutting Length',
        autosize=False,
        width=800,
        height=600,
        margin=dict(l=65, r=50, b=65, t=90),
        # yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black'),  # Emphasize y = 0 line
    )

    # Update layout to hide default x-axis line and emphasize y=0 line
    fig.update_layout(
        xaxis=dict(
            showline=False,  # Hide the default x-axis line
            showticklabels=True,  # Show tick labels on the x-axis
            ticks='',  # Hide ticks along the x-axis
            zeroline=True,  # Ensure the zero line is shown
            zerolinewidth=2,  # Adjust the width of the zero line if you want it more visible
            zerolinecolor='black'  # Set the color of the zero line
        ),
        yaxis=dict(
            zeroline=True,  # Show the zero line for y-axis
            zerolinewidth=2,  # Adjust the width of the zero line
            zerolinecolor='black'  # Set the color of the zero line
        )
    )
    fig.update_xaxes(range=[0, 6])  # Set x-axis limits
    fig.update_yaxes(range=[-2000, 3000])  # Set y-axis limits
    fig.update_layout(template="simple_white")

    # return fig
    return {"plot": fig, "intersection_point": intersection}


# if __name__ == "__main__":
#     demo_main(0.4,0.4,6,100,100)
# change beam or slab
# change energy used and consumption emission
# change rebar ratio