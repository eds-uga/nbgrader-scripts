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