import os
import subprocess

#in 'livetime.py', the 'data_fetcher' module (this) is imported to use the function defined.  This function is for starting the live timing data saving process.   This function can be accessed using the dot notation, 'data_fetcher.function_name()' this way, the live timing process can be initiated and controlled from the 'livetime.py' command by calling the relevant function defined in 'data_fetcher.py'.


def start_live_timing_data_saving():
    cmd = "python -m fastf1.livetiming save saved_data.txt"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def stop_live_timing_data_saving(process):
    process.terminate()