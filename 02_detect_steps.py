"""Trial 3: detect individual steps (heel strike and toe-off) in one walking trial.

A foot counts as on the ground when its total force is above a threshold.
Heel strike = the sample where force rises above the threshold.
Toe-off     = the sample where force drops back below it.
From these events: stance, swing and stride time for every step.
"""
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

DATA_DIR = Path("data/gaitpdb")
FILE = "GaCo01_01.txt"          # Parkinson's example: GaPt03_01.txt
FS = 100                        # samples per second

MIN_CONTACT_S = 0.25            # shorter contacts are noise, not steps
TRIM_S = 5                      # first/last 5 s excluded (starting and stopping)


def detect_steps(force, fs=FS):
    """Heel-strike and toe-off sample indices for one foot."""
    # 5% of a typical peak, never below 20 N
    threshold = max(20, 0.05 * np.percentile(force, 95))
    on_ground = force > threshold

    # +1 where the foot lands, -1 where it lifts
    change = np.diff(on_ground.astype(int))
    heel_strikes = np.where(change == 1)[0] + 1
    toe_offs = np.where(change == -1)[0] + 1

    # recording may start mid-step: drop a toe-off with no heel strike before it
    if len(toe_offs) and len(heel_strikes) and toe_offs[0] < heel_strikes[0]:
        toe_offs = toe_offs[1:]
    n = min(len(heel_strikes), len(toe_offs))
    heel_strikes, toe_offs = heel_strikes[:n], toe_offs[:n]

    long_enough = (toe_offs - heel_strikes) / fs >= MIN_CONTACT_S
    inside = (heel_strikes >= TRIM_S * fs) & (toe_offs <= len(force) - TRIM_S * fs)
    keep = long_enough & inside
    return heel_strikes[keep], toe_offs[keep], threshold


def step_times(heel_strikes, toe_offs, fs=FS):
    """Stance, swing and stride durations in seconds."""
    stance = (toe_offs - heel_strikes) / fs              # foot on the ground
    stride = np.diff(heel_strikes) / fs                  # heel strike to next heel strike
    swing = (heel_strikes[1:] - toe_offs[:-1]) / fs      # foot in the air
    return stance, swing, stride


# --- load ---
data = np.loadtxt(DATA_DIR / FILE)
time = data[:, 0]
forces = {"Left": data[:, 17], "Right": data[:, 18]}

# --- detect and summarise ---
results = {}
print(f"File: {FILE}\n")
for side, force in forces.items():
    hs, to, thr = detect_steps(force)
    stance, swing, stride = step_times(hs, to)
    results[side] = dict(hs=hs, to=to, thr=thr, stride=stride)
    print(f"{side} foot: {len(hs)} steps (threshold {thr:.0f} N)")
    print(f"  stance  {stance.mean():.3f} ± {stance.std():.3f} s")
    print(f"  swing   {swing.mean():.3f} ± {swing.std():.3f} s")
    print(f"  stride  {stride.mean():.3f} ± {stride.std():.3f} s")
    print(f"  stance = {stance.mean() / stride.mean() * 100:.0f}% of each stride\n")

all_strides = np.concatenate([results["Left"]["stride"], results["Right"]["stride"]])
print(f"Cadence: {120 / all_strides.mean():.0f} steps per minute")

# --- plot ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

# top: left foot force with detected events, 6-second window
start, end = 20, 26
win = (time >= start) & (time <= end)
left = results["Left"]
ax1.plot(time[win], forces["Left"][win], color="black", lw=1.2, label="Left foot force")
ax1.axhline(left["thr"], color="gray", ls="--", lw=1, label="Contact threshold")
hs_in = left["hs"][(time[left["hs"]] >= start) & (time[left["hs"]] <= end)]
to_in = left["to"][(time[left["to"]] >= start) & (time[left["to"]] <= end)]
ax1.plot(time[hs_in], forces["Left"][hs_in], "^", color="tab:green", ms=9, label="Heel strike")
ax1.plot(time[to_in], forces["Left"][to_in], "v", color="tab:red", ms=9, label="Toe-off")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Force (N)")
ax1.set_title(f"{FILE}: detected steps (left foot)")
ax1.legend(loc="upper right", fontsize=8)

# bottom: every stride across the whole walk
for side, color in (("Left", "tab:blue"), ("Right", "tab:orange")):
    ax2.plot(results[side]["stride"], "o-", ms=3, lw=0.8, color=color, label=f"{side} foot")
ax2.set_xlabel("Stride number")
ax2.set_ylabel("Stride time (s)")
ax2.set_title("Stride time across the whole walk")
ax2.legend()

fig.tight_layout()
Path("figures").mkdir(exist_ok=True)
fig.savefig(f"figures/02_steps_{FILE.replace('.txt', '')}.png", dpi=150)
plt.show()