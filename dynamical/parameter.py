# +
import numpy as np
import pandas as pd
import os




# +
## Parameter
# -

class Parameter():
    """Parameter object adapted to the execution of the algorithm.
    
    Attributes:
        - path: FilePath object containing information about path to different documents.
        - ctry: the (sorted) list of countries to include
        - target: the target country where to compute the mix and impact.
        - start: starting date (utc)
        - end: ending date (utc)
        - freq: the time step (15min, 30min, H, d, W, M or Y)
        - timezone: the timezone to convert in, in the end
        - cst_imports: boolean to consider a constant impact for the imports
        - sg_imports: boolean to replace Entso exchanges by SwissGrid exchanges
        - net_exchanges: boolean to consider net exchanges at each border (no bidirectional)
        - residual_local: to include a residual (for CH) as if it was all consumed in the country.
        - residual_global: to include a residual (for CH) that can be exchanged.
    
    Methods:
        - from_excel: to load parameters from a excel sheet
        - __setattr__: to allow simple changes of parameter values.
                    + easy use: parameter_object.attribute = new_value
                    + start and end remain datetimes even if strings are passed
                    + ctry remain a sorted list even if an unsorted list is passed
    """
    
    def __init__(self):
        self.path = Filepath()
        
        self.ctry = sorted(["CH","FR","IT","DE","CZ","AT"])
        self.target = "CH"
        
        self.start = pd.to_datetime("2017-02-01 00:00", yearfirst=True) # first considered date
        self.end = pd.to_datetime("2017-02-01 23:00", yearfirst=True) # last considered date
        self.freq = 'H'
        self.timezone = 'CET'
        
        self.cst_imports = False
        self.sg_imports = False
        self.net_exchanges = False
        self.network_losses = False
        self.residual_local = False
        self.residual_global = False
        
    def __repr__(self):
        text = {}
        attributes = ["ctry","target","start","end","freq","timezone","cst_imports","net_exchanges",
                      "network_losses","sg_imports", "residual_local", "residual_global"]
        for a in attributes:
            text[a] = getattr(self, a)
        
        return "\n".join( [f"{a} --> {text[a]}" for a in text] ) + f"\n{self.path}"
    
    def _dates_from_excel(self, array):
        adapt = lambda x: ("0" if x<10 else "") + str(x)
        date = array.fillna(0)
        if date.sum()==0: return None
        return "{0}-{1}-{2} {3}:{4}".format(*date.apply(adapt).values)
    
    def _set_to_None(self):
        attributes = [a for a in dir(self) if ((a[0]!="_")&(not callable( getattr(self, a) )))]
        for a in attributes:
            if np.all( pd.isna(getattr(self, a)) ): setattr( self, a, None )
                
    def _set_bool(self, value):
        if pd.isna(value):
            return None
        else:
            return bool(value)
        
    def __setattr__(self, name, value):
        if name in ['start','end']:
            super().__setattr__(name, pd.to_datetime(value, yearfirst=True)) # set as time
        elif name == 'ctry':
            super().__setattr__(name, sorted(value)) # always keep sorted
        elif ((name == 'frequency') & (value in ['Y','M'])): # Start of Month or Year only.
            super().__setattr__(name, value+"S")
        else:
            super().__setattr__(name, value) # otherwise just set value
    
    def from_excel(self, excel):
        param_excel = pd.read_excel(excel, sheet_name="Parameter", index_col=0, header=None, dtype='O')
        

        self.ctry = np.sort(param_excel.loc["countries"].dropna().values)
        self.target = param_excel.loc['target'].iloc[0]
        
        self.start = self._dates_from_excel(param_excel.loc['start'])
        self.end = self._dates_from_excel(param_excel.loc['end'])
        self.freq = param_excel.loc['frequency'].iloc[0]
        self.timezone = param_excel.loc['timezone'].iloc[0]

        self.cst_imports = self._set_bool(param_excel.loc['constant exchanges'].iloc[0])
        self.sg_imports = self._set_bool(param_excel.loc['exchanges from swissGrid'].iloc[0])
        self.net_exchanges = self._set_bool(param_excel.loc['net exchanges'].iloc[0])
        self.network_losses = self._set_bool(param_excel.loc['network losses'].iloc[0])
        self.residual_local = self._set_bool(param_excel.loc['residual local'].iloc[0])
        self.residual_global = self._set_bool(param_excel.loc['residual global'].iloc[0])

        
        self.path = self.path.from_excel(excel)
        
        self._set_to_None()
        return self


# +
## Filepath
# -

class Filepath():
    """Filepath object adapted to the execution of the algorithm and the Parameter class.
    
    Attributes:
        - rootdir: root directory of the experiment (highest common folder).
                Useful mainly within the class
        - generation: directory containing Entso generation files
        - exchanges: directory containing Entso cross-border flow files
        - savedir: directory where to save the results. Default: None (no saving)
        - savgen: directory where to save generation from raw files. Default: None (no saving)
        - saveimp: directory to save exchange from raw files. Default: None (no saving)
        - mapping: file with the mapping (impact per kWh produced for each production unit)
        - neighbours: file gathering the list of neighbours of each european country
        - gap: file with estimations of the nature of the residual
        - swissGrid: file with production and cross-border flows from Swiss Grid
        - networkLosses: file with estimation of the power grid losses.
    
    Methods:
        - from_excel: load the attributes from a excel sheet.
    """
    def __init__(self):
        
        self.generation = None
        self.exchanges = None
        self.raw_generation = None
        self.raw_exchanges = None
        self.savedir = None
        self.savegen = None
        self.saveimp = None
        
        self.mapping = None
        self.neighbours = None
        self.gap = None
        self.swissGrid = None
        self.networkLosses = None
        
    def __repr__(self):
        attributes = ["generation","exchanges","raw_generation","raw_exchanges","savedir",
                      "savegen","saveimp","mapping","neighbours","gap","swissGrid",
                      "networkLosses"]
        text = ""
        for a in attributes:
            text += f"Filepath to {a} --> {getattr(self, a)}\n"
        return text
    
    def __setattr__(self, name, value):
        if pd.isna(value):
            super().__setattr__(name, None) # set an empty info
        elif os.path.isdir(r"{}".format(value)):
            super().__setattr__(name, os.path.abspath(r"{}".format(value))+"/")
        elif os.path.isfile(r"{}".format(value)):
            super().__setattr__(name, os.path.abspath(r"{}".format(value)))
        else:
            raise ValueError(f'Unidentified file or directory: {os.path.abspath(value)}')
    
    def from_excel(self, excel):
        param_excel = pd.read_excel(excel, sheet_name="Filepath", index_col=0, header=None)
        
        self.generation = param_excel.loc['generation directory'].iloc[0]
        self.exchanges = param_excel.loc['exchange directory'].iloc[0]
        self.raw_generation = param_excel.loc['raw generation directory'].iloc[0]
        self.raw_exchanges = param_excel.loc['raw exchange directory'].iloc[0]
        self.savedir = param_excel.loc['saving directory'].iloc[0]
        self.savegen = param_excel.loc['saving generation'].iloc[0]
        self.saveimp = param_excel.loc['saving exchanges'].iloc[0]
        
        self.mapping = param_excel.loc['mapping file'].iloc[0]
        self.neighbours = param_excel.loc['neighboring file'].iloc[0]
        self.gap = param_excel.loc['gap file'].iloc[0]
        self.swissGrid = param_excel.loc['file swissGrid'].iloc[0]
        self.networkLosses = param_excel.loc['file grid losses'].iloc[0]
        
        return self
