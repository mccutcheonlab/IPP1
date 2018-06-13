# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 10:16:49 2018

@author: James Rig
"""

import JM_general_functions as jmf
import pandas as pd

class Session(object):
    
    def __init__(self, metafiledata):
        self.medfile = metafiledata[hrows['medfile']]
        self.rat = metafiledata[hrows['rat']]
        self.session = metafiledata[hrows['session']]
        self.diet = metafiledata[hrows['dietgroup']]
        self.bottleL = metafiledata[hrows['bottleL']]
        self.bottleR = metafiledata[hrows['bottleR']]
        
    def extractlicks(self):
        self.cas_meddata = jmf.medfilereader(medfolder + self.medfile,
                                         varsToExtract = sub2var(self, 'cas'),
                                         remove_var_header = True)
        self.malt_meddata = jmf.medfilereader(medfolder + self.medfile,
                                 varsToExtract = sub2var(self, 'malt'),
                                 remove_var_header = True)
    
    def calculatelickdata(self):
        self.cas_data = jmf.lickCalc(self.cas_meddata[0],
                                    offset=self.cas_meddata[1])
        self.malt_data = jmf.lickCalc(self.malt_meddata[0],
                                    offset=self.malt_meddata[1])
        

    

def sub2var(session, substance):
    
    if substance in session.bottleL:
        varsOut = ['b', 'c']        
    if substance in session.bottleR:
        varsOut = ['e', 'f']
    return varsOut

# Extracts data from metafile
metafile = 'R:\\DA_and_Reward\\gc214\\IPP1\\IPP1_metafile.txt'
medfolder = 'R:\\DA_and_Reward\\gc214\\IPP1\\MED-PC datafile\\'

rows, header = jmf.metafilereader(metafile)

hrows = {}
for idx, field in enumerate(header):
    hrows[field] = idx

# Sets up individual objects for each sessio and gets data from medfiles
sessions = {}
        
for row in rows:
    sessionID = row[hrows['rat']] + '-' + row[hrows['session']]
    sessions[sessionID] = Session(row)
    
#for session in sessions:
#       x = sessions[session]
#       if x.session == 's4': # s4 is the first preference test day


pref1 = [sessions[x] for x in sessions if sessions[x].session == 's4']

for x in pref1:
    x.extractlicks()
    x.calculatelickdata()

# Puts data in a pandas dataframe for easy acces

df = pd.DataFrame()
    
df.insert(0, 'rat', [x.rat for x in pref1])
df.insert(1, 'diet', [x.diet for x in pref1])
df.insert(2, 'caslicks', [x.cas_data['licks'][1:] for x in pref1])
df.insert(3, 'malt_licks', [x.malt_data['licks'][1:] for x in pref1])

    