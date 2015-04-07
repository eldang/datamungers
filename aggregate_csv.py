#! /usr/bin/env python

__author__ = "Eldan Goldenberg, April 2015"
#		http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com

'''
This is a tool to aggregate data by one dimension across another.

For example: turn a time-series into an "average day" by averaging across all
days, aggregated by time of day:
	./aggregate_csv.py inputfile outputfile daycolumn timecolumn
Or turn each day into its averages, by averaging across all times,
aggregated by date:
	./aggregate_csv.py inputfile outputfile timecolumn daycolumn

Non-numeric entries are simply dropped.

Note that it attempts to sort the output data, but only does so lexically.
This works poorly for non-ISO format dates.

IMPORTANT: because this aggregates with a simple mean, outliers in the source
data can skew averages terribly. Make sure you first clean up outliers and any
weird NULL placeholders in your dataset.
'''

import argparse
import copy
import unicodecsv as csv # unicode-aware replacement for the standard Python csv module. pip install unicodecsv. https://github.com/jdunck/python-unicodecsv
import os
import sys
import time




def main():
	args = get_args()
	print_with_timestamp("Starting run.")
	with open(args.input_file, 'rU') as infile:
		with open(args.output_file, 'w') as outfile:
			aggregate(infile, outfile, args.aggregate_across, args.aggregate_by)
	print_with_timestamp("Run complete.")




def aggregate(infile, outfile, agg_across, agg_by):
	reader = csv.DictReader(infile)
	output_fieldnames = copy.deepcopy(reader.fieldnames)
	output_fieldnames.remove(agg_across)
	writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
	writer.writeheader()

# First step through finding all agg_by values
	agg_by_keys = []
	for row in reader:
		if row[agg_by] not in agg_by_keys:
			agg_by_keys.append(row[agg_by])

# Then make the dict of dicts that will store interim data
	data_frame = {}
	for key in agg_by_keys:
		data_frame[key] = {}
		for field in output_fieldnames:
			data_frame[key][field] = {}
			data_frame[key][field]['count'] = 0
			data_frame[key][field]['sum'] = 0

# Now step through the reader again, sorting and counting values
	infile.seek(0)
	for row in reader:
		for field in row:
			if row[field]!= None and is_number(row[field]):
				data_frame[row[agg_by]][field]['count'] += 1
				data_frame[row[agg_by]][field]['sum'] += float(row[field])

# Now step through data_frame averaging as appropriate and write that to outfile
	for key in sorted(data_frame.keys()):
		outrow = {agg_by: key}
		for field in data_frame[key]:
			if data_frame[key][field]['count'] == 1:
				outrow[field] = data_frame[key][field]['sum']
			elif data_frame[key][field]['count'] > 1:
				outrow[field] = data_frame[key][field]['sum'] / data_frame[key][field]['count']
		writer.writerow(outrow)






def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False



def print_with_timestamp(msg):
	print time.ctime() + ": " + msg
	sys.stdout.flush() # explicitly flushing stdout makes sure that a .out file stays up to date - otherwise it can be hard to keep track of whether a background job is hanging



def get_args():
	parser = argparse.ArgumentParser(description="Aggregate data by one dimension across another.")

# positional arguments
	parser.add_argument("input_file", help="required argument: the file we'll be cleaning.")
	parser.add_argument("output_file", help="required argument: the file we'll be saving cleaned data into. If this file already exists it will be overwritten.")
	parser.add_argument("aggregate_across", help="required argument: the name of the column that we will be aggregating across.")
	parser.add_argument("aggregate_by", help="required argument: the name of the column that we will be aggregating by.")

# optional argument
#	parser.add_argument("-s", "--separator", help="the character that separates values within the out of range column. Default is ';'.", nargs='?', default=';')

	return parser.parse_args()



if __name__ == "__main__":
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	main()
