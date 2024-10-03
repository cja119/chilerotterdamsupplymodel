from MeteorologicalScripts.SampleWeatherData import geospatial_sampling
from MeteorologicalScripts.PlotWeatherData import boxplot
from shapely.geometry import Polygon, Point, shape
from numpy import array, meshgrid, zeros, trapz, asarray, interp
from pandas import DataFrame
import matplotlib.pyplot as plt
from xarray import Dataset
from pyproj import Proj
from math import pi
from os import chdir, getcwd
from pickle import dump, load

def filter_points(coordinates, world_test):

    # Generating a polygon from the coordinates. 
    polygon = Polygon(coordinates)

    # Generating latitude and longitude values.
    latitudes = world_test['lat'].values
    longitudes = world_test['lon'].values

    # Building a meshgrid of these values and flattening it.
    lon_grid, lat_grid = meshgrid(longitudes, latitudes)
    lon_flat = lon_grid.flatten()
    lat_flat = lat_grid.flatten()
    
    # Assembling the points into coordinates
    points = [Point(lat, lon) for lat, lon in zip(lat_flat, lon_flat)]

    # Generating an array boolean based onwhether the coordinates are within the polygon. 
    mask = array([polygon.contains(point) for point in points])
    mask_2d = mask.reshape(lon_grid.shape)

    # Producing filtered points and xarray dataset and returning these as the function output. 
    filtered_latitudes  = lat_grid[mask_2d]
    filtered_longitudes = lon_grid[mask_2d]
    filtered_world_test = world_test.where(mask_2d)

    return filtered_world_test, filtered_latitudes, filtered_longitudes



