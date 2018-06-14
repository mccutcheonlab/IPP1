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

## Colour scheme
col={}
col['np_cas'] = 'xkcd:silver'
col['np_malt'] = 'white'
col['lp_cas'] = 'xkcd:kelly green'
col['lp_malt'] = 'xkcd:light green'


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
                                    burstThreshold=0.5, binsize=120,
                                    adjustforlonglicks=interpolate)
        self.malt_data = jmf.lickCalc(self.malt_meddata[0],
                                    offset=self.malt_meddata[1],
                                    burstThreshold=0.5, binsize=120,
                                    adjustforlonglicks=interpolate)

def sub2var(session, substance):
    
    if substance in session.bottleL:
        varsOut = ['b', 'c']        
    if substance in session.bottleR:
        varsOut = ['e', 'f']
    return varsOut

def makedataframe(day):
    
    subset = [sessions[x] for x in sessions if sessions[x].session == day]
    
    for x in subset:
        x.extractlicks()
        x.calculatelickdata(interpolate='none')
    
    # Puts data in a pandas dataframe for easy acces
    
    df = pd.DataFrame()
        
    df.insert(0, 'rat', [x.rat for x in subset])
    df.insert(1, 'diet', [x.diet for x in subset])
    df.insert(2, 'cashist', [x.cas_data['hist'] for x in subset])
    df.insert(3, 'malthist', [x.malt_data['hist'] for x in subset])
    df.insert(4, 'caslicks', [x.cas_data['total'] for x in subset])
    df.insert(5, 'maltlicks', [x.malt_data['total'] for x in subset])
    df.insert(6, 'caslicks_all', [x.cas_data['licks'] for x in subset])
    df.insert(7, 'maltlicks_all', [x.malt_data['licks'] for x in subset])
    
    return df

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
    
def nplp2Dfig(df, factor1, factor2, ax):
    dietmsk = df.diet == 'NR'
    
    a = [[df[factor1][dietmsk], df[factor2][dietmsk]],
          [df[factor1][~dietmsk], df[factor2][~dietmsk]]]

    ax, x, _, _ = jmfig.barscatter(a, paired=True,
                 barfacecoloroption = 'individual',
                 barfacecolor = [col['np_cas'], col['np_malt'], col['lp_cas'], col['lp_malt']],
                 scatteredgecolor = ['xkcd:charcoal'],
                 scatterlinecolor = 'xkcd:charcoal',
                 grouplabel=['NR', 'PR'],
                 scattersize = 60,
                 ax=ax)

def casVmaltFig(ax, df, factor1, factor2):
    # prepare data
    casdata = np.array(df[factor1])
    maltdata = np.array(df[factor2])
    xydataAll = []
    for cas, malt in zip(casdata, maltdata):
        xydata = []
        x = np.array([cas[1:], [1]*(len(cas)-1)])
        y = np.array([malt[1:], [2]*(len(malt)-1)])
        alllicks = np.concatenate((x,y),axis=1)
        idx = np.argsort(alllicks[0])
        sortedlicks = alllicks[:,idx]
        xydata.append(np.cumsum(np.array(sortedlicks[1,:] == 1, dtype=int)))
        xydata.append(np.cumsum(np.array(sortedlicks[1,:] != 1, dtype=int)))
        xydataAll.append(xydata)
    
    dietmsk = (df.diet == 'NR')
    dietmsk = dietmsk[:24]
    
    # plot line of unity    
    ax.plot([0, 4000], [0, 4000], '--', color='xkcd:silver', linewidth=0.75)
    
    npdata = [x for i,x in enumerate(xydataAll) if dietmsk[i]]
    for x in npdata:
        ax.plot(x[0], x[1], c='xkcd:charcoal', alpha=0.9, linewidth=1)
        ax.scatter(x[0][-1], x[1][-1], c='white', edgecolors='xkcd:charcoal', zorder=-1)
    
    lpdata = [x for i,x in enumerate(xydataAll) if not dietmsk[i]]
    for x in lpdata:
        ax.plot(x[0], x[1], c='xkcd:kelly green', alpha=0.9, linewidth=1)
        ax.scatter(x[0][-1], x[1][-1], color='none', edgecolors='xkcd:kelly green')
        
    max_x = np.max([ax.get_xlim(), ax.get_ylim()])
    ax.set_xlim([-300, max_x])
    ax.set_ylim([-300, max_x])
    
    return xydataAll
    
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

## Analysis of first preference day

df = makedataframe('s4')

figIPP1a, ax = plt.subplots(nrows=1, ncols=2, sharex='all', sharey=True)
prefhistFig(ax[0], ax[1], df, 'cashist', 'malthist')
#figIPP1.text(0.55, 0.04, 'Time (min)', ha='center')
ax[0].set_ylabel('Licks per 2 min')

figIPP1b = plt.figure()
ax = plt.subplot(111)
nplp2Dfig(df, 'caslicks', 'maltlicks', ax)

figIPP1c = plt.figure(figsize=(4,4))
ax = plt.subplot(1,1,1)                
casVmaltFig(ax, df, 'caslicks_all', 'maltlicks_all')
ax.set_xlabel('Licks for casein')
ax.set_ylabel('Licks for maltodextrin')
plt.yticks([0, 2000, 4000])
plt.xticks([0, 2000, 4000])

#df = makedataframe('s7')
#
#figIPP1a, ax = plt.subplots(nrows=1, ncols=2, sharex='all', sharey=True)
#prefhistFig(ax[0], ax[1], df, 'cashist', 'malthist')
##figIPP1.text(0.55, 0.04, 'Time (min)', ha='center')
#ax[0].set_ylabel('Licks per 2 min')
#
#figIPP1b = plt.figure()
#ax = plt.subplot(111)
#nplp2Dfig(df, 'caslicks', 'maltlicks', ax)


