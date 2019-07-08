#!/usr/bin/env python3

import argparse
import time
import subprocess
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

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

def draw_subplot(plot, color, x, y, xlabel, ylabel):
    x = list(map(float, x))
    y = list(map(float, y))
    plot.plot(x, y, color)
    #plot.set_title(ylabel)
    #plot.set_yticks(np.arange(min(y), max(y), 1));
    plot.set(xlabel=xlabel, ylabel=ylabel)

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

        fix, ((cpu_plot, open_files_plot), (memory_plot, threads_plot), (load1m_plot, load5m_plot)) = plt.subplots(figsize=(24,16), nrows=3, ncols=2);

        tab_color = "tab:red"
        load_1mavg = [item[0] for item in map(lambda x: x.split(), plot_out["load"])]
        load_5mavg = [item[1] for item in map(lambda x: x.split(), plot_out["load"])]

        draw_subplot(plot=cpu_plot, color=tab_color, x=plot_out["now"], y=plot_out["cpu"], ylabel="CPU", xlabel="Time");
        draw_subplot(plot=open_files_plot, color=tab_color, x=plot_out["now"], y=plot_out["lsof"], ylabel="Open Files", xlabel="Time");
        draw_subplot(plot=memory_plot, color=tab_color, x=plot_out["now"], y=plot_out["mem"], ylabel="Memory", xlabel="Time");
        draw_subplot(plot=threads_plot, color=tab_color, x=plot_out["now"], y=plot_out["threads"], ylabel="Threads", xlabel="Time");
        draw_subplot(plot=load1m_plot, color=tab_color, x=plot_out["now"], y=load_1mavg, ylabel="Load 1 Minute avg", xlabel="Time");
        draw_subplot(plot=load5m_plot, color=tab_color, x=plot_out["now"], y=load_5mavg, ylabel="Load 5 Minute avg", xlabel="Time");
       

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
