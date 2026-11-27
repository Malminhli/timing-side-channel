"""Run all three experiments and save the machine info next to the results.

    python run_all.py            # full run (roughly 5-15 min on a laptop)
    python run_all.py --quick    # sanity check (under a minute), NOT for the paper

Each experiment has different options, so this script passes each one only
the options it understands. To change a single setting, run that experiment
script directly (e.g. python exp2_tvla.py --samples 5000).
"""
import argparse
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# Full run: each script's own defaults (those are the paper settings).
# Quick run: tiny settings, only to check that everything works.
FULL = {"exp1_leakage.py": [], "exp2_tvla.py": [], "exp3_attack.py": []}
QUICK = {
    "exp1_leakage.py": ["--samples", "300"],
    "exp2_tvla.py": ["--samples", "5000", "--repeats", "2"],
    "exp3_attack.py": ["--samples", "50", "--trials", "2"],
}


def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return "unknown"


def save_machine_info(out):
    import numpy
    with open(os.path.join(out, "machine.txt"), "w") as f:
        f.write(f"python   : {sys.version}\n")
        f.write(f"numpy    : {numpy.__version__}\n")
        f.write(f"platform : {platform.platform()}\n")
        f.write(f"processor: {platform.processor()}\n")
        # The CPU frequency governor affects timing noise a lot; record it.
        f.write("governor : " + read(
            "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") + "\n")
        f.write("args     : " + " ".join(sys.argv[1:]) + "\n")
        try:
            cpu = subprocess.run(["lscpu"], capture_output=True,
                                 text=True).stdout
            f.write("\n" + cpu)
        except FileNotFoundError:
            pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--quick", action="store_true",
                   help="small settings for a fast sanity run")
    p.add_argument("--out", default=os.path.join(HERE, "..", "results"))
    a = p.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    save_machine_info(out)

    settings = QUICK if a.quick else FULL
    start = time.perf_counter()
    for script, args in settings.items():
        print(f"\n===== {script} =====", flush=True)
        subprocess.run([sys.executable, os.path.join(HERE, script),
                        "--out", out] + args, check=True)
    minutes = (time.perf_counter() - start) / 60
    print(f"\nAll done in {minutes:.1f} min. Results are in: {out}")
    if a.quick:
        print("(quick mode: settings are too small for real conclusions)")


if __name__ == "__main__":
    main()
