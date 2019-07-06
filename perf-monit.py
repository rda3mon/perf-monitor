#!/usr/bin/env python3

import argparse
import time
import subprocess
import os
import matplotlib.pyplot as plt

fetch_cpu = "ps -p {} -o %cpu --no-headers"
fetch_mem = "ps -p {} -o %mem --no-headers"
fetch_threads = "ps -p {} -o nlwp --no-headers"
fetch_lsof = "lsof -p {} 2> /dev/null | wc -l"
fetch_load = "cat /proc/loadavg"

default_dir = "/tmp/perf-monit"

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE);

        if result.returncode is 0:
            output = str((result.stdout).decode('UTF-8')).strip()
        else:
            output = 0
    except Exception as e:
        print("An exception occurred while executing command. Message: " + e.message);
    return output 

def writeToFile(content, fp, close=False):
    if close is False:
        fp.write(content)
    else:
        fp.close()

def monit(pid, output, interval, dirpath, draw):
    try:
        os.makedirs(dirpath)
    except:
        pass
    if output == "csv":
        fp = open("{}/{}.csv".format(dirpath, pid), "a");
        writeToFile("Time,CPU,Memory,Threads,Open Files,System Load\n", fp)

    plot_out = {"cpu": [], "mem": [], "threads": [], "lsof": [], "load": [], "now": []}
    try: 
        now = 0;
        while True:
            plot_out["cpu"].append(run_command(fetch_cpu.format(pid)))
            plot_out["mem"].append(run_command(fetch_mem.format(pid)))
            plot_out["threads"].append(run_command(fetch_threads.format(pid)))
            plot_out["lsof"].append(run_command(fetch_lsof.format(pid)))
            plot_out["load"].append(run_command(fetch_load))
            plot_out["now"].append(now)

            if output == "csv":
                writeToFile("{},{},{},{},{},{}\n".format(plot_out["now"][-1], plot_out["cpu"][-1], plot_out["mem"][-1], plot_out["threads"][-1], plot_out["lsof"][-1], plot_out["load"][-1]), fp);
            else:
                print("Time: {}\nCPU: {}\nMemory: {}\nThreads: {}\nOpen Files: {}\nLoad Factor: {}\n\n".format(plot_out["now"][-1], plot_out["cpu"][-1], plot_out["mem"][-1], plot_out["threads"][-1], plot_out["lsof"][-1], plot_out["load"][-1]));
            now += interval;
            time.sleep(interval);
    except KeyboardInterrupt as ex:
        print("Keyboard interrupted. Closing file");
    except Exception as ex:
        print("Failed with unknown exception. Message: " + str(ex));
    finally:
        if output == "csv":
            writeToFile(None, fp, True);

        fig, axs = plt.subplots(figsize=(24,16), nrows=2, ncols=2)

        axs[0, 0].plot(plot_out["now"], list(map(float, plot_out["cpu"])), 'tab:orange')
        axs[0, 0].set_title('CPU')
        axs[0, 1].plot(plot_out["now"], list(map(float, plot_out["lsof"])), 'tab:green')
        axs[0, 1].set_title('Open Files')
        axs[1, 0].plot(plot_out["now"], list(map(float, plot_out["mem"])), 'tab:red')
        axs[1, 0].set_title('Memory')
        axs[1, 1].plot(plot_out["now"], list(map(float, plot_out["threads"])), 'tab:blue')
        axs[1, 1].set_title('Threads')

        for ax in axs.flat:
            ax.set(xlabel='Time')

        plt.savefig("{}/{}.svg".format(dirpath, pid), format='svg', dpi=1200, bbox_inches='tight')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False,description='Performance Monitoring tools');
    parser.add_argument("-p", "--pid", help="Process id for analysing the performance", required=True);
    parser.add_argument("-o", "--output", choices=['csv', 'raw'], help="Output format", default="raw");
    parser.add_argument("-i", "--interval", choices=[3, 5, 10, 20, 60], type=int, help="Monitor interval", default=3);
    parser.add_argument("-s", "--dirpath", default=default_dir, help="Directory path where files to be stored");
    parser.add_argument("-d", "--draw", action='store_true', help="Store the output as figures");
    args = parser.parse_args();

    monit(args.pid, args.output, args.interval, args.dirpath, args.draw);
