import pandas as pd
import matplotlib.pyplot as plt

sdata = pd.read_csv('/home/pi/SamplerDev/logs/samplingTempPressTest3.dat', index_col=0, parse_dates=True)
sdata.plot()
