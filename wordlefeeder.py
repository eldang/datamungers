#! /usr/bin/env python

# Input file creator for Wordle
# Written by Eldan Goldenberg, Nov 2012
# http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com

# This program is free software; you can redistribute it and/or
#		modify it under the terms of the GNU General Public License
#		as published by the Free Software Foundation; either version 2
#		of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#		but WITHOUT ANY WARRANTY; without even the implied warranty of
#		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#		GNU General Public License for more details.
# The licence text is available online at:
#		http://www.gnu.org/licenses/gpl-2.0.html

# This program takes as input a CSV with the following attributes:
# Header row
# List of words as the first column
# One or more further columns with numbers in it
#
# As output it produces one file per column of numbers,
# in which each word from the first column is repeated n times,
# where n is the number from the corresponding column.
# Each file is named [column header].txt .
# Non-integer values are simply rounded off.
#
# Doing this allows me to feed the output files into Wordle.net
# to visualise the word frequencies.

import sys
import csv
import string

# Check command line arguments
# File name and
# 	optional --verbose argument. You'll get more feedback if you use that.
if len(sys.argv) == 3:
	verbose = True
	if sys.argv[1] == "--verbose": input_filename = sys.argv[2]
	elif sys.argv[2] == "--verbose": input_filename = sys.argv[1]
	else:	sys.exit("Error: unexpected command line arguments. " \
		"The only arguments should be a filename and optionally the --verbose switch.")
elif len(sys.argv) == 2:
	# then default to non-verbose
	verbose = False
	input_filename = sys.argv[1]
else:
	sys.exit("Error: unexpected command line arguments. " \
		"The only arguments should be a filename and optionally the --verbose switch.")

# Load input file
if verbose: print "Opening:", input_filename
with open(input_filename, 'rU') as f_in:
	dialect = csv.Sniffer().sniff(f_in.read(1024))
	f_in.seek(0)
	reader = csv.reader(f_in, dialect)

	# Count columns and make list of output files from the header row
	output_filenames = reader.next()[1:]
	if verbose: print "Making the following output files:", output_filenames

	# Open all the output files we'll be needing
	f_outs = [0]
	for i in range(0, len(output_filenames), 1):
		name = output_filenames[i]+".txt"
		f_outs.append(open(name, 'w'))
		if verbose: print name, "opened for output"

	# Go through the rest of the rows
	for row in reader:
		# read first column as word
		word = row[0]
		# If the "word" is actually a phrase, capitalise the individual words ...
		word = string.capwords(word)
		# ...and remove spaces so Wordle counts it as a whole.
		word = word.replace(" ", "")
		# for each other column, output to the relevant file as n repetitions of word
		for i in range(1, len(f_outs), 1):
			for j in range(0, int(round(float(row[i]))), 1):
				f_outs[i].write(word+" ")
			f_outs[i].write("\n")

	# Close files and we're done!
	if verbose: print "Finished parsing file and writing output."
	for i in range(1, len(f_outs), 1):
		f_outs[i].close()
	if verbose: print "Files closed. Exiting."
