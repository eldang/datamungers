#! /usr/bin/env python

#	Script to clear values marked as out of range in an input file
__author__ = "Eldan Goldenberg, April 2015"
#		http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com

''' CONTEXT: It's not unusual for data files from a scientific instrument to
include values that the provider suspects are unreliable because they are out of
range, but flag them as such in a column. I prefer to trust the provider's
judgement and remove all the out of range values, because they probably do
represent an instrument malfunctioning. This script iterates through a CSV with
a designed "out of range" column, and NULLs every value flagged in that column.
ASSUMPTIONS: * CSV starts with a single header row * There is a column that for
any given row, flags those values considered out of range in it. * The column
names are exactly consistent between the header row and their references in the
out of range column '''

import argparse
# import copy
import unicodecsv as csv # unicode-aware replacement for the standard Python csv module. pip install unicodecsv. https://github.com/jdunck/python-unicodecsv
import os
import sys
import time




def main():
	args = get_args()
	print_with_timestamp("Starting run.")

	print_with_timestamp("Run complete.")






def print_with_timestamp(msg):
	print time.ctime() + ": " + msg
	sys.stdout.flush() # explicitly flushing stdout makes sure that a .out file stays up to date - otherwise it can be hard to keep track of whether a background job is hanging



def get_args():
	parser = argparse.ArgumentParser(description="Import and/or update OSM data.")

# positional arguments
	parser.add_argument("input_file", help="required argument: the file we'll be cleaning")
	parser.add_argument("output_file", help="required argument: the file we'll be saving cleaned data into")
	parser.add_argument("out_of_range_column", help="required argument: the name of the column that flags out of range values")

# optional argument
	parser.add_argument("-v", "--verbose", help="output progress reports while working (default is off)", action="store_true")

	args = parser.parse_args()
	return args



if __name__ == "__main__":
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	main()
