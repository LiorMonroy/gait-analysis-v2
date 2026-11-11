""" Trial 1: loading one walking trial and looking at the raw data to test code.

Each file is ~2 minutes of walking, sampled 100 times per second.
Columns: time, 8 left-foot sensors, 8 right-foot sensors,
total left force, total right force (all forces in newtons).
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = Path("data/gaitpdb")
FILE = "GaPt03_01.txt"          # try a Parkinson's file later, e.g. GaPt03_01.txt

# --- load ---
data = np.loadtxt(DATA_DIR / FILE)
time = data[:, 0]
left_sensors = data[:, 1:9]     # columns 2-9  (Python counts from 0)
right_sensors = data[:, 9:17]   # columns 10-17
left_total = data[:, 17]        # column 18
right_total = data[:, 18]       # column 19

print(f"File: {FILE}")
print(f"Rows (samples): {data.shape[0]}, columns: {data.shape[1]}")
print(f"Duration: {time[-1]:.1f} s")
print(f"Max left force: {left_total.max():.0f} N, max right force: {right_total.max():.0f} N")

# --- plot a 6-second window from the middle of the walk ---
start, end = 20, 26
win = (time >= start) & (time <= end)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax1.plot(time[win], left_total[win], label="Left foot")
ax1.plot(time[win], right_total[win], label="Right foot")
ax1.set_ylabel("Total force (N)")
ax1.set_title(f"{FILE}: total force under each foot")
ax1.legend()

colors = plt.cm.viridis(np.linspace(0, 1, 8))
for i in range(8):
    ax2.plot(time[win], left_sensors[win, i], color=colors[i], label=f"Sensor {i + 1}")
ax2.set_ylabel("Force (N)")
ax2.set_xlabel("Time (s)")
ax2.set_title("Left foot: each of the 8 sensors")
ax2.legend(ncol=4, fontsize=8)

fig.tight_layout()
Path("figures").mkdir(exist_ok=True)
fig.savefig(f"figures/01_raw_{FILE.replace('.txt', '')}.png", dpi=150)
plt.show()