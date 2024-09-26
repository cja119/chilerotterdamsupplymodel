from pyomo.environ import Set, Param
from numpy import ones, mean
from math import floor
from csv import DictReader
from os import path

def extract_values(dictionary, index):
    extracted_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            extracted_dict[key] = extract_values(value, index)
        elif isinstance(value, (tuple, list)):
            extracted_dict[key] = value[index] if index < len(value) else None
        elif isinstance(value, (int, float)):
            extracted_dict[key] = value
        else:
            raise ValueError("Values should be tuples, lists, integers, or floats")
    return extracted_dict

def grab_from_store(title,folder='PreOptimisationDataStore'):
    data = {}
    csv_file = path.join(folder, title)

    # Open and read the CSV file
    with open(csv_file, 'r') as file:
        reader = DictReader(file)
        for row in reader:
            key = int(row['Key'])
            try:
                value = float(row['Value'])
            except:
                value = row['Value']
            data[key] = value
    return data

def generate_parameters(self,parameters):

    parameters = extract_values(parameters,1)
    wind_power = grab_from_store('wind_speed.csv')
    time_durations  = grab_from_store('time_duration.csv')
    time_values     = grab_from_store('time_data.csv')
    demand_signal   = grab_from_store('demand_signal.csv')


    # First generating the necessary sets using comprehension of the parameter dictionary. 
    self.model.vectors          = Set(initialize=[key for key, value in parameters['booleans']['vector_choice'].items() if value])
    self.model.ships            = Set(initialize=[key for key, value in parameters['booleans']['ship_sizes'].items() if value])
    self.model.electrolysers    = Set(initialize=[key for key,value in parameters['booleans']['electrolysers'].items() if value])
    self.model.time             = Set(initialize=range(len(time_durations)))
    self.model.shipping_time    = Set(initialize=list(range(int(list(time_values.values())[-1]/parameters['shipping_regularity'])+1)))
    
    # Passing the boolean values to the model
    self.model.grid_connection  = Param(initialize = parameters['booleans']['grid_connection'])
    self.model.fuel_cell        = Param(initialize = parameters['booleans']['fuel_cell'])
    self.model.battery          = Param(initialize = parameters['booleans']['battery_storage'])
    self.model.reconversion     = Param(initialize = parameters['booleans']['reconversion'])
    self.model.relaxed_ramping  = Param(initialize = parameters['booleans']['relaxed_ramping'])
    
    for key,value in parameters['booleans']['vector_choice'].items():
        setattr(self.model, key, Param(initialize = value))
        param = getattr(self.model,key)
        param.construct()
    
    # Constructing the sets, such that they can be used to index parameters.
    self.model.vectors.construct()
    self.model.ships.construct()
    self.model.electrolysers.construct()
    self.model.time.construct()
    self.model.grid_connection.construct()
    self.model.fuel_cell.construct()
    self.model.battery.construct()
    self.model.reconversion.construct()

    self.model.end_time = Param(initialize = list(time_values.values())[-1])
    self.model.end_time_index = Param(initialize=len(time_durations)-1)

    # Generating energy related parameters.
    self.model.time_duration                = Param(self.model.time,initialize = time_durations)
    self.model.time_values                  = Param(self.model.time, initialize = time_values)
    self.model.turbine_power                = Param(self.model.time, initialize = wind_power)
    self.model.turbine_unit_capital_cost    = Param(initialize = parameters['capital_costs']['turbine'])
    self.model.turbine_unit_operating_cost  = Param(initialize = parameters['operating_costs']['turbine'])
    self.model.turbine_efficiency           = Param(initialize = parameters['efficiencies']['turbine'])
    self.model.demand_signal                = Param(self.model.time, initialize = demand_signal)
    self.model.compressor_unit_capital_cost     = Param(initialize = parameters['capital_costs']['compressor'])
    self.model.compressor_unit_operating_cost   = Param(initialize = parameters['operating_costs']['compressor'])
    self.model.compressor_effiency              = Param(initialize = parameters['efficiencies']['compressor'])
    self.model.electrolyser_compression_energy  = Param(self.model.electrolysers, initialize=\
                                                {key: parameters['miscillaneous']['electrolyser_compression_energy'][key] 
                                                    for key, value in parameters['booleans']['electrolysers'].items() if value})
    self.model.storage_compression_penalty      = Param(initialize = parameters['miscillaneous']['storage_compression_penalty'])
    self.model.vector_compression_penalty       = Param(self.model.vectors, initialize=\
                                                {key: parameters['miscillaneous']['vector_compression_penalty'][key] 
                                                    for key, value in parameters['booleans']['vector_choice'].items() if value})


    # Generating HFC related parameters.
    if self.model.fuel_cell.value:
        self.model.fuel_cell_efficiency             = Param(initialize = parameters['efficiencies']['fuel_cell'])
        self.model.fuel_cell_unit_capital_cost      = Param(initialize = parameters['capital_costs']['fuel_cell'])
        self.model.fuel_cell_unit_operating_cost    = Param(initialize = parameters['operating_costs']['fuel_cell'])
        self.model.fuel_cell_lifecycle              = Param(initialize = parameters['replacement_frequencies']['fuel_cell'])

    # Adding the grid connection.
    if self.model.grid_connection:
        self.model.grid_energy_factor               = Param(initialize = parameters['operating_costs']['grid_energy_factor'])
    
    # Adding the battery storage
    if self.model.battery.value:
        self.model.battery_charge_time          = Param(initialize = parameters['miscillaneous']['battery_charge_time'])
        self.model.battery_discharge_time       = Param(initialize = parameters['miscillaneous']['battery_discharge_time'])
        self.model.battery_unit_capital_cost    = Param(initialize = parameters['capital_costs']['battery_storage'])
        self.model.battery_unit_operating_cost  = Param(initialize = parameters['operating_costs']['battery_storage'])
        self.model.battery_efficiency           = Param(initialize = parameters['efficiencies']['battery_storage'])
    
    # Adding electrolyser related parameters
    self.model.electrolyser_efficiency = Param(self.model.electrolysers, initialize=\
                                                {key: parameters['efficiencies']['electrolysers'][key] 
                                                    for key, value in parameters['booleans']['electrolysers'].items() if value})
    self.model.electrolyser_unit_capital_cost       = Param(self.model.electrolysers, initialize=\
                                                {key: parameters['capital_costs']['electrolysers'][key] 
                                                    for key, value in parameters['booleans']['electrolysers'].items() if value})
    self.model.electrolyser_unit_operating_cost     = Param(self.model.electrolysers, initialize=\
                                                {key: parameters['operating_costs']['electrolysers'][key] 
                                                    for key, value in parameters['booleans']['electrolysers'].items() if value})

    # Adding gaseous hydrogen storage related parameters
    self.model.hydrogen_storage_unit_capital_cost   = Param(initialize = parameters['capital_costs']['hydrogen_storage'])
    self.model.hydrogen_storage_unit_operating_cost = Param(initialize = parameters['operating_costs']['hydrogen_storage'])
    self.model.hydrogen_LHV                         = Param(initialize = parameters['miscillaneous']['hydrogen_LHV'])

    # Adding vector related parameters
    
    self.model.single_train_throughput_limit = Param(self.model.vectors, initialize=\
                                                     {key: parameters['vector_production']['single_train_throughput'][key]
                                                      for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.vector_calorific_value= Param(self.model.vectors, initialize=\
                                                {key: parameters['efficiencies']['vector_calorific_value'][key] 
                                                    for key, value in parameters['booleans']['vector_choice'].items() if value})

    self.model.vector_stoichiometry = Param(self.model.vectors, initialize=\
                                                {key: parameters['efficiencies']['vector_stoichiometry'][key] 
                                                    for key, value in parameters['booleans']['vector_choice'].items() if value})
    self.model.minimum_process_throughput = Param(self.model.vectors, initialize=\
                                                {key: parameters['vector_production']['minimum_train_throughput'][key] 
                                                    for key, value in parameters['booleans']['vector_choice'].items() if value})

    self.model.ramp_down_limit = Param(self.model.vectors, initialize=\
                                                {key: parameters['vector_production']['ramp_down_limit'][key] 
                                                    for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.vector_fractional_energy_penalty = Param(self.model.vectors, initialize=\
                                                        {key: parameters['vector_production']['fractional_energy_penalty'][key] 
                                                            for key, value in parameters['booleans']['vector_choice'].items() if value})

    self.model.ramp_up_limit = Param(self.model.vectors, initialize=\
                                                {key: parameters['vector_production']['ramp_up_limit'][key] 
                                                    for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.ramping_frequency = Param(initialize = parameters['ramping_frequency'])

    self.model.vector_production_unit_capital_cost = Param(self.model.vectors, initialize=\
                                                            {key: parameters['capital_costs']['vector_production'][key]*(parameters['vector_production']['single_train_throughput'][key])**(2/3)
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})

    self.model.vector_production_unit_operating_cost = Param(self.model.vectors, initialize=\
                                                            {key: parameters['operating_costs']['vector_production'][key]*(parameters['vector_production']['single_train_throughput'][key])**(2/3)
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.bol_energy_penalty = Param(self.model.vectors, initialize=\
                                                            {key: parameters['vector_production']['boil_off_energy_penalty'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
    self.model.bol_rate = Param(self.model.vectors, initialize=\
                                                            {key: parameters['vector_production']['boil_off_percentage'][key]/100 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})

    self.model.vector_fixed_energy_penalty = Param(self.model.vectors, initialize=\
                                                            {key: parameters['vector_production']['fixed_energy_penalty'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.vector_variable_energy_penalty = Param(self.model.vectors, initialize=\
                                                            {key: parameters['vector_production']['variable_energy_penalty'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.vector_storage_unit_capital_cost = Param(self.model.vectors, initialize=\
                                                            {key: parameters['capital_costs']['vector_storage'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.vector_storage_unit_operating_cost = Param(self.model.vectors, initialize=\
                                                            {key: parameters['operating_costs']['vector_storage'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.vector_fugitive_efficiency = Param(self.model.vectors, initialize=\
                                                            {key: parameters['efficiencies']['vector_fugitive'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
    
    self.model.vector_synthetic_efficiency = Param(self.model.vectors, initialize=\
                                                            {key: parameters['efficiencies']['vector_synthesis'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
    # Adding shipping related parameters
    self.model.port_unit_capital_cost = Param(initialize = parameters['capital_costs']['port'])
    self.model.port_unit_operating_cost = Param(initialize = parameters['operating_costs']['port'])

    self.model.ship_storage_capacity = Param( self.model.ships, self.model.vectors, initialize=\
                                                {(key2,key1): parameters['shipping']['storage_capacity'][key1,key2]
                                                        for key2,value2 in parameters['booleans']['ship_sizes'].items() if value2\
                                                            for key1, value1 in parameters['booleans']['vector_choice'].items() if value1})
    
    self.model.ship_fuel_consumption = Param( self.model.ships, self.model.vectors, initialize=\
                                                {(key2,key1): parameters['shipping']['fuel_consumption'][key1,key2]
                                                        for key2,value2 in parameters['booleans']['ship_sizes'].items() if value2\
                                                            for key1, value1 in parameters['booleans']['vector_choice'].items() if value1})
    
    self.model.ship_unit_capital_cost = Param( self.model.ships, self.model.vectors, initialize=\
                                                {(key2,key1): parameters['capital_costs']['shipping'][key1,key2]
                                                        for key2,value2 in parameters['booleans']['ship_sizes'].items() if value2\
                                                            for key1, value1 in parameters['booleans']['vector_choice'].items() if value1})
    
    self.model.ship_unit_operating_cost = Param(self.model.ships, self.model.vectors, initialize=\
                                                {(key2,key1): parameters['operating_costs']['shipping'][key1,key2]
                                                        for key2,value2 in parameters['booleans']['ship_sizes'].items() if value2\
                                                            for key1, value1 in parameters['booleans']['vector_choice'].items() if value1})

    self.model.journey_time = Param(initialize = parameters['shipping']['journey_time'])

    self.model.loading_time = Param(initialize = parameters['shipping']['loading_time'])
    
    self.model.shipping_decision_granularity = Param(initialize = parameters['shipping_regularity'])

    # Adding cracking related parameters
    if self.model.reconversion.value:
        self.model.reconversion_electrical_demand = Param(self.model.vectors, initialize=\
                                                            {key: parameters['miscillaneous']['reconversion_electrical_demand'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
        self.model.reconversion_efficiency = Param(self.model.vectors, initialize=\
                                                            {key: parameters['efficiencies']['reconversion'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
        self.model.reconversion_unit_capital_cost = Param(self.model.vectors, initialize=\
                                                            {key: parameters['capital_costs']['reconversion'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})
        self.model.reconversion_unit_operating_cost = Param(self.model.vectors, initialize=\
                                                            {key: parameters['operating_costs']['reconversion'][key] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})

    self.destination_storage_requirement = Param(initialize = 3*24*mean([*demand_signal.values()]))

    # Adding the amortisation factor for the OPEX and adding the net annual demand function (kg(H2)) these are used in calculation of the LCOH
    equipment_lives = ones(parameters['replacement_frequencies']['system_duration']+20)

    # This calculates the amortised cost of having to replace equipment during the lifetime of the plant i is equpment replacement age, j is the year of operation
    for i in range(1,parameters['replacement_frequencies']['system_duration']):
        for j in range(1,parameters['replacement_frequencies']['system_duration']):
            if j % i == 0:
                equipment_lives[i-1] += (1 / (1 + parameters['miscillaneous']['discount_factor'])) ** (j - 1)
                
    # Adding the discounted hydrogen demand

    self.model.discounted_demand = Param(initialize = (8760/int(list(time_values.values())[-1])) * equipment_lives[0]*sum([time_durations[key] * demand_signal[key] for key in self.model.time]) / 0.12)

    # Adding the amortised costs for each piece of equpment to the model
    self.model.amortisation_turbine = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['turbine']-1)])

    if self.model.fuel_cell.value:
        self.model.amortisation_fuel_cell = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['fuel_cell']-1)])
    
    self.model.amortisation_battery = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['battery_storage']-1)])

    self.model.amortisation_hydrogen_storage = Param(initialize=equipment_lives[floor(parameters['replacement_frequencies']['hydrogen_storage']-1)])   

    self.model.amortisation_vector_production = Param(self.model.vectors, initialize=\
                                                            {key: equipment_lives[floor(parameters['replacement_frequencies']['vector_production'][key]-1)] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})

    self.model.amortisation_electrolysers = Param(self.model.electrolysers, initialize=\
                                                            {key: equipment_lives[floor(parameters['replacement_frequencies']['electrolysers'][key]-1)] 
                                                                for key, value in parameters['booleans']['electrolysers'].items() if value})
    

    self.model.amortisation_ships = Param(self.model.ships, initialize=\
                                                            {key: equipment_lives[floor(parameters['replacement_frequencies']['ships'][key]-1)] 
                                                                for key, value in parameters['booleans']['ship_sizes'].items() if value})
    
    if self.model.reconversion.value:
        self.model.amortisation_reconversion = Param(self.model.vectors, initialize=\
                                                            {key: equipment_lives[floor(parameters['replacement_frequencies']['reconversion'][key]-1)] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value})    
    
    self.model.amortisation_vector_storage = Param(self.model.vectors, initialize=\
                                                            {key: equipment_lives[floor(parameters['replacement_frequencies']['vector_storage'][key]-1)] 
                                                                for key, value in parameters['booleans']['vector_choice'].items() if value}) 
    self.model.amortisation_compressor = Param(initialize = equipment_lives[floor(parameters['replacement_frequencies']['compressor']-1)])

    self.model.amortisation_plant = Param(initialize=equipment_lives[0])
    self.model.LCOWP = Param(initialize = (1000*(parameters['capital_costs']['turbine']*equipment_lives[parameters['replacement_frequencies']['turbine']-1]+(parameters['operating_costs']['turbine']*equipment_lives[0]))\
                                           /((8760*parameters['efficiencies']['turbine']* equipment_lives[0]/int(list(time_values.values())[-1]))*sum([time_durations[t] * wind_power[t] for t in self.model.time]))))
    pass


 