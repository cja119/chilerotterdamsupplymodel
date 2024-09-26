from pyomo.environ import Constraint
def objective_function(self):
    return (10**6)*(self.OPEX+self.CAPEX) / (self.discounted_demand) 

def energy_balance(self,t):
    expr = self.capacity_number_turbines * self.turbine_power[t]* self.turbine_efficiency - self.energy_curtailed[t] - sum(self.energy_electrolysers[k,t] for k in self.electrolysers)\
            - sum(self.energy_penalty_vector_production[q,t] for q in self.vectors) - self.energy_compression[t] - sum(self.vector_storage_origin[q,t]*self.bol_rate[q]*self.bol_energy_penalty[q]*1000 for q in self.vectors)
    if self.grid_connection.value:
        expr += self.energy_grid[t]
    if self.fuel_cell.value:
        expr += self.energy_HFC[t]
    if self.battery.value:
        expr += self.energy_battery_out[t] - self.energy_battery_in[t]
    return expr == 0

def cumulative_grid_use(self):
    return sum(self.time_duration[t] * self.energy_grid[t] for t in self.time) * (8760 / self.end_time) - self.net_grid * 1000 <= 0

def fuel_cell_production_curve(self,t):
    return self.energy_HFC_flux[t] * self.fuel_cell_efficiency - self.energy_HFC[t] == 0

def fuel_cell_capacity(self,t):
    return self.energy_HFC[t] - self.capacity_HFC <= 0

def battery_energy_balance(self,t):
    if self.time_values[t] == 0:
        return self.battery_storage[t] - self.battery_storage[self.end_time_index.value] == 0
    else:
        return self.battery_storage[t] - self.battery_storage[t-1] + self.time_duration[t]*(self.energy_battery_out[t] - self.energy_battery_in[t] * self.battery_efficiency)== 0 

def battery_storage_capacity(self,t):
    return self.battery_storage[t] - self.capacity_battery <= 0

def battery_charging_limit(self,t):
    return self.energy_battery_in[t] - self.capacity_battery / self.battery_charge_time <= 0

def battery_discharging_limit(self,t):
    return self.energy_battery_out[t] - self.capacity_battery / self.battery_discharge_time <= 0

def electrolyser_production(self,t):
    return sum(self.energy_electrolysers[k,t] * self.electrolyser_efficiency[k] for k in self.electrolysers) - self.energy_gH2_flux[t] == 0

def electrolyser_capacity(self,k,t):
    return self.energy_electrolysers[k,t] - self.capacity_electrolysers[k] <= 0 

def compression_limit(self,t):
    return self.energy_compression[t] - self.compression_capacity <= 0

def compressor_balance(self,t):
    return self.energy_compression[t] - sum((self.electrolyser_compression_energy[k]*(self.electrolyser_efficiency[k]/self.hydrogen_LHV))*self.energy_electrolysers[k,t] for k in self.electrolysers)\
            - sum(self.vector_compression_penalty[q]/self.hydrogen_LHV*self.energy_gh2_use[q,t] for q in self.vectors)\
                  - self.storage_compression_penalty * (self.energy_gh2_in_store[t]/self.hydrogen_LHV) == 0

def influent_hydrogen_balance(self,t):
    return self.energy_gH2_flux[t] * self.compressor_effiency - self.energy_gh2_in_store[t] - sum(self.energy_gh2_use[q,t] for q in self.vectors) == 0

def hydrogen_storage_balance(self,t):
    if self.time_values[t] == 0:
        return self.gh2_storage[t] - self.gh2_storage[self.end_time_index.value] == 0
    else:
        expr = self.gh2_storage[t] - self.gh2_storage[t-1] + self.time_duration[t] * (sum(self.energy_gh2_rem[q,t] for q in self.vectors)  - self.energy_gh2_in_store[t])
        if self.fuel_cell.value:
            expr += self.time_duration[t]*self.energy_HFC_flux[t]
        return expr == 0

