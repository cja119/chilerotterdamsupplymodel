from pyomo.environ import AbstractModel, Objective, minimize, SolverFactory
from OptimisationScripts.OptimisationParameters import generate_parameters
from OptimisationScripts.OptimisationInequalities import generate_inequalities, objective_function
from OptimisationScripts.OptimisationVariables import generate_variables
from OptimisationScripts.OptimisationPlots import demand_and_wind_energy,hydrogen_production,hydrogen_storage_tank_level,origin_storage_tank_levels,destination_storage_tank_levels,vector_production,LCOH_contributions,sankey_diagram
from matplotlib import rcParams
from os import getcwd,chdir
from pickle import dump,load

class OptimModel:
    instance = None

    def __init__(self,parameters,key):
        self.key=key
        self.setup_model(parameters)
        self.generate_objective_function()
        self.build_model()
        pass

    
    def setup_model(self,parameters):
        self.model = AbstractModel()
        generate_parameters(self,parameters)
        generate_variables(self,parameters)
        generate_inequalities(self)
        pass
    
    def generate_objective_function(self):
        self.model.LCOH = Objective(rule=objective_function,sense=minimize)
        pass

    def build_model(self):
        self.instance = self.model.create_instance()
        dir = getcwd()
        chdir(dir+'/PreSolvedModels')
        open(self.key+'.pickle', 'a').close()
        with open(self.key+'.pickle', 'wb') as f:
            dump(self.instance, f)
        chdir(dir)  
        pass
    
    def solve(self,unbounded = False, feasibility = 1e-6, optimality = 1e-8,mip_percentage = 5, random_seed = 42,solver='gurobi',key=None):
            dir = getcwd()
            if self.instance is None:
                chdir(dir+'/PreSolvedModels')
                with open(key+'.pickle', 'rb') as f:
                    self.instance = load(f)
                    self.key = key
                chdir(dir)
            chdir(dir+'/SolverLogs')
            self.solver = SolverFactory(solver)
            self.solver.options['FeasibilityTol'] = feasibility
            self.solver.options['Seed'] = random_seed
            self.solver.options['OptimalityTol'] = optimality
            self.solver.options['MIPGap'] = mip_percentage/100
            self.solver.options['LogToConsole'] = 1  
            self.solver.options['BarHomogeneous'] = 1 
            self.solver.options['LogFile'] = self.key+'.log'
            self.results = self.solver.solve(self.instance,tee=True)
            self.results.write()
            chdir(dir)
            chdir(dir+'/SolvedModels')
            open(self.key+'.pickle', 'a').close()
            with open(self.key+'.pickle', 'wb') as f:
                dump(self.instance, f)
            chdir(dir) 
            pass

    @classmethod
    def class_solve(cls,unbounded = False, feasibility = 1e-6, optimality = 1e-8,mip_percentage = 5, random_seed = 42,solver='gurobi',key=None,parallel=False):
            dir = getcwd()
            if cls.instance is None:
                chdir(dir+'/PreSolvedModels')
                with open(key+'.pickle', 'rb') as f:
                    cls.instance = load(f)
                    cls.key = key
                chdir(dir)
            chdir(dir+'/SolverLogs')
            cls.solver = SolverFactory(solver)
            cls.solver.options['FeasibilityTol'] = feasibility
            if parallel:
                cls.solver.options['Threads'] = 32
                cls.solver.options['DistributedMIPJobs'] = 7
            cls.solver.options['Seed'] = random_seed
            cls.solver.options['OptimalityTol'] = optimality
            cls.solver.options['MIPGap'] = mip_percentage/100
            cls.solver.options['LogToConsole'] = 1  
            cls.solver.options['BarHomogeneous'] = 1 
            cls.solver.options['LogFile'] = cls.key+'.log'
            cls.results = cls.solver.solve(cls.instance,tee=True)
            cls.results.write()
            chdir(dir)
            chdir(dir+'/SolvedModels')
            open(cls.key+'.pickle', 'a').close()
            with open(cls.key+'.pickle', 'wb') as f:
                dump(cls.instance, f)
            chdir(dir) 
            pass

    @classmethod
    def get_solve(cls,key,reinitialise = False):
        dir = getcwd()
        if cls.instance is None or reinitialise is True:
            chdir(dir+'/SolvedModels')
            with open(key+'.pickle', 'rb') as f:
                cls.instance = load(f)
                cls.key = key
        chdir(dir)
        return cls

    def generate_plots(self,
                       all=True,
                       demand = False,
                       storage_tanks = False,
                       conversion_process = False,
                       electrolyser_production = False,
                       LCOH = False,
                       sankey=False,
                       quality = 150,
                       sankey_threshold=10**(-4),
                       sankey_height = 937.5,
                       LCOH_threshold = 0.05):

        # Initializing some global matplotilb parameters
        rcParams['font.family'] = 'serif'
        rcParams['font.serif'] = ['CMU Serif'] + rcParams['font.serif']
        rcParams['figure.dpi'] = quality
        
        # These colours are imperial's new brand colours... using these for plots
        colors =  ["#232333",
                "#000080",
                    "#0000CD",
                    "#008080",
                    "#232333", 
                    "#C71585", 
                    "#DC143C", 
                    "#006400",
                    "#40E0D0", 
                    "#EE82EE",
                    "#7B68EE", 
                    "#FF0000",
                    "#FF8C00", 
                    "#00FF7F", 
                    "#F5F5F5", 
                    "#00BFFF",
                    "#F0E68C",
                    "#AFEEEE",
                    "#FFB6C1",
                    "#E6E6FA", 
                    "#FA8072", 
                    "#FFA500", 
                    "#98FB98"
                    ]
        # Setting other global parameters relating to line_width
        self.alpha          = 0.75
        self.custom_cmap    = colors
        self.linewidth      = 1.25

        # Generating the plots, in accordance with user chosen boolean values
        if demand or all:
            demand_and_wind_energy(self)
        if storage_tanks or all:
            hydrogen_storage_tank_level(self)
            origin_storage_tank_levels(self)
            destination_storage_tank_levels(self)
        if conversion_process or all:
            vector_production(self)
        if electrolyser_production or all:
            hydrogen_production(self)
        if LCOH or all:
            LCOH_contributions(self,LCOH_threshold)
        if sankey or all:
            sankey_diagram(self,sankey_threshold,sankey_height)
        pass
        
