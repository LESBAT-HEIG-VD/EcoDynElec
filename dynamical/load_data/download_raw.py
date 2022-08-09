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


def download(p, is_verbose=False):
    t0 = time()
    ### Get the start and end dates
    dates = _set_time(p.start, p.end)
    
    ### Decide on the files to download
    file_list = {k: _get_file_list(*dates, getattr(p.server, f'_remote{k}Dir'),
                                          getattr(p.server, f'_name{k}File') )
                 for k in ['Generation','Exchanges']}
    
    ### Point to the saving locations
    save_list = {k: _get_file_list(*dates, getattr(p.path, f'raw_{k.lower()}'),
                                          getattr(p.server, f'_name{k}File') )
                 for k in file_list}
    
    ### Clear directories
    if p.server.removeUnused:
        _remove_olds(p.path.raw_generation, save_list['Generation']) # Remove unused generation
        _remove_olds(p.path.raw_exchanges, save_list['Exchanges']) # Remove unused exchanges
        
    ### Download files
    _reach_server(p.server, files=file_list, savepaths=save_list, is_verbose=is_verbose)
    
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
    all_months = pd.period_range(start, end, freq='M')
    return all_months.year, all_months.month

# +

#################
#################
# ## Get File List
##############

# -


def _get_file_list(years, months, path, rootName):
    return [f"{path}{y}_{m:02d}_{rootName}"
            for y,m in zip(years, months)]

# +

#################
#################
# ## Manage Password
##############

# -
    

def _manage_password():
    """Verifies if something is available:
    1. As argument
    2. In a local file
    3. Ask the user
    4. Ask if we want to save... (see rsa package)
    DON'T FORGET ENTSO-E REQUESTS TO CHANGE THE
    PASSWORD SOMETINES... IT MUST BE POSSIBLE EASILY"""
    return getpass("Password: ") #raise NotImplementedError()

# +

#################
#################
# ## Should Download
##############

# -
    
    
def _should_download(sftp, remote, local, threshold_minutes=15, threshold_size=.1):
    """Investigates whether to download a file or not
    (if already exists and not newer)"""
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
    print(f"[{info}] Transferred: {transferred/1024**2:.1f} MB\tOut of: {toBeTransferred/1024**2:.1f}"+" "*10, end="\r")