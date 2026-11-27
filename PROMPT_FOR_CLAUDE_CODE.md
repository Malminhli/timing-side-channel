# Prompt for Claude Code (run the experiments on my laptop)

Copy everything below the line into Claude Code, opened inside the `timing-side-channel` folder.

---

You are helping me (Mohammed) run the experiments of my research project on timing side-channel leakage in string comparison. The code is in `src/`, the README explains the project, and `paper/template/` contains a paper template with `{{PLACEHOLDERS}}`. The experiments only attack a local toy function inside the same Python process. Nothing touches the network or any real system.

My machine: HP 255 G10 laptop, Arch Linux.

Please do the following, in order, and stop to ask me before any step that needs `sudo`:

1. **Read first.** Read `README.md` and every file in `src/` so you understand what each experiment does. Do NOT change the experiment logic, statistics or default parameters. If you think something is wrong, tell me and wait for my answer instead of editing.

2. **Set up the environment.**
   - Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
   - Install: `pip install -r requirements.txt`

3. **Prepare the machine for clean measurements.**
   - Check whether the laptop is on the charger (`cat /sys/class/power_supply/*/online` or `upower -d`). If it is on battery, tell me and wait.
   - Show me the current CPU governor (`cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort | uniq -c`).
   - Ask me if I want to switch it to `performance` with `sudo cpupower frequency-set -g performance` (install `cpupower` with pacman only if I agree). Remember the original governor so we can restore it at the end.
   - Remind me to close the browser and other heavy apps, and wait for me to confirm.

4. **Sanity run.** Run `MPLBACKEND=Agg python src/run_all.py --quick --out results_quick`. Confirm all three experiments finish without errors. These quick results are only a check and must NOT be used in the paper.

5. **Full run.** Run:
   ```
   mkdir -p results
   MPLBACKEND=Agg python src/run_all.py --out results 2>&1 | tee results/log.txt
   ```
   It should take roughly 5–15 minutes. Run it in the foreground with a long timeout (at least 60 minutes), and do not use the computer for anything heavy at the same time. Outputs: CSV files, PNG figures, `machine.txt`, and `log.txt` (the Experiment 1 slopes and the Experiment 3 summary are only printed to the console, so the log matters).

6. **Repeatability check.** Run the full set a second time into a separate folder:
   ```
   mkdir -p results_run2
   MPLBACKEND=Agg python src/run_all.py --out results_run2 2>&1 | tee results_run2/log.txt
   ```
   If the first full run took more than 40 minutes, ask me before doing the second run.

7. **Restore the machine.** If you changed the CPU governor, restore the original value.

8. **Summarise the real numbers for me.** From the CSV files and `log.txt` (not from memory or guesses), for both runs, give me:
   - Experiment 1: the slope in ns per correct character for each of the three targets, and the median at k = 0 and k = L.
   - Experiment 2: the t values for each target and each repeat, whether |t| is above 4.5, and the median difference in ns.
   - Experiment 3: success rate, length-recovery rate, % characters correct, median number of queries and mean time for each target.
   - The CPU model and Python version from `machine.txt`.
   - Anything surprising or inconsistent between the two runs.
   Report every number exactly as it appears in the files. Never invent, round away, or "fix" results. If something failed or looks wrong, say so plainly.

9. **Package the results.** Save the summary from step 8 as `results/SUMMARY.md`, then create `results_package.zip` containing `results/` and `results_run2/` (if it exists). Tell me where the zip is so I can send it back to finish the paper.

Do not fill in the paper template yourself, and do not push anything to GitHub. I will do those steps.
