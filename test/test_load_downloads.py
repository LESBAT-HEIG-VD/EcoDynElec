import unittest

from numpy import all
import paramiko
from getpass import getpass
from datetime import datetime, timedelta

from dynamical.preprocessing import download_raw




class TestDownload(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.pwd = None
        self.transport = None
        self.identify() # Establishes a connexion
        
    
    def identify(self):
        ### Ask for username
        if self.user is None:
            self.user = input("Username: ")
        
        ### Ask for password
        if self.pwd is None:
            ### First try
            pwd = getpass("Password: ")
            transport = self.connect(pwd)
            if not transport:
                print("Error in credentials. Last try before skipping this section.")
                pwd = getpass("Password: ")
                transport = self.connect(pwd)
                if not transport:
                    raise paramiko.AuthenticationException("Password may be outdated. Try to log online.")
            self.pwd = pwd
            self.transport = transport
            
                
    def connect(self, pwd):
        transport = paramiko.Transport( ("sftp-transparency.entsoe.eu", 22) )
        try:
            transport.connect(username=self.user, password=pwd)
            valid = transport
        except paramiko.AuthenticationException:
            transport.close()
            valid = False
        return valid
    
    
    def remoteContent(self, remote_files, expected_filename, case='prod'):
        ### Verify file name structure
        self.assertTrue( all( [f.split("_")[0].isdigit() for f in remote_files] ), msg=f"Cannot find Years in file name {case}" )
        self.assertTrue( all( [f.split("_")[1].isdigit() for f in remote_files] ), msg=f"Cannot find Month in file name {case}" )

        ### Verify core name of files
        self.assertTrue( all( [f.endswith(expected_filename) for f in remote_files] ), msg=f"Change in core name for {case}" )

        ### Verify repo is current files
        recent_year = max([int(f.split("_")[0]) for f in remote_files])
        recent_month = max([int(f.split("_")[1]) for f in remote_files if f.split("_")[0]==str(recent_year)])
        self.assertGreaterEqual(datetime.strptime(f"{recent_year}-{recent_month}",'%Y-%m'), datetime.now()-timedelta(days=31),
                                msg=f'No recent database update for {case}' )
        
    def test_download(self):
        """All tests for downloaded are gathered in 1 single test to avoid asking the credentials multiple times."""
        if self.transport is not None:
            ### Set paths
            # remote Generation
            pathdir_gen = "/TP_export/AggregatedGenerationPerType_16.1.B_C/"
            filename_gen= "AggregatedGenerationPerType_16.1.B_C.csv"
            # remote Exchanges
            pathdir_exch = "/TP_export/PhysicalFlows_12.1.G/"
            filename_exch= "PhysicalFlows_12.1.G.csv"
            
            ### Get files
            with paramiko.SFTPClient.from_transport(self.transport) as sftp:
                remote_gen = sorted(sftp.listdir(pathdir_gen)) # Get files list in directory
                remote_exch = sorted(sftp.listdir(pathdir_exch)) # Get files list in directory
            
            
            ### Testing Generation
            self.remoteContent(remote_gen, filename_gen, case='Production')

            ### Testing
            self.remoteContent(remote_exch, filename_exch, case='Exchanges')

            ### Close the transport
            self.transport.close()
        
        else:
            raise paramiko.AuthenticationException(f"No connection was made. Skip download tests.")
        
        
        
#############
if __name__=="__main__":
    res = unittest.main(argv=[''], verbosity=2, exit=False)