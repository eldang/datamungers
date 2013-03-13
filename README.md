# Data munging scripts repository

A collection of scripts I've written to automate data munging tasks, which other people may find useful.

## Contact

Eldan Goldenberg, username eldang on twitter, gmail and skype

## Using

Mostly: Python with included libraries.
earthquakemap.r & earthquakemaps.r : R with the "mapdata" package, which is available on CRAN.

## Contents

* earthquakemap.r - downloads a snapshot of recent earthquake data from USGS and plots it on a world map.
* earthquakemaps.r - version of the above that makes a series of frames to be animated, rather than one image containing all the data.
* NOAAdownloader.py - downloads historical weather data from NOAA's archive and converts it from an idiosyncratic format into straightforward CSV.  See [http://eldan.co.uk/2012/10/rain-redux/](http://eldan.co.uk/2012/10/rain-redux/) for background and a use example.
* wordlefeeder.py - takes a CSV file with a list of word frequencies and outputs a text file with each word repeated the listed number of times. [Wordle](http://www.wordle.net/) needs the latter as input.
