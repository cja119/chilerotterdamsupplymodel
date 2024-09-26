from matplotlib.pyplot import  subplots, show,legend, gca,bar,xticks, fill_between, minorticks_on,tick_params
from matplotlib.ticker import MaxNLocator
from plotly.graph_objects import Figure, Sankey
from numpy import array,zeros,size

def demand_and_wind_energy(self):
    # Initialising the subplots environment and employing the custom colour scheme. 
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    legend_entry = ('Energy From Wind Farm','Demand Signal at Destination')

    # Addiing the energy produced by the turbine to the plot

    ax.plot([*self.instance.time_values.values()],
            array([*self.instance.turbine_power.values()][:self.instance.end_time_index+1])*int(self.instance.capacity_number_turbines.value),
            label = legend_entry[line_counter],
            color = cmap[line_counter],
            linewidth = self.linewidth
            )
    
    line_counter += 1

    # Adding the demand signal to the plot
    ax.plot([*self.instance.time_values.values()],
                 [*self.instance.demand_signal.values()][:self.instance.end_time_index+1],
                 label = legend_entry[line_counter],
                 color = cmap[line_counter],
                 linewidth = self.linewidth
                 )
    line_counter += 1
    
    # Updating the axes
    ax.set(xlabel = 'Time [h]',
           ylabel = 'Energy [GJ/h]',
           title = 'Demand Signal and Wind Farm Energy against Time'
           )
    
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    legend()
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which = 'minor',
                length = 2,
                width = 1,
                direction = 'out',
                labelsize = 0
                ) 
    
    # Displaying the plot
    show()
    pass

def hydrogen_storage_tank_level(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    
   
    ax.plot([*self.instance.time_values.values()], 
            array([*self.instance.gh2_storage[:].value]),
            color = cmap[line_counter],
            linewidth = self.linewidth
            )

    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Hydrogen Storage at Origin [GJ]',
           title='Hydrogen Storage Against time'
           )
    
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    legend()
    minorticks_on()
    
    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                ) 
    
    # Displaying the plot
    show()
    pass

def origin_storage_tank_levels(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    
    for i in self.instance.vectors:
        ax.plot([*self.instance.time_values.values()], 
                array([*self.instance.vector_storage_origin[i,:].value]),
                label = i,
                color = cmap[line_counter],
                linewidth = self.linewidth
                )
        line_counter += 1

    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Vector Storage at Origin [TJ]',
           title='Origin Vector Storage Against time'
           )
    
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    legend()
    minorticks_on()
    
    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                ) 
    
    # Displaying the plot
    show()
    pass

def destination_storage_tank_levels(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap    = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.
    line_counter = 0
    
    for i in self.instance.vectors:
        ax.plot([*self.instance.time_values.values()], 
                array([*self.instance.vector_storage_destination[i,:].value]),
                label = i,
                color = cmap[line_counter],
                linewidth = self.linewidth
                )
        line_counter += 1

    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Vector Storage at Destination [TJ]',
           title='Destination Vector Storage Against time'
           )
    
    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    legend()
    minorticks_on()
    
    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                ) 
    
    # Displaying the plot
    show()
    pass

def hydrogen_production(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.    
    line_counter = 0

    # As this will be a stacked plot, y is the array to which each plot is added to.
    y = zeros(size(self.instance.time_values))
    
    for i in self.instance.electrolysers:
        # Plotting an infill for the stacked plot
        fill_between([*self.instance.time],
                     y,
                     y+array([*self.instance.energy_electrolysers[i,:].value]), 
                     color = cmap[line_counter],
                     alpha = self.alpha)
        
        # Updating the y array
        y += array([*self.instance.energy_electrolysers[i,:].value])
        
        # Plottin the line
        ax.plot([*self.instance.time_values.values()],
                y,
                label = i, 
                color = cmap[line_counter],
                linewidth = self.linewidth
                )
        
        line_counter += 1
    
    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Hydrogen Production [GJ/h]',
        title='Hydrogen Production Against time'
        )

    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    legend()
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                )
    
    # Displaying the plot
    show()
    pass

