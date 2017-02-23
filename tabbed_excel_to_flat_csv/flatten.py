#! /usr/bin/env python3

# Converts multiple-tab Excel files into flat CSVs, preserving unicode
__author__ = "Eldan Goldenberg for Manastash Mapping, February 2017"
# http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com
#
# Usage: put a job list CSV like the enclosed files_to_process.csv
# into the same directory as the files it names.	Fill the columns as follows:
# filename: input file name relative to the location of the CSV itself
# header: row number (A = 1) of the row to use as a header - simply lets us skip rows if needed
# subheader: optional row number (A = 1) of a subheader row.
#		If a file has a subheader, the output CSV will have column headings in the
#		format: headervalue_subheadervalue
# tabs: column name for the text in tab names, so that their data is preserved
#		in the flat output CSV.	 Leave blank to only process the first tab
# column_wrap: optional number of columns after which the data wraps around
# special_handling: optional argument; values defined so far:
#		"transpose" will make a new row for each individual cell, with just 3
#			columns: column heading, row heading, value
# notes: optional human-readable notes, ignored by the script
#
# Then simply: flatten.py path/to/joblist.csv

import argparse
import csv
import os
import sys
import time
import xlrd	 # Python Excel reader. pip install xlrd. Documentation at https://secure.simplistix.co.uk/svn/xlrd/trunk/xlrd/doc/xlrd.html?p=4966



verbose = True
output_subdir = "flattened"




def main():
	args = get_args()
	print_with_timestamp("Starting run.")
	starttime = time.time()

	inputdir = os.path.dirname(args.joblist)
	outputdir = os.path.join(inputdir, output_subdir)

	filecount = process_job_list(inputdir, outputdir, args.joblist)

	print_with_timestamp(
			"Run complete. " + str(filecount) + " files processed in "
			+ elapsed_time(starttime) + "."
	)




def process_job_list(inputdir, outputdir, joblist):
	filecount = 0
	print(inputdir)
	print(outputdir)
	print(joblist)
	return filecount





def get_args():
	parser = argparse.ArgumentParser(description="Make flat CSVs out of tabbed Excel files")

# positional argument
	parser.add_argument("joblist", help="required argument: list of files to process with some metadata described in comments at the top of the script.")

	args = parser.parse_args()
	return args



def print_if_verbose(msg):
	if verbose:
		if msg == "":
			print(" ")
		else:
			print_with_timestamp(msg)



def print_with_timestamp(msg):
	print("	 " + time.ctime() + ": " + str(msg))
	sys.stdout.flush()
# explicitly flushing stdout makes sure that a .out file stays up to date
# otherwise it can be hard to keep track of whether a background job is hanging




def elapsed_time(starttime):
	seconds = time.time() - starttime
	if seconds < 1:
		return "Less than one second"
	hours = int(seconds / 60 / 60)
	minutes = int(seconds / 60 - hours * 60)
	seconds = int(seconds - minutes * 60 - hours * 60 * 60)
	if minutes < 1 and hours < 1:
		return str(seconds) + " seconds"
	elif hours < 1:
		return str(minutes) + " minute[s] and " + str(seconds) + " second[s]"
	else:
		return (
				str(hours) + " hour[s], " +
				str(minutes) + " minute[s] and " +
				str(seconds) + " second[s]"
		)


if __name__ == "__main__":
	try:
		main()
	except:
		import sys
		print(sys.exc_info()[0])
		import traceback
		print(traceback.format_exc())
	if verbose:
		print("Press Enter to continue ...")
		input()
