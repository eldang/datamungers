# Data munging scripts repository

A collection of scripts I've written to automate data munging tasks, which other people may find useful.

## Contact

Eldan Goldenberg, username eldang on twitter, gmail and skype

## Using

Mostly: Python with included libraries. Additional libraries are commented with where to install them from and find documentation

earthquakemap.r & earthquakemaps.r : R with the "mapdata" package, which is available on CRAN.

## Contents

### Scripts that should be usable out of the box

Most of these have additional explanation at the top of the file, clarifying what they were made for and how to use them.

* [aggregate_csv.py](./aggregate_csv.py) - takes a CSV and returns a summary of it, averaged across one field, aggregated by another (e.g. averaging the readings for each time of day across all days).
* [clear_out_of_range.py](./clear_out_of_range.py) - takes a CSV in which some fields are market as suspect by a metadata column, and removes all of those values so only data that the provider trusts is left.
* [earthquakemap.r](./earthquakemap.r) - downloads a snapshot of recent earthquake data from USGS and plots it on a world map.
* [earthquakemaps.r](./earthquakemaps.r) - version of the above that makes a series of frames to be animated, rather than one image containing all the data.
* [NOAAdownloader.py](./NOAAdownloader.py) - downloads historical weather data from NOAA's archive and converts it from an idiosyncratic format into straightforward CSV.  See [http://eldan.co.uk/2012/10/rain-redux/](http://eldan.co.uk/2012/10/rain-redux/) for background and a use example.
* [wordlefeeder.py](./wordlefeeder.py) - takes a CSV file with a list of word frequencies and outputs a text file with each word repeated the listed number of times. [Wordle](http://www.wordle.net/) needs the latter as input.

#### See also

Some related scripts get their own repository for one reason or another:

* [osm_export_import](https://github.com/eldang/osm_export_import) - simple automation of the process of keeping a partial OpenStreetMap mirror up to date. Coming soon: export part, to export arbitrary regions and feature sets from these.

### Fragments

These are generally highly specialised and poorly tested.  They're more likely to be useful to grab parts out of than in their entirety.  See the [fragments](./fragments) subdirectory for sources.

* [parse_excel.py](./fragments/parse_excel.py) - finds all `.xls` files in a directory and its subdirectories, parse them all according to some assumptions about structure, and spit out a huge combined CSV and a smaller one that does some processing on the contents. *The specific assumptions were for a particular dataset, but I expect to recycle a lot of the parts of this, and work it into a more modular, tinkerable form over time*
