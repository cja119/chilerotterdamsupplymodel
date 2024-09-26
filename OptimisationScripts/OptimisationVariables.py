from pyomo.environ import NonNegativeIntegers, NonNegativeReals, Var

def generate_variables(self,parameters):

    # Starting with all energy related variables
    self.model.energy_curtailed                     = Var(self.model.time,within=NonNegativeReals)
    self.model.energy_electrolysers                 = Var(self.model.electrolysers,self.model.time,within=NonNegativeReals)
    self.model.energy_gH2_flux                      = Var(self.model.time,within=NonNegativeReals)
    self.model.energy_penalty_vector_production     = Var(self.model.vectors,self.model.time, within=NonNegativeReals)
    self.model.energy_vector_production_flux        = Var(self.model.vectors,self.model.time, within=NonNegativeReals)
    self.model.energy_vector_consumption_flux       = Var(self.model.vectors, self.model.time, within = NonNegativeReals)
    self.model.energy_demand_signal_flux            = Var(self.model.time, within=NonNegativeReals)

    # Adding compressino and GH2 Balance variables
    self.model.energy_compression                   = Var(self.model.time,within=NonNegativeReals)
    self.model.compression_capacity                 = Var(within=NonNegativeReals)
    self.model.energy_gh2_use                       = Var(self.model.vectors,self.model.time,within=NonNegativeReals)
    self.model.energy_gh2_rem                       = Var(self.model.vectors,self.model.time,within=NonNegativeReals)
    self.model.energy_gh2_in_store                  = Var(self.model.time,within=NonNegativeReals)
    

    if self.model.grid_connection.value:
        self.model.energy_grid          = Var(self.model.time,within=NonNegativeReals)
        self.model.net_grid             = Var(within = NonNegativeReals)
    if self.model.fuel_cell.value:
        self.model.energy_HFC           = Var(self.model.time,within=NonNegativeReals)
        self.model.energy_HFC_flux      = Var(self.model.time,within=NonNegativeReals)
        self.model.capacity_HFC         = Var(within=NonNegativeReals)
    if self.model.battery.value:
        self.model.energy_battery_in    = Var(self.model.time,within=NonNegativeReals)
        self.model.energy_battery_out   = Var(self.model.time,within=NonNegativeReals)
        self.model.capacity_battery     = Var(within=NonNegativeReals)
        self.model.battery_storage      = Var(self.model.time,within=NonNegativeReals)

    # Generating accumulation related variables
    self.model.gh2_storage                          = Var(self.model.time,within=NonNegativeReals)
    self.model.vector_storage_origin                = Var(self.model.vectors, self.model.time,within=NonNegativeReals)
    self.model.vector_storage_destination           = Var(self.model.vectors, self.model.time,within=NonNegativeReals)

    # Generating equipment size related variables
    self.model.capacity_gH2_storage                 = Var(within=NonNegativeReals)
    self.model.capacity_vector_storage_origin       = Var(self.model.vectors, within=NonNegativeReals)
    self.model.capacity_vector_storage_destination  = Var(self.model.vectors, within=NonNegativeReals)
    self.model.capacity_electrolysers               = Var(self.model.electrolysers,within=NonNegativeReals)
    self.model.number_active_trains                 = Var(self.model.vectors, self.model.time, within = NonNegativeIntegers)
    self.model.capacity_vector_production           = Var(self.model.vectors,within=NonNegativeReals)
    self.model.capacity_number_turbines             = Var(within=NonNegativeReals)
    self.model.destination_storage_requirement      = Var(within=NonNegativeReals)
    if self.model.reconversion.value:
        self.model.capacity_vector_conversion       = Var(self.model.vectors, within=NonNegativeReals)

    # Generating shipping scheduling related variables
    self.model.number_ships_start_charging          = Var(self.model.ships,self.model.vectors,self.model.shipping_time, within = NonNegativeIntegers)
    self.model.number_ships_start_discharging       = Var(self.model.ships,self.model.vectors,self.model.shipping_time, within = NonNegativeIntegers)
    self.model.number_ships_charging                = Var(self.model.ships,self.model.vectors,self.model.time, within=NonNegativeReals)  
    self.model.number_ships_discharging             = Var(self.model.ships,self.model.vectors,self.model.time, within=NonNegativeReals)  
    self.model.number_ships_origin                  = Var(self.model.ships,self.model.vectors,self.model.time, within=NonNegativeReals)                
    self.model.number_ships_destination             = Var(self.model.ships,self.model.vectors,self.model.time, within=NonNegativeReals)
    self.model.number_ships_total                   = Var(self.model.ships,self.model.vectors, within=NonNegativeReals)

    # Generating cost variables
    self.model.CAPEX    = Var(within=NonNegativeReals)
    self.model.OPEX     = Var(within=NonNegativeReals)
    pass