def effluent_hydrogen_balance(self,q,t):
    return self.energy_vector_production_flux[q,t]/self.vector_synthetic_efficiency[q] - self.energy_gh2_rem[q,t] - self.energy_gh2_use[q,t] == 0

def hydrogen_storage_limit(self,t):
    return self.gh2_storage[t] - self.capacity_gH2_storage <= 0

def hydrogen_storage_lower_limit(self,t):
    return 0.2*self.capacity_gH2_storage - self.gh2_storage[t] <= 0

def vector_production_energy_balance(self,q,t):
    return (self.energy_vector_production_flux[q,t]) * (self.vector_variable_energy_penalty[q] / self.vector_calorific_value[q]) * (1 - self.vector_fixed_energy_penalty[q])\
            + self.number_active_trains[q,t] * self.vector_fixed_energy_penalty[q] * self.vector_variable_energy_penalty[q] * self.single_train_throughput_limit[q]\
                - (self.energy_penalty_vector_production[q,t]) == 0

def lower_ramping_limit(self,q,t):
    if self.time_values[t] == 0:
        return Constraint.Skip
    elif self.relaxed_ramping:
        return (self.energy_vector_production_flux[q,t-1] - self.energy_vector_production_flux[q,t])/self.vector_calorific_value[q] - self.number_active_trains[q,t] * self.single_train_throughput_limit[q] * self.ramp_down_limit[q]*self.time_duration[t] <= 0
    else:
        return (self.energy_vector_production_flux[q,t-1] - self.energy_vector_production_flux[q,t])/self.vector_calorific_value[q] - self.number_active_trains[q,t] * self.single_train_throughput_limit[q] * self.ramp_down_limit[q] <= 0

def upper_ramping_limit(self,q,t):
    if self.time_values[t] == 0:
        return Constraint.Skip
    elif self.relaxed_ramping:
        return (self.energy_vector_production_flux[q,t] - self.energy_vector_production_flux[q,t-1] )/self.vector_calorific_value[q] - (self.capacity_vector_production[q] + 1 - self.number_active_trains[q,t]) * self.single_train_throughput_limit[q] * self.ramp_up_limit[q]*self.time_duration[t] <= 0
    else:
        return (self.energy_vector_production_flux[q,t] - self.energy_vector_production_flux[q,t-1] )/self.vector_calorific_value[q] - (self.capacity_vector_production[q] + 1 - self.number_active_trains[q,t]) * self.single_train_throughput_limit[q] * self.ramp_up_limit[q] <= 0
    
def vector_upper_production_limit(self,q,t):
    if q == 'LH2':
        return (self.energy_vector_production_flux[q,t]) / self.vector_calorific_value[q] + self.vector_storage_origin[q,t]*self.bol_rate[q]*self.bol_energy_penalty[q]*1000 - self.single_train_throughput_limit[q] * self.number_active_trains[q,t] <= 0
    else: 
        return (self.energy_vector_production_flux[q,t]  / self.vector_calorific_value[q]) - self.single_train_throughput_limit[q] * self.number_active_trains[q,t] <= 0 

def vector_lower_production_limit(self,q,t):
    return self.single_train_throughput_limit[q] * self.minimum_process_throughput[q] - (self.energy_vector_production_flux[q,t]  / self.vector_calorific_value[q])  <= 0
    
def active_train_limit(self,q,t):
    return self.number_active_trains[q,t]  - self.capacity_vector_production[q] <= 0

def origin_vector_storage_balance(self,q,t):
    if self.time_values[t] == 0:
        return self.vector_storage_origin[q,t] - self.vector_storage_origin[q,self.end_time_index.value] == 0
    else:
        return (self.vector_storage_origin[q,t] - self.vector_storage_origin[q,t-1])*1000 + self.time_duration[t]*(-(self.energy_vector_production_flux[q,t]*self.vector_fugitive_efficiency[q]) / self.vector_calorific_value[q]\
              + sum(self.number_ships_charging[j,q,t] * (self.ship_storage_capacity[j,q] / self.loading_time) for j in self.ships)) == 0
    
def origin_vector_storage_limit(self,q,t):
    return self.vector_storage_origin[q,t] - self.capacity_vector_storage_origin[q] <= 0

