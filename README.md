# encointer-assignment-simulation


Full analysis on remote machine:

1. Checkout repo on remote machine
2. `python3 analyze_assignment.py` on remote machine
3. `python3 analyze_logs.py` on remote machine
4. pull all analysis files into a folder called `data/` on local machine
   relevant files: `analysis_XYZ.csv`, `skips_XYZ.csv`, `lens_XYZ.csv`
   
Now locally:

5. `cd analysis`
6. `python3 -m venv env`
7. `source env/bin/activate`
8. `pip install -r requirements.txt`
8. `./run_all.sh`  
you will get a cryptic console output and some plots :)