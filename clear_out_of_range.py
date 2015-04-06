#! /usr/bin/env python

#	Script to clear values marked as out of range in an input file
__author__ = "Eldan Goldenberg, April 2015"
#		http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com

'''
CONTEXT:
	It's not unusual for data files from a scientific instrument to
	include values that the provider suspects are unreliable because they are out
	of range, but flag them as such in a column. I prefer to trust the provider's
	judgement and remove all the out of range values, because they probably do
	represent an instrument malfunctioning. This script iterates through a CSV
	with a designated "out of range" column, and NULLs every value flagged in that
	column.
ASSUMPTIONS:
	* CSV starts with a single header row
	* There is a column that for any given row, flags those values considered out
		of range in it.
	* The column names are exactly consistent between the header row and their
		references in the out of range column
TESTING:
	I am making this to clean data from https://green2.kingcounty.gov/marine-buoy/
	At present, this is the only file I've tested it on, with some manual
	pre-processing to make it fit the assumptions above
'''

import argparse
import unicodecsv as csv # unicode-aware replacement for the standard Python csv module. pip install unicodecsv. https://github.com/jdunck/python-unicodecsv
import os
import sys
import time




def main():
	args = get_args()
	print_with_timestamp("Starting run.")
	with open(args.input_file, 'rU') as infile:
		with open(args.output_file, 'w') as outfile:
			clean_file(infile, outfile, args.flag_col, args.separator)
	print_with_timestamp("Run complete.")




def clean_file(infile, outfile, flag_col, separator):
	reader = csv.DictReader(infile)
	writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
	writer.writeheader()
	replacements = {}
	unreplaceables = {}
	for row in reader:
		if row[flag_col] != None and row[flag_col] != '':
			for colname in row[flag_col].split(separator):
				if colname != None and colname != '' and colname != ' ':
					if colname in reader.fieldnames:
						row[colname] = None
						if colname in replacements.keys():
							replacements[colname] = replacements[colname] + 1
						else:
							replacements[colname] = 1
					else:
						print "Column mismatch: '"+colname+"'\tlisted in '"+flag_col+"' but not present in headers."
						if colname in unreplaceables.keys():
							unreplaceables[colname] = unreplaceables[colname] + 1
						else:
							unreplaceables[colname] = 1
		writer.writerow(row)
	if len(replacements) > 0:
		print "Here are the number of times each field was removed:"
		for key in replacements.keys():
			print key+":\t", replacements[key]
	else:
		print "No replacements were made."
	if len(unreplaceables) > 0:
		print "And this is the number of unmatchable filed names found in '"+flag_col+"':"
		for key in unreplaceables.keys():
			print key, unreplaceables[key]






def print_with_timestamp(msg):
	print time.ctime() + ": " + msg
	sys.stdout.flush() # explicitly flushing stdout makes sure that a .out file stays up to date - otherwise it can be hard to keep track of whether a background job is hanging



def get_args():
	parser = argparse.ArgumentParser(description="Import and/or update OSM data.")

# positional arguments
	parser.add_argument("input_file", help="required argument: the file we'll be cleaning.")
	parser.add_argument("output_file", help="required argument: the file we'll be saving cleaned data into. If this file already exists it will be overwritten.")
	parser.add_argument("flag_col", help="required argument: the name of the column that flags out of range values.")

# optional argument
	parser.add_argument("-s", "--separator", help="the character that separates values within the out of range column. Default is ';'.", nargs='?', default=';')

	return parser.parse_args()



if __name__ == "__main__":
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	main()