def origin_storage_min(self,q,t):
    return 0.2*self.capacity_vector_storage_origin[q] - self.vector_storage_origin[q,t] <= 0

def origin_storage_max(self,q):
    return self.single_train_throughput_limit[q] * self.capacity_vector_production[q] * 3 * 24 - self.capacity_vector_storage_origin[q]*1000 <= 0 

def destination_vector_storage_balance(self,q,t):
    if self.time_values[t] == 0:
        return self.vector_storage_destination[q,t] - self.vector_storage_destination[q,self.end_time_index.value] == 0
    else:
        expr = 1000*(self.vector_storage_destination[q,t] - self.vector_storage_destination[q,t-1]) - self.time_duration[t]*((sum(self.number_ships_discharging[j,q,t]  * ((self.ship_storage_capacity[j,q] - 2*(self.journey_time)*self.ship_fuel_consumption[j,q])\
               / self.loading_time) for j in self.ships)) - self.bol_rate[q] * sum((self.number_ships_destination[j,q,t] - self.number_ships_discharging[j,q,t])*self.ship_storage_capacity[j,q]for j in self.ships))
        if self.reconversion:
            expr += self.time_duration[t]*(self.energy_vector_consumption_flux[q,t] * (1 / (self.reconversion_efficiency[q]))/ self.vector_calorific_value[q])
        if not self.reconversion:
            expr +=  self.time_duration[t]*(self.energy_vector_consumption_flux[q,t]/ self.vector_calorific_value[q])
        return expr == 0
    
def destination_vector_storage_limit(self,q,t):
    return self.vector_storage_destination[q,t] - self.capacity_vector_storage_destination[q] <= 0

def destination_storage_min(self,q,t):
    return 0.2*self.capacity_vector_storage_destination[q] - self.vector_storage_destination[q,t] <= 0

def destination_storage_max(self):
    return self.destination_storage_requirement / 1000 - sum(self.vector_calorific_value[q]*self.capacity_vector_storage_destination[q] for q in self.vectors) <= 0 

