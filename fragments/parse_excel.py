#! /usr/bin/env python

#	Script to parse Excel files from Peru's financial regulator
# Written as an exercise for MIX
__author__ = "Eldan Goldenberg, March 2015"
#		http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com


# TODO to make this more useful:
# 1. break up that main function into a few parts
# 2. comment, comment, comment
# 3. add option to output .xlsx, which Tableau handles better
# 4. make interim output optional
# 5. make month_int_from_spanish() use just the first few letters, so more typos are handled gracefully



import argparse
import copy
import unicodecsv as csv # unicode-aware replacement for the standard Python csv module. pip install unicodecsv. https://github.com/jdunck/python-unicodecsv
import os
import sys
import time
import xlrd	# Python Excel reader. pip install xlrd. Documentation at https://secure.simplistix.co.uk/svn/xlrd/trunk/xlrd/doc/xlrd.html?p=4966



def main():
	args = get_args()
	print_with_timestamp("Starting run.")

	globalheaders = ['dir', 'fname', 'sheet', 'year', 'month', 'day', 'title', 'date']

	data_frame = []

# ASSUMPTION: we want to parse every single .xls file found within args.root_dir and its subdirectories, but ignore anything else
	for dirName, subdirList, fileList in os.walk(args.root_dir):
		for fname in fileList:
			if fname[-4:].lower() != '.xls':
				print_with_timestamp("Skipping " + dirName +'/'+ fname + " because it's not a .xls file.")
			elif fname[0] == '~':
				pass # just skip these - they're temp files from having the Excel sheet open
			else:
				book = xlrd.open_workbook(os.path.abspath(dirName + '/' + fname))

				for sheet in book.sheets():
# ASSUMPTION: some workbooks contain empty sheets; just skip those
					if sheet.nrows is 0 or sheet.ncols is 0:
						pass
					else:
#						print_with_timestamp("Parsing sheet named " + sheet.name.encode('utf-8', 'ignore') + ".")
# ASSUMPTION: all worksheets we care about have a human-readable title in either A1, A2 or B1, and if it's A2 or B1 then the entire column A is empty
# (i.e. I know there's at least one worksheet that doesn't fit this pattern, in Peru Data/Branch Data/Financial Institution/B-3241-jl2009.XLS, because it's just a summary of data that's in the form I can work with in another worksheet in the same file)
# I did find one other exception to this pattern, in Peru Data/Branch Data/Rural Credit and Savings//C-2234-fe2009.XLS. Because it's exactly one file, I manually edited that one to make it comply.
						if sheet.cell_value(0,0) != "":
							title = sheet.cell_value(0,0).encode('utf-8', 'ignore')
							firstrow = firstcol = 0
						elif sheet.cell_value(0,1) != "":
							title = sheet.cell_value(0,1).encode('utf-8', 'ignore')
							firstrow = 0
							firstcol = 1
						elif sheet.cell_value(1,0) != "":
							title = sheet.cell_value(1,0).encode('utf-8', 'ignore')
							firstrow = 1
							firstcol = 0
						else:
							print_with_timestamp("Can't find title cell in sheet " + sheet.name.encode('utf-8', 'ignore') + " in file " + os.path.abspath(dirName + '/' + fname))
							break # just skip these sheets
# ASSUMPTION: every sheet has a date line immediately below the title.  This can be either an Excel date type (shows up as a float in Python) or a text string
						dateline = sheet.cell_value(firstrow+1,firstcol)
						if type(dateline) is float:
							dateline = xlrd.xldate_as_tuple(dateline, book.datemode)
							dateyear = dateline[0]
							datemonth = dateline[1]
							dateday = dateline[2]
						else:
# ASSUMPTION: every text date line is in the form "Al DD de MES [de] YYYY", possibly with spaces and/or parentheses before and/or after
							i = dateline.find('Al ')+3
							dateday = int(dateline[i:i+3])
							i = dateline.find('de ',i)+3
							i_end = dateline.find(' ',i)
							datemonth = month_int_from_spanish(dateline[i:i_end])
							i = dateline.find('2',i)
							dateyear = int(dateline[i:i+4])
						datestring = make_date_string(dateyear, datemonth, dateday)
