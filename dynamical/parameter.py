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
        - data_cleaning:to enable automatic data cleaning / filling
    
    Methods:
        - from_excel: to load parameters from a excel sheet
        - __setattr__: to allow simple changes of parameter values.
                    + easy use: parameter_object.attribute = new_value
                    + start and end remain datetimes even if strings are passed
                    + ctry remain a sorted list even if an unsorted list is passed
    """
    
    def __init__(self, excel=None):
        self.path = Filepath()
        self.server = Server()
        
        self.ctry = sorted(["CH","FR","IT","DE","CZ","AT"])
        self.target = "CH"
        
        self.start = pd.to_datetime("2017-02-01 00:00", yearfirst=True) # first considered date
        self.end = pd.to_datetime("2017-02-01 23:00", yearfirst=True) # last considered date
        self.freq = 'H'
        self.timezone = 'UTC'
        
        self.cst_imports = False
        self.sg_imports = False
        self.net_exchanges = False
        self.network_losses = False
        self.residual_local = False
        self.residual_global = False
        self.data_cleaning = True
        
        if excel is not None: # Initialize with an excel file
            self.from_excel(excel)
        
    def __repr__(self):
        text = {}
        attributes = ["ctry","target","start","end","freq","timezone","cst_imports","net_exchanges",
                      "network_losses","sg_imports", "residual_local", "residual_global", 'data_cleaning']
        for a in attributes:
            text[a] = getattr(self, a)
        
        return ( "\n".join( [f"{a} --> {text[a]}" for a in text] )
                + f"\n\n{self.path} \n{self.server}" )
    
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
        elif ((name in ['freq','frequency']) & (value in ['Y','M'])): # Start of Month or Year only.
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
        self.data_cleaning = self._set_bool(param_excel.loc['data cleaning'].iloc[0])

        
        self.path = self.path.from_excel(excel)
        self.server = self.server.from_excel(excel)
        
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
        - generation: directory containing Entso generation files OR where to save it (if from raw)
        - exchanges: directory containing Entso cross-border flow files OR where to save it (if from raw)
        - raw_generation: directory containing raw Entso generation files
        - raw_exchanges: directory containing raw Entso cross-border flow files
        - savedir: directory where to save the results. Default: None (no saving)
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
        
        self.fu_vector = None
        self.mapping = None
        self.neighbours = None
        self.gap = None
        self.swissGrid = None
        self.networkLosses = None
        
    def __repr__(self):
        attributes = ["generation","exchanges","raw_generation","raw_exchanges","savedir",
                      "fu_vector","mapping","neighbours","gap","swissGrid",
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
        
        self.fu_vector = param_excel.loc['FU vector'].iloc[0]
        self.mapping = param_excel.loc['mapping file'].iloc[0]
        self.neighbours = param_excel.loc['neighboring file'].iloc[0]
        self.gap = param_excel.loc['gap file'].iloc[0]
        self.swissGrid = param_excel.loc['file swissGrid'].iloc[0]
        self.networkLosses = param_excel.loc['file grid losses'].iloc[0]
        
        return self



# +
## SERVER
# -

class Server():
    """Server object allowing to parametrize the automatic downloading of data files.
    
    Attributes:
    
    Methods:
    """
    def __init__(self):
        # Root of file names on server
        self._nameGenerationFile = "AggregatedGenerationPerType_16.1.B_C.csv"
        self._nameExchangesFile = "PhysicalFlows_12.1.G.csv"
        
        # Directory with files
        self._remoteGenerationDir = "/TP_export/AggregatedGenerationPerType_16.1.B_C/"
        self._remoteExchangesDir = "/TP_export/PhysicalFlows_12.1.G/"
        
        # Information about the server connection
        self.useServer = False
        self.removeUnused = False
        self.host = "sftp-transparency.entsoe.eu"
        self.port = 22
        
        # Connection login
        self.username = None
        self.password = None # Preferable to ask for it. May be interesting to store if we can encrypt.
        
        
    def __repr__(self):
        attributes = ['useServer','host','port','username','password','removeUnused',
                      '_remoteGenerationDir','_remoteExchangesDir']
        text = ""
        for a in attributes:
            if a!='password': text += f"Server for {a} --> {getattr(self, a)}\n"
            elif isinstance( getattr(self, a), str ): text += f"Server for {a} --> {'*'*len(a)}\n"
            else: text += f"Server for {a} --> \n"
        return text
    
    def __setattr__(self, name, value):
        if pd.isna(value):
            if name in ['useServer','removeUnused']:
                super().__setattr__(name, False) # set False
            else: super().__setattr__(name, None) # set an empty info
        elif name in ['useServer','removeUnused']:
            if value in ['False','No','',' ','-','/']:
                super().__setattr__(name, False)
            else: super().__setattr__(name, value)
        else:
            super().__setattr__(name, value) # Set the value
        
    
    def from_excel(self, excel):
        param_excel = pd.read_excel(excel, sheet_name="Server", index_col=0, header=None)
        
        self.host = param_excel.loc['host'].iloc[0]
        self.port = param_excel.loc['port'].iloc[0]
        self.username = param_excel.loc['username'].iloc[0]
        self.password = param_excel.loc['password'].iloc[0]
        self.useServer = param_excel.loc['use server'].iloc[0]
        self.removeUnused = param_excel.loc['remove unused'].iloc[0]
        
        return self