def vector_production(self):
    # Initialising the subplots environment and employing the custom colour scheme.
    fig, ax = subplots()
    cmap = self.custom_cmap 

    # Initiating a line counter, to be used to update the legend entry and colour.    
    line_counter = 0

    # As this will be a stacked plot, y is the array to which each plot is added to.
    y = zeros(size(self.instance.time_values))
    
    for i in self.instance.vectors:
        # Plotting an infill for the stacked plot
        fill_between([*self.instance.time_values.values()],
                     y,
                     y+array([*self.instance.energy_vector_production_flux[i,:].value]), 
                     color = cmap[line_counter],
                     alpha = self.alpha)
        
        # Updating the y array
        y += array([*self.instance.energy_vector_production_flux[i,:].value])
        
        # Plottin the line
        ax.plot([*self.instance.time_values.values()],
                y,
                label = i, 
                color = cmap[line_counter],
                linewidth = self.linewidth
                )
        
        line_counter += 1
    
    # Updating the axes
    ax.set(xlabel='Time [h]',
           ylabel='Vector Production [GJ/h]',
        title='Vector Production Against time'
        )

    # Updating plot settings
    gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    legend()
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which='minor',
                length=2,
                width=1,
                direction='out',
                labelsize=0
                )
    
    # Displaying the plot
    show()
    pass