# ASSUMPTION: every sheet's actual data table starts with a cell labeled "Empresa", which is the beginning of a double header row
						headers = []
						for row in range (firstrow+2, sheet.nrows):
							if sheet.cell_value(row,firstcol) == u'Empresa':
								for col in range (firstcol, sheet.ncols):
									item = sheet.cell_value(row, col)
									if item != '':
										headers.append(str(item.encode('utf-8', 'ignore')))
									else:
										headers.append(headers[col-1-firstcol])
								row += 1
								for col in range (firstcol, sheet.ncols):
									item = sheet.cell_value(row, col)
									if item != '':
										headers[col-firstcol] += ": " + str(item.encode('utf-8', 'ignore'))
								firstdatarow = row + 1
								break
						else:
							print_with_timestamp("Can't find start of data table in " + sheet.name.encode('utf-8', 'ignore') + " in file " + os.path.abspath(dirName + '/' + fname))
							exit(1) # actually exit the script here, because we won't reach this condition unless something unforeseen has gone wrong
						for h in headers:
							if h not in globalheaders:
								globalheaders.append(h)
# ASSUMPTION: there can be blank row[s] after the headers, and if the first cell is blank then the entire row will be.
						while sheet.cell_value(firstdatarow,firstcol) == '':
							firstdatarow += 1
						sheet_defaults = {
							'dir': dirName,
							'fname': fname,
							'sheet': sheet.name.encode('utf-8', 'ignore'),
							'year': dateyear,
							'month': datemonth,
							'day': dateday,
							'title': title,
							'date': datestring
						}
						prev_row = {}
# ASSUMPTION: every blank cell represents the same value as the cell above it (as though the cells were merged)
						for row in range (firstdatarow, sheet.nrows):
							i = 0
							row_data = {}
#							print row_data
							row_data = copy.deepcopy(sheet_defaults)
							for col in range (firstcol,sheet.ncols):
								item = sheet.cell_value(row, col)
								if (item is None or item == '') and (len(prev_row) > 0):
									row_data[headers[i]] = prev_row[headers[i]]
								else:
									row_data[headers[i]] = str(unicode(sheet.cell_value(row, col)).encode('utf-8', 'ignore'))
								i+=1
								if item == "5433" or item == 5433: print row_data
							prev_row = row_data
#							print sheet_defaults
#							print row_data
							data_frame.append(row_data)
