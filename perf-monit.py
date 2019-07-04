#!/usr/bin/env python3

import argparse
import time
import subprocess

fetch_cpu = "ps -p {} -o %cpu --no-headers"
fetch_mem = "ps -p {} -o %mem --no-headers"
fetch_threads = "ps -p {} -o nlwp --no-headers"
fetch_lsof = "lsof -p {} 2> /dev/null | wc -l"
fetch_load = "cat /proc/loadavg  |  grep -oE '^[0-9.]{4} [0-9.]{4} [0-9.]{4}'"

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

def monit(pid, output, interval, outfile):
    fp = open(outfile, "a");
    writeToFile("Time,CPU,Memory,Threads,Open Files,System Load\n", fp)

    count = 0;
    while count < 10:
        count += 1;
        cpu = run_command(fetch_cpu.format(pid));
        mem = run_command(fetch_mem.format(pid));
        threads = run_command(fetch_threads.format(pid));
        lsof = run_command(fetch_lsof.format(pid));
        load = run_command(fetch_load);

        writeToFile("{},{},{},{},{}\n".format(cpu, mem, threads, lsof, load), fp);
        time.sleep(interval)

    writeToFile(None, None, True);



if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False,description='Performance Monitoring tools');
    parser.add_argument("-p", "--pid", help="Process id for analysing the performance", required=True);
    parser.add_argument("-o", "--output", choices=['csv'], help="Output format", required=True);
    parser.add_argument("-i", "--interval", choices=[5, 10, 20, 60], type=int, help="Monitor interval", required=True);
    parser.add_argument("-f", "--outfile", default="/tmp/output.csv", help="Monitor interval, default=/tmp/output.csv");
    args = parser.parse_args();

    monit(args.pid, args.output, args.interval, args.outfile);