def LCOH_contributions(self,threshold):
    
    # Producing lists, containing the different LCOH contributions
    categories  = ['Total LCOH',
                   'Wind Turbines']
    OPEX        = [(10**6)*self.instance.OPEX.value / self.instance.discounted_demand,
                   (10**6)*self.instance.turbine_unit_operating_cost * self.instance.capacity_number_turbines.value * self.instance.amortisation_plant / self.instance.discounted_demand
                   ]
    CAPEX       = [(10**6)*self.instance.CAPEX.value / self.instance.discounted_demand,
                   (10**6)*self.instance.turbine_unit_capital_cost * self.instance.capacity_number_turbines.value * self.instance.amortisation_turbine / self.instance.discounted_demand
                   ]

    if self.instance.grid_connection.value:
        if (10**6)*self.instance.net_grid.value * self.instance.LCOWP * self.instance.grid_energy_factor * self.instance.amortisation_plant / self.instance.discounted_demand >= threshold:
            categories.append("Grid Connection")
            OPEX.append((10**6)*self.instance.net_grid.value * self.instance.LCOWP * self.instance.grid_energy_factor * self.instance.amortisation_plant / self.instance.discounted_demand)
            CAPEX.append(0)

    if self.instance.fuel_cell.value:
        if (10**6)*self.instance.fuel_cell_unit_capital_cost * self.instance.capacity_HFC.value * self.instance.amortisation_fuel_cell / self.instance.discounted_demand >= threshold:
            categories.append("Fuel Cell")
            OPEX.append((10**6)*self.instance.fuel_cell_unit_operating_cost * self.instance.capacity_HFC.value * self.instance.amortisation_plant / self.instance.discounted_demand)
            CAPEX.append((10**6)*self.instance.fuel_cell_unit_capital_cost * self.instance.capacity_HFC.value * self.instance.amortisation_fuel_cell / self.instance.discounted_demand)

    if self.instance.battery.value:
        if (10**6)*self.instance.battery_unit_capital_cost * self.instance.capacity_battery.value * self.instance.amortisation_battery / self.instance.discounted_demand >= threshold:
            categories.append("Battery")
            OPEX.append((10**6)*self.instance.battery_unit_operating_cost * self.instance.capacity_battery.value * self.instance.amortisation_plant / self.instance.discounted_demand)
            CAPEX.append((10**6)*self.instance.battery_unit_capital_cost * self.instance.capacity_battery.value * self.instance.amortisation_battery / self.instance.discounted_demand)

    for i in self.instance.electrolysers:
        if (10**6)*self.instance.electrolyser_unit_capital_cost[i] * self.instance.capacity_electrolysers[i].value * self.instance.amortisation_electrolysers[i]/ self.instance.discounted_demand >= threshold:
            categories.append(i+' Electrolysis')
            OPEX.append((10**6)*self.instance.electrolyser_unit_operating_cost[i] * self.instance.capacity_electrolysers[i].value * self.instance.amortisation_plant / self.instance.discounted_demand)
            CAPEX.append((10**6)*self.instance.electrolyser_unit_capital_cost[i] * self.instance.capacity_electrolysers[i].value * self.instance.amortisation_electrolysers[i]/ self.instance.discounted_demand)

    if (10**6)*(self.instance.hydrogen_storage_unit_capital_cost / self.instance.hydrogen_LHV) * self.instance.capacity_gH2_storage.value * self.instance.amortisation_hydrogen_storage / self.instance.discounted_demand >= threshold:
        categories.append('GH2 Storage')
        OPEX.append((10**6)*(self.instance.hydrogen_storage_unit_operating_cost / self.instance.hydrogen_LHV) * self.instance.capacity_gH2_storage.value * self.instance.amortisation_plant / self.instance.discounted_demand)
        CAPEX.append((10**6)*(self.instance.hydrogen_storage_unit_capital_cost / self.instance.hydrogen_LHV) * self.instance.capacity_gH2_storage.value * self.instance.amortisation_hydrogen_storage / self.instance.discounted_demand)
    
    for i in self.instance.vectors:
        if (10**6)*self.instance.vector_production_unit_capital_cost[i] * self.instance.capacity_vector_production[i].value * self.instance.amortisation_vector_production[i] / self.instance.discounted_demand >= threshold:
            categories.append(i+' Production')
            OPEX.append((10**6)*self.instance.vector_production_unit_operating_cost[i] * self.instance.capacity_vector_production[i].value * self.instance.amortisation_plant / self.instance.discounted_demand)
            CAPEX.append((10**6)*self.instance.vector_production_unit_capital_cost[i] * self.instance.capacity_vector_production[i].value * self.instance.amortisation_vector_production[i] / self.instance.discounted_demand)

    for i in self.instance.vectors:
        if (10**6)*(self.instance.capacity_vector_storage_origin[i].value + self.instance.capacity_vector_storage_destination[i].value) * (self.instance.vector_storage_unit_capital_cost[i]* self.instance.amortisation_vector_storage[i]) / self.instance.discounted_demand >= threshold:
            categories.append(i+' Storage')
            OPEX.append((10**6)*(self.instance.capacity_vector_storage_origin[i].value + self.instance.capacity_vector_storage_destination[i].value) * (self.instance.vector_storage_unit_operating_cost[i] * self.instance.amortisation_plant) / self.instance.discounted_demand)
            CAPEX.append((10**6)*(self.instance.capacity_vector_storage_origin[i].value + self.instance.capacity_vector_storage_destination[i].value) * (self.instance.vector_storage_unit_capital_cost[i] * self.instance.amortisation_vector_storage[i]) / self.instance.discounted_demand )
    
    for i in self.instance.vectors:
        if (10**6)*sum(self.instance.number_ships_total[j,i].value * self.instance.ship_unit_capital_cost[j,i] * self.instance.amortisation_ships[j] for j in self.instance.ships)/ self.instance.discounted_demand >= threshold:
            categories.append(i+' Ships')
            OPEX.append((10**6)*sum(self.instance.number_ships_total[j,i].value * self.instance.ship_unit_operating_cost[j,i] * self.instance.amortisation_plant for j in self.instance.ships)/ self.instance.discounted_demand)
            CAPEX.append((10**6)*sum(self.instance.number_ships_total[j,i].value * self.instance.ship_unit_capital_cost[j,i] * self.instance.amortisation_ships[j] for j in self.instance.ships)/ self.instance.discounted_demand)

    if self.instance.reconversion:
        for i in self.instance.vectors:
            if (10**6)*self.instance.capacity_vector_conversion[i].value * self.instance.reconversion_unit_capital_cost[i] * self.instance.amortisation_reconversion[i] / self.instance.discounted_demand >= threshold:
                categories.append(i+' Cracking')
                OPEX.append((10**6)*self.instance.capacity_vector_conversion[i].value * self.instance.reconversion_unit_operating_cost[i] * self.instance.amortisation_plant/ self.instance.discounted_demand)
                CAPEX.append((10**6)*self.instance.capacity_vector_conversion[i].value * self.instance.reconversion_unit_capital_cost[i] * self.instance.amortisation_reconversion[i] / self.instance.discounted_demand)

    # Initialising the subplots environment.
    fig, ax = subplots()
    
    # Plotting the bar chart    
    bar(categories, CAPEX, label='CAPEX',color=self.custom_cmap[0])
    bar(categories, OPEX, bottom=CAPEX, label='OPEX',color=self.custom_cmap[1])

    # Updating the axes    
    ax.set(ylabel='LCOH [$/kg]')

    # Updating plot settings    
    xticks(rotation = 45,ha='right')
    legend()
    minorticks_on()

    # Updating the hyperaparmeters for the tick markers
    tick_params(which = 'minor',
                length = 2,
                width = 1,
                direction = 'out',
                labelsize = 0
                ) 
    
    # Producing dictionaries of the CAPEX and OPEX breakdowns for the user
    self.CAPEX = dict(zip(categories, CAPEX))
    self.OPEX = dict(zip(categories, OPEX))
    
    # Displaying the plot
    show()
    pass