#							print len(data_frame)
	print_with_timestamp("Loading complete, now writing raw file.")
	with open('interim.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=globalheaders)
		writer.writeheader()
		for row in data_frame:
			writer.writerow(row)
	print_with_timestamp("Raw file written, now writing cleaned output file.")
	with open('output.csv', 'w') as csvfile:
		fields = [
			'NAME_0',
			'NAME_1',
			'NAME_2',
			'NAME_3',
			'Type of Institution',
			'Type of Access Point',
			'Name of Company',
			'Name of Branch',
			'Metric Type',
			'FSP Metrics',
			'FSP Metrics Description',
			'Date',
			'Year',
			'Month',
			'Day'
		]
		writer = csv.DictWriter(csvfile, fieldnames=fields)
		writer.writeheader()
		for row in data_frame:
# ASSUMPTION: the following few rows are special cases which were total or subtotal rows in the source data, so we should skip them
			if row['Empresa'] == "Total general": pass
			elif row['Empresa'] == "Total CM": pass
			elif row['Empresa'][0:3] == "1/ ": pass
			elif row['Empresa'][0:3] == "2/ ": pass
			elif row['Empresa'][0:6] == "Nota: ": pass
			else:
				cleaned_row = {}
				atms = 0
				branches = 0
				agents = 0
				cleaned_row['NAME_0'] = "Peru"
				cleaned_row['NAME_1'] = row['Ubicaci\xc3\xb3n: Departamento']
				cleaned_row['NAME_2'] = row['Ubicaci\xc3\xb3n: Provincia']
				cleaned_row['NAME_3'] = row['Ubicaci\xc3\xb3n: Distrito']
				i = row['dir'].find('/') + 1
				i+= row['dir'][i:].find('/') + 1
				j = row['dir'][i:].find('/')
				if j > -1:
					cleaned_row['Type of Institution'] = row['dir'][i:i+j]
				else:
					cleaned_row['Type of Institution'] = row['dir'][i:]
				cleaned_row['Date'] = row['date']
				cleaned_row['Year'] = row['year']
				cleaned_row['Month'] = row['month']
				cleaned_row['Day'] = row['day']
				cleaned_row['Name of Company'] = row['Empresa']
# ASSUMPTION: that my inferences about these Spanish labels are correct (eek)!
				if 'N\xc3\xbamero de Cajeros Autom\xc3\xa1ticos' in row and row['N\xc3\xbamero de Cajeros Autom\xc3\xa1ticos'] != '-' and row['N\xc3\xbamero de Cajeros Autom\xc3\xa1ticos'] != '':
					atms = float(row['N\xc3\xbamero de Cajeros Autom\xc3\xa1ticos'])
				if 'N\xc3\xbamero de Cajeros Corresponsales 1/' in row and row['N\xc3\xbamero de Cajeros Corresponsales 1/'] != '-' and row['N\xc3\xbamero de Cajeros Corresponsales 1/'] != '' and row['N\xc3\xbamero de Cajeros Corresponsales 1/'] > 0:
					agents = float(row['N\xc3\xbamero de Cajeros Corresponsales 1/'])
				if 'N\xc3\xbamero de establecimientos con Cajeros Corresponsales 1/' in row and row['N\xc3\xbamero de establecimientos con Cajeros Corresponsales 1/'] != '-' and row['N\xc3\xbamero de establecimientos con Cajeros Corresponsales 1/'] != '':
					branches = float(row['N\xc3\xbamero de establecimientos con Cajeros Corresponsales 1/'])
				if 'N\xc3\xbamero de Cajeros Corresponsales 2/' in row and row['N\xc3\xbamero de Cajeros Corresponsales 2/'] != '-' and row['N\xc3\xbamero de Cajeros Corresponsales 2/'] != '':
					agents = float(row['N\xc3\xbamero de Cajeros Corresponsales 2/'])
				if agents + branches + atms == 0:
					if 'Codigo Oficina' in row:
						branches = 1
						cleaned_row['Name of Branch'] = row['Empresa'] + "-" + row['Codigo Oficina']
					elif 'C\xc3\xb3digo de oficina' in row:
						branches = 1
						cleaned_row['Name of Branch'] = row['Empresa'] + "-" + row['C\xc3\xb3digo de oficina']
				cleaned_row['FSP Metrics Description'] = "# Locations"
				if atms > 0:
					cleaned_row['Type of Access Point'] = "ATM"
					cleaned_row['FSP Metrics'] = atms
					writer.writerow(cleaned_row)
				if agents > 0:
					cleaned_row['Type of Access Point'] = "Agent"
					cleaned_row['FSP Metrics'] = agents
					writer.writerow(cleaned_row)
				if branches > 0:
					cleaned_row['Type of Access Point'] = "Branch"
					cleaned_row['FSP Metrics'] = branches
					writer.writerow(cleaned_row)
	print_with_timestamp("Run complete.")




def month_int_from_spanish(mes):
	mes = mes.lower() # just to make it case-insenstive
	if mes == 'enero': return 1
	elif mes == 'febrero': return 2
	elif mes == 'marzo': return 3
	elif mes == 'abril': return 4
	elif mes == 'mayo': return 5
	elif mes == 'junio': return 6
	elif mes == 'julio': return 7
	elif mes == 'agosto': return 8
	elif mes == 'septiembre' or mes == "setiembre": return 9 # "setiembre" seems to be a common typo....
	elif mes == 'octubre': return 10
	elif mes == 'noviembre': return 11
	elif mes == 'diciembre': return 12
	else: return None




def make_date_string(y,m,d, sep="-"):
	return str(y) + str(sep) + str(m) + str(sep) + str(d)




def print_with_timestamp(msg):
	print time.ctime() + ": " + msg
	sys.stdout.flush() # explicitly flushing stdout makes sure that a .out file stays up to date - otherwise it can be hard to keep track of whether a background job is hanging



def get_args():
	parser = argparse.ArgumentParser(description="Import and/or update OSM data.")

# positional argument
	parser.add_argument("root_dir", help="required argument: the root directory within which we should find files to parse")

	args = parser.parse_args()
	return args



if __name__ == "__main__":
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	main()
