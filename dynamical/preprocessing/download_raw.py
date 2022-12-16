"""Module reaching ENTSO-E server and downloading data"""

import pandas as pd
import numpy as np
from time import time
from datetime import datetime, timedelta
import os
import paramiko
from functools import partial
from getpass import getpass

# +

#################
#################
# ## Download
##############

# -


def download(config, is_verbose=False):
    """Downloads data from ENTSO-E servers and save it.

    Parameters
    ----------
        config: dynamical.Parameter
            collection of parameters for the execution of dynamical.
            The relevant information is the start and end date, as well
            as server information and path information to save raw_generation
            and raw_exchange.
        is_verbose: bool, default to False
            to display information during the download

    Returns
    -------
    None
    """
    t0 = time()
    ### Get the start and end dates
    dates = _set_time(config.start, config.end)
    
    ### Decide on the files to download
    file_list = {k: _get_file_list(*dates, getattr(configserver, f'_remote{k}Dir'),
                                          getattr(configserver, f'_name{k}File') )
                 for k in ['Generation','Exchanges']}
    
    ### Point to the saving locations
    save_list = {k: _get_file_list(*dates, getattr(configpath, f'raw_{k.lower()}'),
                                          getattr(configserver, f'_name{k}File') )
                 for k in file_list}
    
    ### Clear directories
    if configserver.removeUnused:
        _remove_olds(configpath.raw_generation, save_list['Generation']) # Remove unused generation
        _remove_olds(configpath.raw_exchanges, save_list['Exchanges']) # Remove unused exchanges
        
    ### Download files
    _reach_server(configserver, files=file_list, savepaths=save_list, is_verbose=is_verbose)
    
    ### EOF
    if is_verbose: print(f"\tDownload from server: {time()-t0:.2f} sec" + " "*40)
    return

# +

#################
#################
# ## Reach Server
##############

# -

    
def _reach_server(server_info, files, savepaths, is_verbose=False):
    """Function establishing the connection with the server using credentials
    , collecting files and saving them. Nothing is returned.
    """
    
    ### Create the connection
    if is_verbose: print("Connection...", end='\r')
    
    ### Connexion loop
    password = server_info.password # Get the password from parameters
    if server_info.password is None:
        password = _manage_password()
    
    is_valid, safety_loop = False, 1
    while not is_valid:
        transport = paramiko.Transport( (server_info.host, server_info.port) )
        try:
            transport.connect(username=server_info.username, password = password)
            is_valid = True # Success
        except paramiko.AuthenticationException as authentication_error:
            if safety_loop==0:
                message = "Connection failed. Your password may be outdated. "
                message += "Please verify by logging in at https://transparency.entsoe.eu/"
                print(message)
                raise paramiko.AuthenticationException(message)
            else:
                print("Error in Password or Username. Connection failed.")
                safety_loop-=1 # One chance less
                transport.close() # Close the transport
                #del transport
                password = _manage_password() # New try for password
    
    ### Create a data pipe between local and remote
    if is_verbose: print("Create pipe...", end='\r')
    with paramiko.SFTPClient.from_transport(transport) as sftp:
        ### Download all files
        for categ in files: # Generation then Exchanges
            for i, (remote,local) in enumerate(zip(files[categ],savepaths[categ])): # For each file
                if not _should_download(sftp, remote, local): continue;
                
                callback_fct = None
                if is_verbose:
                    callback_fct = partial(_progressBar, info=f"{categ} {i+1}/{len(files[categ])}")
                
                sftp.get(remotepath=remote, localpath=local,
                         callback=callback_fct)
    
    ### Close the connection to transport (already done for sftp)
    transport.close()
    ### EOF

# +

#################
#################
# ## Set Time
##############

# -
    

def _set_time(start,end):
    """Set the list of year-month to target the files to download.
    If start is None: start of previous month or 2 months before end.
    If end is None: now.
    """
    
    if None not in [start, end]: # Regular method
        all_months = pd.period_range(start=start, end=end, freq='M', periods=None)
    elif ((start is None) & (end is None)): # Both -> 2months before now
        all_months = pd.period_range(start=start, end=datetime.utcnow(), freq='M', periods=2)
    elif end is None: # Start but no end: until now
        all_months = pd.period_range(start=start, end=datetime.utcnow(), freq='M', periods=None)
    elif start is None: # End but no start -> 2 months before end
        all_months = pd.period_range(start=start, end=end, freq='M', periods=2)
        
    return all_months.year, all_months.month

# +

#################
#################
# ## Get File List
##############

# -


def _get_file_list(years, months, path, rootName):
    """Create the list of files to download from the server,
    with exact names.
    """
    return [f"{path}{y}_{m:02d}_{rootName}"
            for y,m in zip(years, months)]

# +

#################
#################
# ## Manage Password
##############

# -
    

def _manage_password():
    """Asks the user to give a password.

    ENTSO-E requires the password to be changed once in a while,
    it might just have expired. If the correct password is not valid
    anymore, visit https://transparency.entsoe.eu/ to login and reset.
    """
    return getpass("Password: ")

# +

#################
#################
# ## Should Download
##############

# -
    
    
def _should_download(sftp, remote, local, threshold_minutes=15, threshold_size=.1):
    """Investigates whether to download a file or not.

    Parameters
    ----------
        sftp
            the connexion to server
        remote: str
            name of the remote file
        local: str
            local version of the file name, if it were to exist
        thershold_minutes: int, default to 15
            time in minutes. Maximum time between last download and
            last remote unpdate to not download the file.
        threshold_size: float, default to 0.1
            maximum ratio of size difference between local and remote file
            to not download, if the last download is newer than `threshold_minutes`.

    Returns
    -------
    bool
        True if
            - the file does not exist in the local target directory OR
            - the remote file is newer than `threshold_minutes` after download of the local file
            - the local file is smaller in size than `threshold_size` of the remote file's size.
    """
    ### IF NO LOCAL FILE ALREADY, DOWNLOAD.
    if not os.path.isfile(local):
        return True
    
    ### IF REMOTE FILE IS NEWER THAN LOCAL, DOWNLOAD.
    remote_mtime = datetime.fromtimestamp( getattr(sftp.lstat(remote), 'st_mtime') )
    local_mtime = datetime.fromtimestamp( getattr(os.stat(local), 'st_mtime') )
    delta_utc = datetime.utcnow()-datetime.now() # Server is in UTC. Local files are in local time.
    is_newer = ( remote_mtime - (local_mtime+delta_utc) ) > timedelta(minutes=threshold_minutes)
    if is_newer: return True

    ### IF REMOTE IS (SIGNIFICANTLY) LARGER, DOWNLOAD
    remote_size = getattr(sftp.lstat(remote), 'st_size') # Size of remote document
    local_size = getattr(os.stat(local), 'st_size') # Size of local document
    is_larger = ((remote_size-local_size)/remote_size) > threshold_size
    if is_larger: return True
    
    ### OTHER CASES: DO NOT DOWNLOAD
    return False

# +

#################
#################
# ## Remove Old Files
##############

# -
    

def _remove_olds(path, local_list):
    """Clears unused files in local directory"""
    remove_list = [path+f for f in os.listdir(path) if ((f not in local_list)&(os.path.isfile(path+f)))]
    for f in remove_list:
        os.remove(f) # Delete the file
    #EOF

# +

#################
#################
# ## Progress Bar
##############

# -

    
def _progressBar(transferred, toBeTransferred, info):
    """Display a progress bar during the download"""
    print(f"[{info}] Transferred: {transferred/1024**2:.1f} MB\tOut of: {toBeTransferred/1024**2:.1f}"+" "*10, end="\r")
