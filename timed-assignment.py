# This is a companion script that will manage timed nbgrader assignments
# on JupyterHub. It's little more than a hack, though someday I hope to
# eventually integrate this in some form into nbgrader.

# NOTE: This relies on modifications made on the nbgrader side to include
# timestamps whenever an assignment is checked OUT of JupyterHub, in
# addition to when assignments are submitted back in. You can't run
# this manager without those modifications!

# This script is broken into three parts:
# 1: Preamble
#   This sets up everything from the command line, mainly the times and
#   date ranges of the assignment. Once all the configuration options
#   have been processed, it goes to "sleep" until the assignment is to
#   be released.
#
# 2: Live assignment
#   After the assignment is released, the manager essentially acts as a
#   "monitor", checking the timestamp files every interval for retrievals
#   and submissions by the students. Finding any, it creates a hashed
#   entry in a dictionary and records all the activities as they appear
#   by that student. This is done to prevent or at least minimize the
#   consequences of direct tampering of the timestamp files by students
#   (since those tamperings would show up in the dictionary).
#
# 3: Post processing
#   Once the assignment period ends, the script runs the collect command,
#   pulling all the submitted assignments into the instructor database
#   (as such, late or unsubmitted assignments are not pulled in). It also
#   serializes the student dictionary to a file, so the instructors can
#   confirm these timestamps with the ones in the nbgrader timestamp files.
#

import argparse
from collections import defaultdict
from datetime import datetime
import glob
import json
import os
import subprocess
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'JupyterHub Exams',
        epilog = 'lol moar gr4d3z', add_help = 'How to use',
        prog = 'python timed-assignment.py <args>')
    parser.add_argument("-n", "--name", required = True,
        help = "Name of the assignment (in nbgrader) to check.")
    parser.add_argument("-s", "--startdate", required = True,
        help = "Timestamp for the date start time (in YYYY-MM-DD format).")

    # Optional arguments.
    parser.add_argument("-d", "--enddate", default = None,
        help = "Timestamp for the date deadline (in YYYY-MM-DD format). [DEFAULT: None]")
    parser.add_argument("-e", "--exchange", default = "/srv/nbgrader/exchange",
        help = "Path to the nbgrader exchange directory. [DEFAULT: /srv/nbgrader/exchange]")
    parser.add_argument("-ts", "--timestart", default = "00:00:00",
        help = "Timestamp for the time start. [DEFAULT: 00:00:00]")
    parser.add_argument("-te", "--timeend", default = "23:59:59",
        help = "Timestamp for the time end. [DEFAULT: 23:59:59]")
    parser.add_argument("-o", "--outfile", default = "fetches.json",
        help = "Path to an output file for the results. [DEFAULT: fetches.json]")
    parser.add_argument("-i", "--interval", default = 60, type = int,
        help = "Number of seconds to wait before searching for new results. [DEFAULT: 60]")

    args = vars(parser.parse_args())

    # Some configuration variables.
    starttime = "{} {}".format(args['startdate'], args['timestart'])
    if args['enddate'] is None:
        args['enddate'] = args['startdate']
    endtime = "{} {}".format(args['enddate'], args['timeend'])
    exam = args['name']
    exchange = args['exchange']
    students = {}

    # How much time until the assignment actually starts?
    # Pause for that interval. Then, release the assignment.
    ds = datetime.strptime(starttime, "%Y-%m-%d %H:%M:%S")
    t = int(ds.timestamp())
    delay = t - time.time()
    if delay > 0:
        print("Sleeping for {:.2f} seconds.".format(delay))
        time.sleep(t - time.time())
    print("Releasing exam \"{}\" at {}.".format(exam, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    cmd = "nbgrader release_assignment {}".format(exam).split()
    subprocess.run(cmd)

    # When does the assignment end?
    dt = datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S")
    ts = int(dt.timestamp())

    # Run while the assignmen is live, checking every so often
    # for any submissions made by students. The necessity of this
    # is to prevent (or at least minimize) direct tampering of the
    # timestamp files by the students.
    while time.time() < ts:
        # Grab all the text files.
        files = glob.glob(os.path.join(exchange, "*.txt"))
        for f in files:
            student = f.split("/")[-1].split(".")[0]
            if student not in students:
                students[student] = {}
            cmd = "openssl dgst -md5 {}".format(f).split()
            out = subprocess.run(cmd, stdout = subprocess.PIPE)
            filehash = out.stdout.split()[-1].decode()
            if filehash not in students[student]:
                with open(f, "r") as s_file:
                    students[student][filehash] = s_file.read()
        time.sleep(args['interval'])

    # Exam's over! Collect everything.
    print("Exam \"{}\" is ended! Collecting at {}.".format(exam, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    cmd = "nbgrader collect {}".format(exam).split()
    subprocess.run(cmd)
    with open(args["outfile"], "w") as out:
        json.dump(students, out)
