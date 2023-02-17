import unittest
import os
import numpy as np
import pandas as pd

from dynamical.preprocessing import autocomplete



def get_missing_index(gap):
    if gap.lower()=='small':
        return [(None,'2020-01-01 00:45:00'), ('2020-01-10 12:00:00','2020-01-10 12:45:00'), ("2020-01-19 23:00",None)]
    elif gap.lower()=='long':
        return [('2020-01-10 00:00:00','2020-01-10 23:45:00')]
    elif gap.lower()=='excess':
        return [('2020-01-05 00:00:00','2020-01-15 23:45:00')]
    else:
        raise KeyError(f'Unknown gap type "{gap}"')
    
        
def create_series(gap, freq="H"):
    """Create one series with a specific kind of gap at a specific frequency"""
    dt = pd.date_range("2020", end="2020-01-19 23:45", freq=freq)
    
    if gap.lower()=='small':
        ### For short gap, use 20 days with missing 1h @start, @end, @center, for special and non-special
        base = np.concatenate([np.full(dt.shape[0]//2, 0), np.full(dt.shape[0]//2, 7)])
        series = pd.Series(base, index=dt)

        ### Set the sides to 1
        series.loc[:'2020-01-02 00:45:00'] = 7 # To obtain a completion of 7 if no special, and 1 if special
        series.loc["2020-01-18 23:00":] = 0 # To obtain a completion of 0 if no special, and 6 if special
    
    elif gap.lower()=='long':
        base = np.concatenate([np.full(dt.shape[0]//2, 0), np.full(dt.shape[0]//2, 7)])
        series = pd.Series(base, index=dt)

    else:
        base = np.concatenate([np.full(dt.shape[0]//2, 5), np.full(dt.shape[0]//2, 5)])
        series = pd.Series(base, index=dt)

    ### Add the missing days
    for mss in get_missing_index(gap):
        series.loc[mss[0]:mss[1]] = np.nan

    return {'Ctry': pd.DataFrame({'Solar':series, 'Banal':series})}

def get_expected(gap, freq='H'):
    missing = get_missing_index(gap)
    data = create_series(gap, freq=freq)['Ctry']

    ### Fill the gap with expected values
    if gap=='small':
        # Starting gap
        data.loc[missing[0][0]:missing[0][1],'Solar'] = 1
        data.loc[missing[0][0]:missing[0][1],'Banal'] = 7
        # Ending gap
        data.loc[missing[2][0]:missing[2][1],'Solar'] = 6
        data.loc[missing[2][0]:missing[2][1],'Banal'] = 0
        # Middle gap
        if freq=='H': data.loc[missing[1][0]:missing[1][1],:] = 3.5
        else: data.loc[missing[1][0]:missing[1][1],:] = np.array([np.linspace(0,7,num=6)[1:-1]]*2).T
    
    elif gap=='long':
        data.loc[missing[0][0]:missing[0][1],:] = 3.5
    
    else:
        data.loc[missing[0][0]:missing[0][1],:] = 0
        
    return data





class TestAutocomplete(unittest.TestCase):
    
    def verify_case(self, gap, freq):
        expected = get_expected(gap, freq)
        
        data = create_series(gap, freq)
        out = autocomplete.autocomplete(data)
        
        ### Verify the content
        self.assertTrue( np.all(out[1]==pd.DataFrame({"Ctry": {"Banal":freq, "Solar":freq}})),
                         msg=f"Correct freq returned for ({freq},{gap})")
        self.assertTrue( np.all(out[0]['Ctry'] == expected), msg=f"Correct content for ({freq},{gap})" )
    
    def test_autocomplete(self):
        frequencies = ['H','15T']
        gaps = ['small','long','excess']
        
        for freq in frequencies:
            for gap in gaps:
                self.verify_case(gap, freq)
        



        

#############
if __name__=='__main__':
    res = unittest.main(verbosity=2)
