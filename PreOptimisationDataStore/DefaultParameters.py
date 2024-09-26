
class Default_Params:
    def __init__(self):
        self.efficiencies = {'turbine':(0.95,0.97,0.99),                # Assumed 3% loss in transformer losses.
                             'fuel_cell':(0.5,0.6,0.7),                 # Assumed 50% cycle effciciency in fuel cell.
                             'battery_storage':0.9,                     # Assumed 90% cycle efficeincy of battery storage
                             'electrolysers': {'alkaline':(.60,.70,.85),   # Assumed 61.5% energetic efficiency of electrolysers (LHV basis)
                                              'PEM':(.60,.70,.85),         # Assumed 61.5% energetic efficiency of electrolysers (LHV basis)
                                              'SOFC':(.80,.85,.90)
                                              },
                             'hydrogen_storage':0.99,                       # Assumed 1% loss to compression and fittings.
                             'compressor':(0.996,0.995,0.9925),
                             'vector_fugitive':  {'LH2':(0.95,0.984,1),     # Fugitive losses of hydrogen
                                                  'NH3':(0.9,0.95,1)        # High fugitiev loss through purge due to modulation of throughput
                                                  },
                             'vector_synthesis':{'LH2':1,           # This is the energetic efficiency of the reaction (no fugitive losses) on a LHV basis
                                                'NH3':0.888         # This is the energetic efficeicney of the reaction (no fugitive losses) on a LHV basis
                                                },
                             'vector_stoichiometry':{'LH2':1,       # Stoichoimetric ratio of vector production. 
                                                     'NH3':5.67     # Stoichoimetric ratio of vector production. 
                                                     },
                             'reconversion':{'LH2':(0.98,0.99,1),
                                             'NH3':(0.7,0.8,0.85),
                                             },                   
                             'vector_calorific_value':{'LH2':120,   # GJ/t (LHV)
                                                       'NH3':18.8   # GJ/t (LHV) 
                                                       }        
                            }

        self.capital_costs =      {'turbine':(1.4157,2.145,3.2175),                     # M$/turbine.   Aligns with a LCOH for IRENA's lower bound 2050 estimate of $650 per kW.
                                   'fuel_cell':(0.167,0.233,0.2675),                    # M$/(GJ/h).    Taken from 10.1039/d0ee01707h.
                                   'battery_storage':(0.0436,0.0625,0.0964),            # M$/GJ.        National Renewable Energy Laboratory (NREL) Figure.
                                   'electrolysers':{'alkaline': (0.0556,0.0972,0.1389), # M$/(GJ/h).    IRENA
                                                    'PEM':(0.0556,0.1111,0.1944),       # M$/(GJ/h).    IRENA
                                                    'SOFC':(0.0833,0.1389,0.2777)
                                                    },
                                   'compressor':9.8,                                    # M$/(t/h)
                                   'hydrogen_storage': (0.4,0.5,0.635),                 # M$/t.         USDOE value.
                                   'vector_storage': {'LH2': (10,20,30),                # M$/kt.         10.1016/j.ijhydene.2022.06.168
                                                      'NH3': (0.5,1.3,2.72)             # M$/kt.         10.1016/j.ijhydene.2018.06.121
                                                       },
                                   'vector_production': {'LH2': (13.57*24**(2/3),17.55*24**(2/3),25*24**(2/3)),        # M$/(t/h)^(2/3).     IdealHy
                                                         'NH3': (18.86,21.82,26.7)                                        # M$/(t/h).     Ishimoto et al.
                                                        },
                                   'shipping':{('LH2','small'):(101.3,130,158.5),       # M$/ship       Scaled cost of the JAMILA ship
                                                ('LH2','medium'):(203.6,235.1,286.6),   # M$/ship       Scaled cost of the JAMILA ship
                                                ('LH2','large'):(336.8,431,525),        # M$/ship       Scaled cost of the JAMILA ship
                                                ('NH3','small'):(59.0,85.1,97.6),       # M$/ship       Scaled cost of the JAMILA ship (incl NH3 tanks)
                                                ('NH3','medium'):(106.9,153.4,200),   # M$/ship       Scaled cost of the JAMILA ship (incl NH3 tanks)
                                                ('NH3','large'):(196,280,330)           # M$/ship       Scaled cost of the JAMILA ship (incl NH3 tanks)
                                                       ,
                                                },
                                   'reconversion':{'LH2':(1.38,2,3.73),         # M$/(t/h)
                                                  'NH3':(2,2.69,5.7)            # M$/(t/h)   
                                                  },  
                                   'port': 0,  
                                   }

        self.operating_costs =      {'turbine':(0.0429,0.0575,0.0686),                      # M$/t/y.            This is $75,000 per kW reduced by 47% - in line with 2050 estimates.
                                     'fuel_cell':(0.00667,0.00933,0.0107),                           # M$/(GJ/h)/y.       This is 4% of the unit capital cost.
                                     'battery_storage':(0.00108,0.00156,0.00242),           # M$/GJ/y.           This is 2.5% of the unit capital cost. 
                                     'electrolysers':{'alkaline':(0.00111,0.00194,0.00278), # M$/(GJ/h)/y.       This is 2% of the unit capital cost. 
                                                      'PEM':(0.00111,0.00222,0.00389),      # M$/(GJ/h)/y.       This is 2% of the unit capital cost. 
                                                      'SOFC':(0.00167,0.00278,0.00556)
                                                      },              
                                     'compressor':0.196,
                                     'hydrogen_storage': (0.016,0.02,0.0254),               # M$/t/y.        This is 4% of the unit capital cost. 
                                     'vector_storage': {'LH2': (.4,0.8,2.25),               # M$/kt.         10.1016/j.ijhydene.2022.06.168
                                                        'NH3': (0.02,0.052,0.204)           # M$/kt.         10.1016/j.ijhydene.2018.06.121
                                                        },
                                     'vector_production': {'LH2':(0.542,0.702,1),           # M$/(t.p.d)^(2/3)/y.        This is 4% of the unit capital cost. 
                                                           'NH3':(0.7758,0.8728,1.0667)           # M$/(t/h)/y.                This is 4% of the unit capital cost. 
                                                           },
                                     'shipping':{('LH2','small'):(4.05,5.20,6.34),      # M$/ship/y          This is 4% of the unit capital cost. 
                                                  ('LH2','medium'):(8.1,9.4,11.5),    # M$/ship/y          This is 4% of the unit capital cost. 
                                                  ('LH2','large'):(14.5,17.2,21),       # M$/ship/y          This is 4% of the unit capital cost. 
                                                  ('NH3','small'):(2.36,3.4,3,9),       # M$/ship/y          This is 4% of the unit capital cost. 
                                                  ('NH3','medium'):(4.3,6.1,8),      # M$/ship/y          This is 4% of the unit capital cost. 
                                                  ('NH3','large'):(7.8,11.2,13.2)       # M$/ship/y          This is 4% of the unit capital cost. 
                                                 },
                                     'reconversion':{'LH2':(0.069,0.1,0.186),          # M$/(t/h)          Unknown  cost as of yet
                                                     'NH3':(0.18,0.339,0.51)           # M$/(t/h)          This is 4% of the unit capital cost. 
                                                     },
                                     'grid_energy_factor':(1,1.5,2),                   # M$/GJ
                                     'port': 0,
                                    }

        self.replacement_frequencies = {'turbine':25,                         # y
                                        'fuel_cell':10,                       # y
                                        'battery_storage':5,                  # y
                                        'electrolysers': {'alkaline': (9.78,11.42,16.31),      # y
                                                         'PEM':(11.42,13.86,19.6),            # y
                                                         'SOFC':(3.26,9.78,13.04)
                                                         },
                                        'compressor':(7.5,15),
                                        'hydrogen_storage':(20),               # y
                                        'vector_production':{'LH2':30,
                                                             'NH3':30
                                                            },             # y
                                        'ships':{'small':30,
                                                 'medium':30,
                                                 'large':30
                                                 },
                                        'reconversion':{'LH2':30,
                                                        'NH3':30
                                                        },
                                        'vector_storage':{'LH2':20,
                                                          'NH3':20
                                                          },
                                        'system_duration':30
                                        }

        self.vector_production = {'single_train_throughput': {'LH2':(4.17,6.25,10.42),   # t/h/train.   This is 50 t.p.d, from IdealHy.
                                                              'NH3':114  
                                                              },
                                'ramp_up_limit': {'LH2':(0.05,0.2,0.5),       # %/h.          This is an estimate. 
                                                  'NH3':(0.02,0.1,0.25)       # %/h.          This is taken from Hatton et al.
                                                  },
                                'ramp_down_limit': {'LH2':(0.15,0.3,0.5),     # %/h.          This is an estimate.
                                                    'NH3':(0.2,0.25,0.5)      # %/h.          This is taken from Hatton et al.    
                                                    },
                                'fixed_energy_penalty': {'LH2':(0.25,0.4,0.6),       # %.         This is taken from IdealHy. 
                                                         'NH3':(0.25,0.4,0.6)  # %.         
                                                         },
                                'variable_energy_penalty': {'LH2':(17.09,21.6,24.3),   # GJ/t
                                                            'NH3':(0.962,1.826,3.63)   # GJ/t
                                                            },
                                'fractional_energy_penalty': {'LH2':(0.25,0.4,0.6),      # 
                                                              'NH3':(0.25,0.4,0.6)    # %MaxCap
                                                              },
                                'boil_off_energy_penalty': {'LH2':(0.77,0.975,1.05),  # GJ/t.         This is the flash gas recycle for idealhy.
                                                            'NH3':0
                                                            },

                                'boil_off_percentage': {'LH2':(0.001042,0.003125,0.004167),     # %/h.          This corresponds to 0.1% per day. 
                                                        'NH3':0             # 
                                                        },
                                'minimum_train_throughput': {'LH2': (0.25,0.4,0.75),
                                                            'NH3': (0.25,0.4,0.75)
                                                            }
                                }

        self.shipping = {'storage_capacity':{('LH2','small'):3542.5,            # t/d       This corresponds to 50,000 m3
                                            ('LH2','medium'):7085,              # t/d       This corresponds to 100,000 m3
                                            ('LH2','large'):14160,              # t/d       This corresponds to 200,000 m3
                                            ('NH3','small'):32500,              # t/d       This corresponds to 50,000 m3
                                            ('NH3','medium'):65000,             # t/d       This corresponds to 100,000 m3
                                            ('NH3','large'):32500               # t/d       This corresponds to 200,000 m3
                                                },
                        'fuel_consumption':{('LH2','small'):21.5/24*(36/23),    # t/h       This corresponds to 50,000 m3
                                            ('LH2','medium'):34.35/24*(36/23),  # t/h       This corresponds to 100,000 m3
                                            ('LH2','large'):55.1/24*(36/23),    # t/h       This corresponds to 200,000 m3
                                            ('NH3','small'):120.2/24*(36/23),   # t/h       This corresponds to 50,000 m3
                                            ('NH3','medium'):201.2/24*(36/23),  # t/h       This corresponds to 100,000 m3
                                            ('NH3','large'):340/24*(36/23)      # t/h       This corresponds to 200,000 m3
                                            },
                     'journey_time': 360,                                   # hours     This is the time to travel from Chile to Rotterdam
                     'loading_time': 8                                      # hours     This is assumed to be the same for all ships irrespective of capacity. 
                     }
  
        self.miscillaneous = {'reconversion_electrical_demand':{'LH2':0,    # Don't yet have a value
                                                                'NH3':1.44  # GJ/t 
                                                                },
                              'battery_charge_time':4,                      # hours
                              'battery_discharge_time':4,                   # hours
                              'hydrogen_LHV':120,                           # GJ/t
                              'discount_factor':(0.066,0.121,0.14),
                              'electrolyser_compression_energy':{'alkaline':(4.53,5.62,7.58),   # GJ/t
                                                                 'PEM':(3.6,5.2,7.58),          # GJ/t
                                                                 'SOFC':(2.71,4.53,6.13)        # GJ/t
                                                                 },
                              'storage_compression_penalty':4.79,                               #GJ/t
                              'vector_compression_penalty':{'LH2':0,                            #GJ/t(H2)
                                                            'NH3':2.14                          #GJ/t(H2)
                                                            }
                              }    

        self.formulation_parameters = {'shipping_regularity': 168,
                                        'ramping_frequency': 1,
                                        'efficiencies':self.efficiencies,
                                        'capital_costs':self.capital_costs,
                                        'operating_costs':self.operating_costs,
                                        'replacement_frequencies':self.replacement_frequencies,
                                        'vector_production':self.vector_production,
                                        'shipping':self.shipping,
                                        'miscillaneous':self.miscillaneous}
        pass