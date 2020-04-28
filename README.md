# `nbgrader` scripts

Various [nbgrader](http://github.com/jupyter/nbgrader/) + [JupyterHub](https://github.com/jupyterhub/jupyterhub) scripts I've assembled to help with online instruction.

These scripts were tested on
 - `python` 3.7.6
 - `nbgrader` 0.6.1
 - `jupyterhub` 1.0.0

### `timed-assignment.py`

This script functions as a "manager" and "monitor" to enforce timed assignments released on JupyterHub using nbgrader. It requires a slight modification in nbgrader to function correctly: this modification adds check-out timestamps in addition to submission timestamps in the nbgrader exchange.

First and foremost, this script provides fully-automated assignment release and collection with nbgrader according to specific start and end time intervals. In this way, you don't have to worry about remembering to release the assignment on time or collect it at the deadline; just set those in the command line parameters ahead of time and forget about it.

Due to the world-readable nature of the nbgrader exchange, steps are taken on this end to minimize the possibility of tampering with the timestamp files, hence the ultimate purpose of this script. It monitors for changes in the exchange directory over the whole active interval of the assignment and records those changes in a dictionary. Once the active interval has ended (i.e., the assignment is due), the monitoring script serializes all the timestamp information to a file that can be read later by instructors and verified against the timestamps in the exchange for evidence of any tampering.

### `nbgrader`

To install this change, you'll need to overwrite the `fetch_assignment.py` file in nbgrader to include a new function.

Look at `$PYTHONPATH/lib/python3.7/site-packages/nbgrader/`, then go to the subdirectory `exchange/`. Put the new `fetch_assignment.py` file from this repository there (feel free to rename the old one, though modificaions in this file are clearly identified and easily removed by hand if you prefer).

The modifications add a new function, `do_timed`, which only trigger if the assignment name (as identified in nbgrader) matches a hard-coded parameter list in the new function. Otherwise, it operates identically to the old version.

If the assignment is listed as a timed one, then the new function kicks off by recording the fetch time in a uniquely-named file in the nbgrader exchange, according to the student account that fetched it. Each fetch is recorded and logged, and when paired with the assignment monitor that periodically checks these files for changes, instructors will have a near-complete record of the timeline of the assignment with some added robustness if the students should try to tamper with the timestamp files in the exchange.

It isn't foolproof, but it's close.