def shipping_balance_origin(self,j,q,t):
    if self.time_values[t] == 0:
        return self.number_ships_origin[j,q,t] - self.number_ships_origin[j,q,self.end_time_index.value] == 0
    elif self.time_values[t] < self.loading_time.value:
        return self.number_ships_origin[j,q,t] - self.number_ships_origin[j,q,t-1] == 0
    elif self.time_values[t] < self.journey_time:
        if (self.time_values[t] - self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_origin[j,q,t] - self.number_ships_origin[j,q,t-1] +  self.time_duration[t] * self.number_ships_start_charging[j,q,int((self.time_values[t]-self.loading_time)\
                /self.shipping_decision_granularity)] == 0
        else: return self.number_ships_origin[j,q,t] - self.number_ships_origin[j,q,t-1] == 0
    else:
        if (self.time_values[t] - self.loading_time) % self.shipping_decision_granularity.value  == 0 and (self.time_values[t]-self.journey_time - self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_origin[j,q,t] - self.number_ships_origin[j,q,t-1] + self.time_duration[t] * self.number_ships_start_charging[j,q,int((self.time_values[t]-self.loading_time)\
                /self.shipping_decision_granularity)] - self.time_duration[t] * self.number_ships_start_discharging[j,q,int((t-self.journey_time - self.loading_time)/self.shipping_decision_granularity)] == 0
        elif (self.time_values[t] - self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_origin[j,q,t] - self.number_ships_origin[j,q,t-1] + self.time_duration[t] * self.number_ships_start_charging[j,q,int((self.time_values[t]-self.loading_time)\
                /self.shipping_decision_granularity)] == 0
        elif (self.time_values[t]-self.journey_time - self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_origin[j,q,t] - self.number_ships_origin[j,q,t-1] - self.time_duration[t] * self.number_ships_start_discharging[j,q,int((self.time_values[t]-self.journey_time\
                - self.loading_time)/self.shipping_decision_granularity)] == 0
        else: return self.number_ships_origin[j,q,t] - self.number_ships_origin[j,q,t-1] == 0

def shipping_balance_charging(self,j,q,t):
    if self.time_values[t] == 0:
        return self.number_ships_charging[j,q,t] - self.number_ships_start_charging[j,q,int(self.time_values[t]/self.shipping_decision_granularity)] == 0
    elif self.time_values[t] < self.loading_time:
        if self.time_values[t] % self.shipping_decision_granularity.value == 0:
            return self.number_ships_charging[j,q,t] - self.number_ships_charging[j,q,t-1] - self.time_duration[t] * self.number_ships_start_charging[j,q,int(self.time_values[t]/self.shipping_decision_granularity)] == 0
        else: return self.number_ships_charging[j,q,t] - self.number_ships_charging[j,q,t-1] == 0
    else:
        if self.time_values[t] % self.shipping_decision_granularity.value  == 0 and (self.time_values[t]-self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_charging[j,q,t] - self.number_ships_charging[j,q,t-1] - self.time_duration[t] *  self.number_ships_start_charging[j,q,int(self.time_values[t]/self.shipping_decision_granularity)]\
                + self.time_duration[t] *  self.number_ships_start_charging[j,q,int((self.time_values[t]-self.loading_time)/self.shipping_decision_granularity)] == 0
        elif self.time_values[t] % self.shipping_decision_granularity.value == 0:
            return self.number_ships_charging[j,q,t] - self.number_ships_charging[j,q,t-1] - self.time_duration[t] * self.number_ships_start_charging[j,q,int(self.time_values[t]/self.shipping_decision_granularity)] == 0
        elif (self.time_values[t]-self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_charging[j,q,t] - self.number_ships_charging[j,q,t-1] + self.time_duration[t] * self.number_ships_start_charging[j,q,int((self.time_values[t]-self.loading_time)\
                /self.shipping_decision_granularity)] == 0
        else: return self.number_ships_charging[j,q,t] - self.number_ships_charging[j,q,t-1] == 0

def charging_ship_limit(self,j,q,t):
    return self.number_ships_charging[j,q,t] - self.number_ships_origin[j,q,t] <= 0

def number_of_ships(self,j,q,t):
    if self.time_values[t] == 0:
        return self.number_ships_origin[j,q,t] + self.number_ships_destination[j,q,t] - self.number_ships_total[j,q] == 0
    else:
        return Constraint.Skip

def shipping_balance_destination(self,j,q,t):
    if self.time_values[t] == 0:
        return self.number_ships_destination[j,q,t] - self.number_ships_destination[j,q,self.end_time_index.value] == 0
    elif self.time_values[t] < self.loading_time:
        return self.number_ships_destination[j,q,t] - self.number_ships_destination[j,q,t-1] == 0
        
    elif self.time_values[t] < self.journey_time:
        if (self.time_values[t] - self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_destination[j,q,t] - self.number_ships_destination[j,q,t-1] + self.time_duration[t] * self.number_ships_start_discharging[j,q,int((self.time_values[t]-self.loading_time)\
                /self.shipping_decision_granularity)] == 0
        else: return self.number_ships_destination[j,q,t] - self.number_ships_destination[j,q,t-1] == 0
    else:
        if (self.time_values[t] - self.loading_time) % self.shipping_decision_granularity.value  == 0 and (self.time_values[t]-self.journey_time - self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_destination[j,q,t] - self.number_ships_destination[j,q,t-1] + self.time_duration[t] * self.number_ships_start_discharging[j,q,int((self.time_values[t]-self.loading_time)\
                /self.shipping_decision_granularity)] - self.time_duration[t] * self.number_ships_start_charging[j,q,int((self.time_values[t]-self.journey_time - self.loading_time)/self.shipping_decision_granularity)] == 0
        elif (self.time_values[t] - self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_destination[j,q,t] - self.number_ships_destination[j,q,t-1] + self.time_duration[t] * self.number_ships_start_discharging[j,q,int((self.time_values[t]-self.loading_time)\
                /self.shipping_decision_granularity)] == 0
        elif (self.time_values[t] - self.journey_time - self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_destination[j,q,t] - self.number_ships_destination[j,q,t-1] - self.time_duration[t] * self.number_ships_start_charging[j,q,int((self.time_values[t]-self.journey_time\
                - self.loading_time)/self.shipping_decision_granularity)] == 0
        else: return self.number_ships_destination[j,q,t] - self.number_ships_destination[j,q,t-1] == 0

def shipping_balance_discharging(self,j,q,t):
    if self.time_values[t] == 0:
        return self.number_ships_discharging[j,q,t] - self.time_duration[t] * self.number_ships_start_discharging[j,q,int(self.time_values[t]/self.shipping_decision_granularity)] == 0 
    elif self.time_values[t] < self.loading_time:
        if self.time_values[t] % self.shipping_decision_granularity.value == 0:
            return self.number_ships_discharging[j,q,t] - self.number_ships_discharging[j,q,t-1] - self.time_duration[t] * self.number_ships_start_discharging[j,q,int(self.time_values[t]/self.shipping_decision_granularity)] == 0
        else: return self.number_ships_discharging[j,q,t] - self.number_ships_discharging[j,q,t-1] == 0
    else:      
        if self.time_values[t] % self.shipping_decision_granularity.value == 0 and (self.time_values[t]-self.loading_time) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_discharging[j,q,t] - self.number_ships_discharging[j,q,t-1] - self.time_duration[t] * self.number_ships_start_discharging[j,q,int(self.time_values[t]/self.shipping_decision_granularity)]\
                + self.time_duration[t] * self.number_ships_start_discharging[j,q,int((self.time_values[t]-self.loading_time)/self.shipping_decision_granularity)] == 0
        elif self.time_values[t] % self.shipping_decision_granularity.value == 0:
            return self.number_ships_discharging[j,q,t] - self.number_ships_discharging[j,q,t-1] - self.time_duration[t] * self.number_ships_start_discharging[j,q,int(self.time_values[t]/self.shipping_decision_granularity)] == 0
        elif (self.time_values[t]-self.loading_time.value) % self.shipping_decision_granularity.value == 0:
            return self.number_ships_discharging[j,q,t] - self.number_ships_discharging[j,q,t-1] + self.time_duration[t] * self.number_ships_start_discharging[j,q,int((self.time_values[t]-self.loading_time)\
                /self.shipping_decision_granularity)] == 0
        else: return self.number_ships_discharging[j,q,t] - self.number_ships_discharging[j,q,t-1] == 0

def discharging_ship_limit(self,j,q,t):
    return self.number_ships_discharging[j,q,t] - self.number_ships_destination[j,q,t] <= 0

def demand_signal_matching(self,t):
    return self.demand_signal[t] - sum(self.energy_vector_consumption_flux[q,t] for q in self.vectors) <= 0

def vector_reconversion_limit(self,q,t):
    return self.energy_vector_consumption_flux[q,t] - self.capacity_vector_conversion[q] * self.vector_calorific_value[q] <= 0

def total_capital_expenditure(self):
    expr = 0
    expr += self.turbine_unit_capital_cost * self.capacity_number_turbines * self.amortisation_turbine
    if self.fuel_cell.value:
        expr += self.fuel_cell_unit_capital_cost * self.capacity_HFC * self.amortisation_fuel_cell
    if self.battery.value:
        expr += self.battery_unit_capital_cost * self.capacity_battery * self.amortisation_battery
    expr += sum(self.electrolyser_unit_capital_cost[k] * self.capacity_electrolysers[k] * self.amortisation_electrolysers[k] for k in self.electrolysers)
    expr += self.compression_capacity * self.compressor_unit_capital_cost * self.amortisation_compressor / self.hydrogen_LHV
    expr += (self.hydrogen_storage_unit_capital_cost / self.hydrogen_LHV) * self.capacity_gH2_storage * self.amortisation_hydrogen_storage
    expr += sum(self.vector_production_unit_capital_cost[q] * self.capacity_vector_production[q] * self.amortisation_vector_production[q] for q in self.vectors)
    expr += sum((self.capacity_vector_storage_origin[q] + self.capacity_vector_storage_destination[q]) * (self.vector_storage_unit_capital_cost[q])\
                * self.amortisation_vector_storage[q] for q in self.vectors) 
    expr += sum(sum(self.number_ships_total[j,q] * self.ship_unit_capital_cost[j,q] * self.amortisation_ships[j] for j in self.ships) for q in self.vectors) 
    if self.reconversion.value:
        expr += sum(self.capacity_vector_conversion[q] * self.reconversion_unit_capital_cost[q] * self.amortisation_reconversion[q] for q in self.vectors)
    return expr - self.CAPEX <= 0

def total_operating_expenditure(self):
    expr = 0
    expr += self.turbine_unit_operating_cost * self.capacity_number_turbines * self.amortisation_plant
    if self.fuel_cell.value:
        expr += self.fuel_cell_unit_operating_cost * self.capacity_HFC * self.amortisation_plant
    if self.battery.value:
        expr += self.battery_unit_operating_cost * self.capacity_battery * self.amortisation_plant
    if self.grid_connection.value:
        expr += self.net_grid * self.grid_energy_factor * self.LCOWP * self.amortisation_plant
    expr += sum(self.electrolyser_unit_operating_cost[k] * self.capacity_electrolysers[k] * self.amortisation_plant for k in self.electrolysers)
    expr += self.compression_capacity * self.compressor_unit_operating_cost * self.amortisation_plant / self.hydrogen_LHV
    expr += (self.hydrogen_storage_unit_operating_cost / self.hydrogen_LHV) * self.capacity_gH2_storage * self.amortisation_plant
    expr += sum(self.vector_production_unit_operating_cost[q] * self.capacity_vector_production[q] * self.amortisation_plant for q in self.vectors)
    expr += sum((self.capacity_vector_storage_origin[q] + self.capacity_vector_storage_destination[q]) * (self.vector_storage_unit_operating_cost[q])\
                 for q in self.vectors) * self.amortisation_plant
    expr += sum(sum(self.number_ships_total[j,q] * self.ship_unit_operating_cost[j,q] for j in self.ships) for q in self.vectors) * self.amortisation_plant
    if self.reconversion.value:
        expr += sum(self.capacity_vector_conversion[q] * self.reconversion_unit_operating_cost[q] * self.amortisation_plant for q in self.vectors)
    return expr - self.OPEX <= 0

def generate_inequalities(self):
    # Specifying an energy balance for the energy production of the system
    self.model.energy_balance   = Constraint(self.model.time, rule = energy_balance)

    # If a grid connection is used, calculating the net usage. This is in a bid to avoid mismatching coefficient sizes in the OPEX function 
    if self.model.grid_connection.value:
        self.model.cumulative_grid_use = Constraint(rule = cumulative_grid_use)

    # Specifying fuel cell equaitons, if a fuel cell is utilized in the model.
    if self.model.fuel_cell.value:
        self.model.fuel_cell_production_curve   = Constraint(self.model.time, rule = fuel_cell_production_curve)
        self.model.fuel_cell_capacity           = Constraint(self.model.time, rule = fuel_cell_capacity)

    # Specifying battery equations, if a battery is utilized in the model.
    if self.model.battery.value:
        self.model.battery_energy_balance       = Constraint(self.model.time, rule = battery_energy_balance)
        self.model.battery_storage_capacity     = Constraint(self.model.time, rule = battery_storage_capacity)
        self.model.battery_charging_limit       = Constraint(self.model.time, rule = battery_charging_limit)
        self.model.battery_discharging_limit    = Constraint(self.model.time, rule = battery_discharging_limit)

    # Specifying electrolysis equations.
    self.model.electrolyser_production  = Constraint(self.model.time, rule = electrolyser_production)
    self.model.electrolyser_capacity    = Constraint(self.model.electrolysers, self.model.time, rule = electrolyser_capacity)

    # Specifying gaseous hydrogen storage equations
    self.model.hydrogen_storage_balance     = Constraint(self.model.time,rule = hydrogen_storage_balance)
    self.model.hydrogen_storage_limit       = Constraint(self.model.time,rule = hydrogen_storage_limit)
    self.model.hydrogen_storage_lower_limit = Constraint(self.model.time, rule = hydrogen_storage_lower_limit)
    self.model.influent_hydrogen_balance    = Constraint(self.model.time, rule = influent_hydrogen_balance)
    self.model.effluent_hydrogen_balance    = Constraint(self.model.vectors,self.model.time, rule = effluent_hydrogen_balance)

    # Specifying compression equations
    self.model.compression_limit            = Constraint(self.model.time,rule=compression_limit)
    self.model.compression_balance          = Constraint(self.model.time,rule=compressor_balance)

    # Specifying vector production equations
    self.model.vector_production_energy_balance = Constraint(self.model.vectors,self.model.time, rule = vector_production_energy_balance)
    self.model.vector_upper_production_limit    = Constraint(self.model.vectors,self.model.time, rule = vector_upper_production_limit)
    self.model.vector_lower_production_limit    = Constraint(self.model.vectors,self.model.time, rule = vector_lower_production_limit)
    self.model.active_train_limit               = Constraint(self.model.vectors,self.model.time, rule = active_train_limit)
    self.model.lower_ramping_limit              = Constraint(self.model.vectors,self.model.time, rule = lower_ramping_limit)
    self.model.upper_ramping_limit              = Constraint(self.model.vectors,self.model.time, rule = upper_ramping_limit)


    # Specifying vector storage equations
    self.model.origin_vector_storage_balance        = Constraint(self.model.vectors,self.model.time, rule = origin_vector_storage_balance)
    self.model.origin_vector_storage_limit          = Constraint(self.model.vectors,self.model.time, rule = origin_vector_storage_limit)
    self.model.origin_storage_min                   = Constraint(self.model.vectors,self.model.time, rule = origin_storage_min)
    self.model.origin_storage_max                   = Constraint(self.model.vectors, rule = origin_storage_max)
    self.model.destination_vector_storage_balance   = Constraint(self.model.vectors,self.model.time, rule = destination_vector_storage_balance)
    self.model.destination_vector_storage_limit     = Constraint(self.model.vectors,self.model.time, rule = destination_vector_storage_limit)
    self.model.destination_storage_min              = Constraint(self.model.vectors,self.model.time, rule=destination_storage_min)
    self.model.destination_storage_max              = Constraint(rule = destination_storage_max)

    # Specifying shipping equations
    self.model.number_of_ships                        = Constraint(self.model.ships,self.model.vectors,self.model.time, rule = number_of_ships)
    self.model.shipping_balance_origin                = Constraint(self.model.ships,self.model.vectors,self.model.time, rule = shipping_balance_origin)
    self.model.shipping_balance_destination           = Constraint(self.model.ships,self.model.vectors,self.model.time, rule = shipping_balance_destination)
    self.model.charging_ship_limit                    = Constraint(self.model.ships,self.model.vectors,self.model.time, rule = charging_ship_limit)
    self.model.discharging_ship_limit                 = Constraint(self.model.ships,self.model.vectors,self.model.time, rule = discharging_ship_limit)
    self.model.shipping_balance_charging              = Constraint(self.model.ships,self.model.vectors,self.model.time, rule = shipping_balance_charging)
    self.model.shipping_balance_discharging           = Constraint(self.model.ships,self.model.vectors,self.model.time, rule = shipping_balance_discharging)

    # Ensuring demand is met
    if self.model.reconversion.value:
        self.model.vector_reconversion_limit          = Constraint(self.model.vectors,self.model.time, rule = vector_reconversion_limit)

    self.model.demand_signal_matching                 = Constraint(self.model.time, rule = demand_signal_matching)

    # Calculating CAPEX and OPEX
    self.model.total_capital_expenditure              = Constraint(rule = total_capital_expenditure)
    self.model.total_operating_expenditure            = Constraint(rule = total_operating_expenditure)
    pass