class RenewableEnergy:
    def __init__(self, meteorological,vertices: list[tuple[float,float],tuple[float,float],tuple[float,float],tuple[float,float]], power_curve, min_radius: float = 100):
        
        self.vertices       = vertices
        self.min_radius     = min_radius  
        if meteorological.wind:
            self.allocate_windfarm(meteorological)
            self.wind_power_output(meteorological,power_curve)
        if meteorological.solar:
            self.allocate_solarfarm(meteorological)

    def allocate_windfarm(self,meteorological, plot: bool = False):
        ''' NB, this sampling only works on convex domains
        
        plot:       Boolean -> Whether a plot of the windfarm is desired. 
        '''

        # Generating ordered lists of vertex coordinates.
        longitudes = (min(list(zip(*self.vertices))[1]), max(list(zip(*self.vertices))[1]))
        latitudes  = (min(list(zip(*self.vertices))[0]), max(list(zip(*self.vertices))[0]))

        # Sampling the data within these coordinates. 
        square_datset = geospatial_sampling(meteorological.wind_data_spatial_temporal, latitudes, longitudes)

        # Filtering these points to turn the square dataset into only points enclosed within the polygon. 
        filtered, lats, lons = filter_points(self.vertices,square_datset)
        
        # Generating a geographic projection of the polygon.
        pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
        x, y = pa(list(zip(*self.vertices))[1], list(zip(*self.vertices))[0])
        cop = {"type": "Polygon", "coordinates": [zip(x, y)]}

        # Plotting, if the boolean plot is set to true.
        if plot:
            boxplot(meteorological, points=list(zip(lats,lons)), just_wind=True,vertices = self.vertices)
        
        # Setting these values as attributes as they can be useful to access later on. 
        self.fitered        = filtered
        self.latitudes      = lats
        self.longitudes     = lons
        self.meanU          = filtered.variables['U10M'].mean(dim=['lat', 'lon'],keep_attrs=True)
        self.meanV          = filtered.variables['V10M'].mean(dim=['lat', 'lon'],keep_attrs=True)
        self.meanspeed      = (filtered.variables['U10M'].mean(dim=['lat', 'lon'],keep_attrs=True)**2 + filtered.variables['U10M'].mean(dim=['lat', 'lon'],keep_attrs=True)**2)**0.5
        self.time           = filtered.variables['time']
        area                = shape(cop).area
        area_km             = area/ 1000000
        self.area           = {'m2': area, 'km2': area_km}
        self.num_turbines   = int((self.area['m2'] * (pi / (2*(3**0.5)))) / (pi*self.min_radius**2))
        pass
    
    def allocate_solarfarm(self,meteorological, plot: bool = False):
        ''' NB, this sampling only works on convex domains

            plot:       Boolean -> Whether a plot of the windfarm is desired. '''
        
        # Generating ordered lists of vertex coordinates.
        longitudes = (min(list(zip(*self.vertices))[1]), max(list(zip(*self.vertices))[1]))
        latitudes  =(min(list(zip(*self.vertices))[0]), max(list(zip(*self.vertices))[0]))

        # Sampling the data within these coordinates.   
        square_datset = geospatial_sampling(meteorological.solar_data_spatial_temporal, latitudes, longitudes)

        # Filtering these points to turn the square dataset into only points enclosed within the polygon. 
        filtered, lats, lons = filter_points(self.vertices,square_datset)

        # Generating a geographic projection of the polygon.
        pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
        x, y = pa(list(zip(*self.vertices))[1], list(zip(*self.vertices))[0])
        cop = {"type": "Polygon", "coordinates": [zip(x, y)]}

        # Plotting, if the boolean plot is set to true.
        if plot:
            boxplot(meteorological, points=list(zip(lats,lons)), just_solar=True,vertices = self.vertices)
        
        # Setting these values as attributes as they can be useful to access later on.      
        self.fitered        = filtered
        self.latitudes      = lats
        self.longitudes     = lons
        self.meanradiation  = filtered.variables['SWTDN'].mean(dim=['lat', 'lon'],keep_attrs=True)
        self.time           = filtered.variables['time']
        area                = shape(cop).area
        area_km             = area/ 1000000
        self.area           = {'m2': area, 'km2': area_km}
        self.num_panels     = int((self.area['m2'] * (pi / (2*(3**0.5)))) / (pi*self.min_radius**2))
        pass

    def wind_power_output(self,meteorological, power_curve_points, temperature_range_k: tuple[float,float] = (248,323),  hub_height: float = 100, hellman_exponent = 0.15):
        '''
        This function generates a temporally indexed wind turbine power output, based on the power curve of a turbine and the temporally indexed wind speed data.

        power_curve_points:     list(tuple[float,float])    -> A list of tuples of (wind speed [m/s], power output). The same power units are output as those input.
        temperature_range_k:    tuple(float,float)          -> The operating temperatuer range of the turbine, in kelvin, lower temperature first.
        hub_height:             float                       -> Height of the turbine's hub [m].
        hellman_exponent        float                       -> Exponent for the wind-speed against height function. 
        '''
        # The below function allows for an interpolation of a wind turbines power curve.

        def power_curve(wind_speed,points):
                
            # Generating an empty array of windspeeds 
            wind_speed  = wind_speed.values
            power       = zeros(len(wind_speed))

            # Iterating over the list of windspeeds in order to generate a list of power outputs. 
            for j in range(len(wind_speed)):
                if wind_speed[j] >= points[-1][0]:
                    power[j] = 0
                else:
                    for i in range(len(points)-1):
                        if wind_speed[j] >= points[i][0] and wind_speed[j] <= points[i+1][0]:
                            power[j] = ((wind_speed[j] - points[i][0]) / (points[i+1][0] - points[i][0])) * (points[i+1][1] - points[i][1]) + points[i][1]
                            break 
            return power

        # Calculating the wind speed at the height of the hub (default MERRA-2 is at 10m). 
        self.wind_speed_hub_height  = self.meanspeed * (hub_height / 10)**hellman_exponent

        # Calculating the turbine power output
        power_output                = power_curve(self.wind_speed_hub_height,power_curve_points)

        # Dropping all values of power output that occur when the ambient temperature is out of the operating range of the turbine.  
        temperature_data            = meteorological.wind_data_spatial_temporal.variables['T10M'].mean(dim=['lat','lon']).values
        conditions                  = [all([ temperature_data[i] >= temperature_range_k[0], temperature_data[i] <= temperature_range_k[1]]) for i in range(len(temperature_data))]
        self.power_output           = power_output[conditions]
        # Calculating a capacity factor for the wind farm. 
        self.capacity_factor        = trapz(self.power_output, dx = meteorological.interval) / (power_curve_points[-1][1] * meteorological.interval * len(self.power_output))
        pass

    def export_power(self,meteorological,name: str, dates=True):
        '''
        This function saves the wind speed data in a csv, if required.

        name:   string      -> Name of the CSV file
        dates:  booolean    -> Choice whether or not the time indices are to be stored in a column, to the left of the wind speed data.
        '''
        if dates:
            data = DataFrame({"Wind Data": self.power_output,"Start Date": meteorological.date_lower,"End Date": meteorological.date_upper})
        else:
            data = DataFrame({"Wind Data": self.power_output})
        data.to_csv(name,sep=' ')
        pass