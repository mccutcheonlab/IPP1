# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 10:16:49 2018

@author: James Rig
"""

import JM_general_functions as jmf
import JM_custom_figs as jmfig
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np

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
    
    def calculatelickdata(self, interpolate='none'):
        self.cas_data = jmf.lickCalc(self.cas_meddata[0],
                                    offset=self.cas_meddata[1],
                                    adjustforlonglicks=interpolate)
        self.malt_data = jmf.lickCalc(self.malt_meddata[0],
                                    offset=self.malt_meddata[1],
                                    adjustforlonglicks=interpolate)

def sub2var(session, substance):
    
    if substance in session.bottleL:
        varsOut = ['b', 'c']        
    if substance in session.bottleR:
        varsOut = ['e', 'f']
    return varsOut

def prefhistFig(ax1, ax2, df, factor1, factor2):
    dietmsk = df.diet == 'NR'

    jmfig.shadedError(ax1, df[factor1][dietmsk], linecolor='black')
    ax1 = jmfig.shadedError(ax1, df[factor2][dietmsk], linecolor='xkcd:bluish grey')
    ax1.set_xticks([0,10,20,30])
    ax1.set_xticklabels(['0', '20', '40', '60'])

    jmfig.shadedError(ax2, df[factor1][~dietmsk], linecolor='xkcd:kelly green')
    ax2 = jmfig.shadedError(ax2, df[factor2][~dietmsk], linecolor='xkcd:light green')
    ax2.set_xticks([0,10,20,30])
    ax2.set_xticklabels(['0', '20', '40', '60'])
    
def shadedError(ax, yarray, linecolor='black', errorcolor = 'xkcd:silver'):
    yarray = np.array(yarray)
    y = np.mean(yarray)
    yerror = np.std(yarray)/np.sqrt(len(yarray))
    x = np.arange(0, len(y))
    ax.plot(x, y, color=linecolor)
    ax.fill_between(x, y-yerror, y+yerror, color=errorcolor, alpha=0.4)
    
    return ax

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
    x.calculatelickdata(interpolate='none')

# Puts data in a pandas dataframe for easy acces

df = pd.DataFrame()
    
df.insert(0, 'rat', [x.rat for x in pref1])
df.insert(1, 'diet', [x.diet for x in pref1])
df.insert(2, 'cashist', [x.cas_data['hist'] for x in pref1])
df.insert(3, 'malthist', [x.malt_data['hist'] for x in pref1])
df.insert(4, 'caslicks', [x.cas_data['total'] for x in pref1])
df.insert(5, 'maltlicks', [x.malt_data['total'] for x in pref1])

figIPP1a, ax = plt.subplots(nrows=1, ncols=2, sharex='all', sharey=True)
prefhistFig(ax[0], ax[1], df, 'cashist', 'malthist')
#figIPP1.text(0.55, 0.04, 'Time (min)', ha='center')
ax[0].set_ylabel('Licks per 2 min')

#figIPP1b, ax = plt.subplots(1, 1, 1)