def sankey_diagram(self,threshold,height):

    normaliser  = sum(self.instance.demand_signal[t]*self.instance.time_duration[t] for t in self.instance.time)
    grid        = 0
    battery     = 0
    fuel_cell   = 0
    conversion  = 0

    labels = ["Blank",
              "Renewable Energy",
              "Low Wind Loss",
              "Electrical Energy"]
    connections = [(1,2,sum(self.instance.capacity_number_turbines.value * self.instance.time_duration[t]*(max(self.instance.turbine_power[t] for t in self.instance.time) - self.instance.turbine_power[t]) for t in self.instance.time) / normaliser),
                   (1,3,sum(self.instance.time_duration[t]*self.instance.capacity_number_turbines.value * self.instance.turbine_power[t]*self.instance.turbine_efficiency for t in self.instance.time) / normaliser)
                   ]
    
    if self.instance.grid_connection.value:
        grid += 1
        labels.append("Grid Energy")
        connections.append((3+grid,3, sum(self.instance.time_duration[t]*self.instance.energy_grid[t].value for t in self.instance.time)/ normaliser))
    
    if self.instance.battery.value:
        battery += 2
        labels.append("Battery Storage")
        connections.append((3+grid+battery-1, 3, sum(self.instance.time_duration[t]*self.instance.energy_battery_out[t].value for t in self.instance.time) / normaliser))
        connections.append((3,3+grid+battery-1,sum(self.instance.time_duration[t]*self.instance.energy_battery_in[t].value for t in self.instance.time) / normaliser))
        labels.append("Battery Inefficiency")
        connections.append((3+grid+battery-1,3+grid+battery,abs(sum(self.instance.time_duration[t]*(self.instance.energy_battery_in[t].value - self.instance.energy_battery_out[t].value)for t in self.instance.time)) / normaliser))

    if self.instance.fuel_cell.value:
        fuel_cell += 2
        labels.append("Fuel Cell")
        connections.append((2+grid+battery+fuel_cell,3,sum(self.instance.time_duration[t]*self.instance.energy_HFC[t].value for t in self.instance.time) / normaliser))
        connections.append((7+grid+battery+fuel_cell-1,3+grid+battery+fuel_cell-1,sum(self.instance.time_duration[t]*self.instance.energy_HFC_flux[t].value for t in self.instance.time)/normaliser))
        labels.append("Fuel Cell Inefficiency")
        connections.append((3+grid+battery+fuel_cell-1,3+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*(self.instance.energy_HFC_flux[t].value - self.instance.energy_HFC[t].value) for t in self.instance.time)/normaliser))
        
    labels.append("Curtailed Energy")
    connections.append((3, 4+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*self.instance.energy_curtailed[t].value for t in self.instance.time)/normaliser))

    labels.append("Electrolysis")
    connections.append((3,5+grid+battery+fuel_cell,sum(sum(self.instance.time_duration[t]*self.instance.energy_electrolysers[k,t].value for k in self.instance.electrolysers) for t in self.instance.time)/normaliser))

    labels.append("Gaseous Hydrogen Storage")
    connections.append((5+grid+battery+fuel_cell,6+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*self.instance.energy_gh2_in_store[t].value for t in self.instance.time)/normaliser))
    connections.append((5+grid+battery+fuel_cell,8+grid+battery+fuel_cell,sum(sum(self.instance.time_duration[t]*self.instance.energy_gh2_use[q,t].value for q in self.instance.vectors) for t in self.instance.time)/normaliser))

    labels.append("Electrolysis Losses")
    connections.append((5+grid+battery+fuel_cell,7+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*(sum(self.instance.energy_electrolysers[k,t].value for k in self.instance.electrolysers) - self.instance.energy_gH2_flux[t].value) for t in self.instance.time)/normaliser))

    labels.append("Vector Production")
    connections.append((3, 8+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_penalty_vector_production[q,t].value for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    connections.append((6+grid+battery+fuel_cell,8+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.energy_gh2_rem[q,t].value for q in self.instance.vectors) for t in self.instance.time)/normaliser+sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.bol_energy_penalty[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser))

    labels.append("Origin Vector Storage")
    connections.append((8+grid+battery+fuel_cell,9+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser))
    
    labels.append("Fugitive Loss")
    connections.append((8+grid+battery+fuel_cell,10+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*(1-self.instance.vector_fugitive_efficiency[q]) for q in self.instance.vectors) for t in self.instance.time)/ normaliser))

    labels.append("Vector Production Efficiency Loss")
    connections.append((8+grid+battery+fuel_cell, 11+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_penalty_vector_production[q,t].value for q in self.instance.vectors) for t in self.instance.time)/normaliser))

    labels.append("Shipping")
    connections.append((9+grid+battery+fuel_cell,12+grid+battery+fuel_cell, sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser))
    
    labels.append("Shipping Fuel")
    connections.append((12+grid+battery+fuel_cell,13+grid+battery+fuel_cell,(self.instance.journey_time  * 2 * sum(sum(sum(self.instance.time_duration[t]*self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time) * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser ))

    labels.append("Destination Vector Storage")
    connections.append((12+grid+battery+fuel_cell,14+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time)* self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser - sum(self.instance.time_duration[t]*sum(self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    
    if self.instance.reconversion:
        labels.append("Reconversion")
    else:
        labels.append("Demand")
    connections.append((14+grid+battery+fuel_cell,15+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time) * self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser - sum(self.instance.time_duration[t]*sum(self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    
    labels.append("Compression")
    connections.append((3,16+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*self.instance.energy_compression[t].value for t in self.instance.time) / normaliser))

    labels.append("Transmission Loss")
    connections.append((1,17+grid+battery+fuel_cell,(1-self.instance.turbine_efficiency)*sum(self.instance.time_duration[t]*self.instance.capacity_number_turbines.value * self.instance.turbine_power[t] for t in self.instance.time) / normaliser))

    labels.append("Compression Parasitic Loss")
    connections.append((5+grid+battery+fuel_cell,18+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*self.instance.energy_gH2_flux[t].value * (1-self.instance.compressor_effiency) for t in self.instance.time)/normaliser))

    if self.instance.reconversion:
        conversion += 1
        labels.append("Delivered H2")
        conversion += 1
        labels.append("Reconversion Loss")
        #connections.append((15+grid+battery+fuel_cell,18+conversion+grid+battery+fuel_cell, (sum(self.instance.time_duration[t]*sum((1-self.instance.reconversion_efficiency[q]) * self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*(1-self.instance.reconversion_efficiency[q]) *self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time)* self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser) - sum(self.instance.time_duration[t]*sum((1-self.instance.reconversion_efficiency[q])*self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))
        #connections.append((15+grid+battery+fuel_cell,17+conversion+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time) * self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser - sum(self.instance.time_duration[t]*sum(self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser - (sum(self.instance.time_duration[t]*sum((1-self.instance.reconversion_efficiency[q]) * self.instance.energy_vector_production_flux[q,t].value*self.instance.vector_fugitive_efficiency[q] for q in self.instance.vectors) for t in self.instance.time) / normaliser - (sum(sum(sum(self.instance.time_duration[t]*(1-self.instance.reconversion_efficiency[q]) *self.instance.number_ships_discharging[j,q,t].value for t in self.instance.time)* self.instance.journey_time  * 2 * self.instance.ship_fuel_consumption[j,q] for j in self.instance.ships) * self.instance.vector_calorific_value[q] for q in self.instance.vectors) / self.instance.loading_time) / normaliser) - sum(self.instance.time_duration[t]*sum((1-self.instance.reconversion_efficiency[q])*self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q] for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))
        connections.append((15+grid+battery+fuel_cell,17+conversion+grid+battery+fuel_cell,sum(self.instance.demand_signal[t]*self.instance.time_duration[t] for t in self.instance.time)/normaliser))
        connections.append((15+grid+battery+fuel_cell,18+conversion+grid+battery+fuel_cell,sum(sum(self.instance.energy_vector_consumption_flux[q,t].value*self.instance.time_duration[t]*((1-self.instance.reconversion_efficiency[q])/self.instance.reconversion_efficiency[q]) for t in self.instance.time) for q in self.instance.vectors)/normaliser))

    labels.append("Vector Production Synthetic Loss")
    connections.append((8+grid+battery+fuel_cell,19+conversion+grid+battery+fuel_cell,(sum(self.instance.time_duration[t]*sum((1-self.instance.vector_synthetic_efficiency[q])*(self.instance.energy_vector_production_flux[q,t].value / self.instance.vector_synthetic_efficiency[q])for q in self.instance.vectors) for t in self.instance.time)/normaliser)))
    
    labels.append("Waiting Ship BOL")
    connections.append((14+grid+battery+fuel_cell,20+conversion+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.bol_rate[q] * sum((self.instance.number_ships_destination[j,q,t].value - self.instance.number_ships_discharging[j,q,t].value)*self.instance.ship_storage_capacity[j,q]for j in self.instance.ships) for q in self.instance.vectors) for t in self.instance.time)/normaliser))

    labels.append("BOL Management")
    labels.append("BOL Management Penalty")
    connections.append((21+conversion+grid+battery+fuel_cell,22+conversion+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.bol_energy_penalty[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    connections.append((21+conversion+grid+battery+fuel_cell,8+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.vector_calorific_value[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    connections.append((8+grid+battery+fuel_cell,21+conversion+grid+battery+fuel_cell,sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.vector_calorific_value[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser+sum(self.instance.time_duration[t]*sum(self.instance.vector_storage_origin[q,t].value*self.instance.bol_rate[q]*self.instance.bol_energy_penalty[q]*1000 for q in self.instance.vectors) for t in self.instance.time)/normaliser))
    
    fig = Figure(data=[Sankey(
            arrangement='freeform',
            node = dict(
            pad = 30,
            thickness =15,
            line = dict(color = "black", width = 0.2),
            label = labels,           #22
            color=self.custom_cmap),
            link = dict(
            source = list(map(lambda x: x[0], connections)), # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = list(map(lambda x: x[1], connections)),
            value = list(map(lambda x: 0 if x[2] <= threshold else x[2], connections)),
            color=['#708090']*50
        ))])

    fig.update_layout(title_text="Supply Chain Sankey Diagram",
                      font_family="Times New Roman",
                      font_color="black",
                      font_size=16,
                      title_font_family="Times New Roman",
                      title_font_color="black",
                      )
    
    fig.update_layout( autosize=False, width=1350, height=height)
    fig.show(scale=6)
    pass