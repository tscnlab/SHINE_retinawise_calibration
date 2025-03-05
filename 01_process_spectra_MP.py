# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 15:41:36 2024

@author: jmarti2
"""

# %%
import glob
import re
import os.path as op
import pathlib as pl

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pysilsub import problems
import seaborn as sns

plt.style.use("bmh")
plt.rcParams["font.size"] = 10


def tryint(s):
    try:
        return int(s)
    except:
        return s


def sort_files(s):
    return [tryint(c) for c in re.split("([0-9]+)", s)]


# %% Set these accordingly
spd_path = r"C:\Users\experiment\Documents\RetinaWISE\CalibrationMP\20230305_calibration\*.csv"
out_path = r"C:\Users\experiment\Documents\RetinaWISE\CalibrationMP\20230305_calibration"

# %% Process the spectra

# Get the file paths
files = glob.glob(spd_path)
files = sorted(files, key=sort_files)
ratios = np.hstack([[0.0, 0.01, 0.02], np.linspace(.05,1,20)])
ratios = [int(r*100) for r in ratios]
# Separate store for left and right eye
right_spds = []
left_spds = []

# Loop over files
for f in files:
    # Extract Primary label using regex
    p = re.findall("[rl][0-5](?=_)", f)[0]
    # Load data
    df = pd.read_csv(
        f, sep=",", skiprows=27,nrows=401, header=None, encoding="unicode_escape"
    ).set_index(
        0
    )
    df.index.name='Wavelength'
    fig,ax=plt.subplots()
    df.plot(ax=ax)
    df.columns=ratios
    df=df.T
    df.index.name='Setting'   
    df["Primary"] = int(p[1])

    df = df.set_index("Primary", append=True)
    df = df.reorder_levels(["Primary", "Setting"])
    
    if p[0] == 'r':
        right_spds.append(df)
    elif p[0] == 'l':
        left_spds.append(df)
        
right_spds=pd.concat(right_spds)
left_spds=pd.concat(left_spds)

right_spds.to_csv(r"C:\Users\experiment\Documents\RetinaWISE\CalibrationMP\right_spds.csv")
left_spds.to_csv(r"C:\Users\experiment\Documents\RetinaWISE\CalibrationMP\left_spds.csv")

#%%
right = r"C:\Users\experiment\Documents\RetinaWISE\CalibrationMP\right_spds.csv"
left = r"C:\Users\experiment\Documents\RetinaWISE\CalibrationMP\left_spds.csv"

ssp_right = problems.SilentSubstitutionProblem(
    right,
    [380, 780, 1],
    [100] * 6,
    ["violet", "blue", "cyan", "green", "orange", "red"],
    config=dict(calibration_units="W/[sr*sqm*nm]")
)
    
left = r"C:\Users\experiment\Documents\RetinaWISE\CalibrationMP\left_spds.csv"
ssp_left = problems.SilentSubstitutionProblem(
    left,
    [380, 780, 1],
    [100] * 6,
    ["violet", "blue", "cyan", "green", "orange", "red"],
    config=dict(calibration_units="W/[sr*sqm*nm]")
)  

left_fig = ssp_left.plot_calibration_spds_and_gamut()
right_fig = ssp_right.plot_calibration_spds_and_gamut()

left_fig.savefig(op.join(out_path, "left_spds.png"))
right_fig.savefig(op.join(out_path, "right_spds.png"))

