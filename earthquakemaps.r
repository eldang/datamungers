# Script to download USGS earthquake data and plot it on a world map
# Written by Eldan Goldenberg, February 2013
# http://eldan.co.uk/ ~ @eldang ~ eldang@gmail.com
# requires "mapdata" library

# This program is free software; you can redistribute it and/or
#  	modify it under the terms of the GNU General Public License
#		as published by the Free Software Foundation; either version 2
#		of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
#		but WITHOUT ANY WARRANTY; without even the implied warranty of
#		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#		GNU General Public License for more details.
# The licence text is available online at:
#		http://www.gnu.org/licenses/gpl-2.0.html

# Background:
# Downloads recent earthquake data from USGS's public repository, and plots it
# on a world map in a format I find useful.  Originally a class exercise;
# hopefully easy enough to tailor to your requirements
# See http://www.flickr.com/photos/eldan/8456517923/in/photostream/lightbox/ for example output

# USE:
# Just run it, after installing the "mapdata" library if you don't already have that.
# You'll also need the "mapproj" library if you want to use a projection other than the default Mercator, but you don't need it for the defaults I'm using
# The first few lines of code define constants that help tune the output

# SEE ALSO: earthquakemap.r, which uses the same data but saves one image, containing all the earthquakes in the downloaded data.

# TODO: get the timestamps at top and bottom into the same damn time zone!

# YouTube & Vimeo resolutions (at least when exporting from iMovie): 1920x1080, 1280x720, 720x540, 640x480

# this bit is specific to my machine!  
# Comment it out if I forget to, or change it to fit requirements
# setwd("/Users/eldan/Documents/data_files/earthquakes/")

# How many days do we want in one frame?
datewindow = 7

# How many hours do we want to increment between frames?
stepsize = 1

# set some constants to get the sizes of image elements right relative to each other  If you change the image size you may well have to tweak the others a little.
imagewidth <- 1920 # using my monitor size as an OK default. The rest should scale reasonably from this
aspectratio <- 1940/1080 # keep <2 to have space for titles
magnifier <- imagewidth * 0.0002 # multiply point sizes by this to get something reasonably in scale with the image
magnifier.text <- imagewidth / 800

# remind user where the files will end up
print(paste("Current working directory is", getwd()))

# set URL to download from. See http://earthquake.usgs.gov/earthquakes/feed/ for USGS's direct options
# or use the following for my scraperwiki store, which has been aggregating all M1+ events since Feb 12th 2013 (USGS only makes the latest week of this available by default at any one time)
sourceURL <- "https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=csv&name=earthquakes&query=select+*+from+`swdata`&apikey="

# Store today's date and construct local filename from it
now <- Sys.time() # this is probably a bit belt-and-suspenders, but storing a specific moment to call "now" so that time delays don't get blurred by the time taken for the script to run
today <- as.Date(now)
fname <- paste0("earthquakeData", today, ".csv")

# Download the data and read it in to R
download.file(sourceURL, destfile=fname, method="curl")
print(paste0("Data file saved as ", getwd(), "/", fname))
eData <- read.csv(fname)

# Optional checks that the data look reasonable - just comment/uncomment whatever is helpful
# print(dim(eData))
# print(names(eData))
# print(sapply(eData[1,],class)) # this is how to get the class of each column in the data frame
# print(str(eData))
# print(head(eData))
# print(summary(eData)) # frequency counts for factors (most common 6 levels + "other"); quartiles for numeric/integer columns

library(mapdata) # like the built-in maps but has higher resolution outlines

makeframe <- function(eData, framenum) {
  # set up the file output
  fname.image <- paste0(today, "/earthquakeMap_", framenum, ".png")
  png(file=fname.image, height=imagewidth/aspectratio, width=imagewidth)
  
  # world2 has the Pacific at the centre; feels more intuitive for earthquakes given the Ring of Fire
  # world2Hires is the high res version from mapdata
  # The first call puts national boundaries in in grey; the second draws coasts in black
  # the ylim argument cuts out the areas most severely distorted by the Mercator projection, which happen also to get very few earthquakes, while keeping in enough that all outlines are clearly recognisable
  map("world2Hires", col="gray", resolution=1, interior=TRUE, mar=c(0,0,3,0), ylim=c(-90,84)) 
  map("world2Hires", col="black", resolution=1, interior=FALSE, add=TRUE) 
  
  # An artefact of centering the map on longitude 180 is that there are no negative longitudes in the frame, so we have convert the longitudes from the data to the range [0,360)
  longitude.adjusted <- (eData$Longitude + 360) %% 360 
  
  # calculate point sizes from magnitudes; this scale feels more intuitive than a linear transform of the Richter scale (which is logarithmic, after all)
  magnitude.adjusted <- sqrt(exp(eData$Magnitude))*magnifier
  
  # calculate appropriate brightness values for the points based on their recency
  timestamps <- strptime(eData$DateTime, format="%Y-%m-%dT%H:%M:%S")
  recency <- as.double(difftime(now, timestamps, units="hours"))
  recency <- recency - min(recency)
  recency <- 1 - recency / (min(recency) + datewindow*24)
#   print(summary(recency))
  
  # add points to the map for all earthquakes in the file
  points(longitude.adjusted, eData$Latitude, pch=19, cex=magnitude.adjusted, col=rgb(1, 0, 0, recency))
  
  # add legends
  magnitude.samples = seq(1,8,1)
  legend(0, -90, magnitude.samples, pt.cex=sqrt(exp(magnitude.samples))*magnifier, title="Magnitude", col=rgb(1,0,0,0.8), pch=19, xjust=0, yjust=0, bg=rgb(1,1,1,0.75), horiz=TRUE, cex=magnifier.text, text.width=magnifier.text*2.6, adj=0.7)
  
  recency.samples = seq(0,datewindow,ceiling(datewindow/7))
  legend(360, -90, recency.samples, pt.cex=sqrt(exp(5))*magnifier, title="Recency (days before snapshot)", col=rgb(1,0,0,1-recency.samples/datewindow), pch=19, xjust=1, yjust=0, bg=rgb(1,1,1,0.75), horiz=TRUE, cex=magnifier.text, text.width=magnifier.text*2, adj=0.4) 

  # add title and source info
  title(main=paste("M1 or greater earthquakes between", format(min(timestamps), "%b %d, %Y %H:%M"), "and", format(max(timestamps), "%b %d, %Y %H:%M"), "UTC"), xlab=paste("       Image generated at", format(Sys.time(),"%b %d, %Y %H:%M %Z"),"\nData URL:",sourceURL,"\nPrimary source: USGS http://earthquake.usgs.gov/earthquakes/feed/"), cex.main=magnifier.text*1.25, cex.sub=magnifier.text*0.9, cex.lab=magnifier.text*0.9)
  
  dev.off()
  
  print(paste0("Map saved as ", getwd(), "/", fname.image))
}

# make sure we have somewhere to save all the frames together
newdir <- paste("mkdir", today)
system(newdir)

# prepare to subset the data to generate individual images
timestamps <- strptime(eData$DateTime, format="%Y-%m-%dT%H:%M:%S")
# print(summary(timestamps))
recency <- as.double(difftime(now, timestamps, units="hours"))
# print(summary(recency))
recency <- recency - min(recency)
# print(summary(recency))
oldest <- ceiling(max(recency)-1)

for (i in seq(oldest, 0, 0-stepsize)) {
# for (i in seq(240, 120, 0-stepsize)) {
  inwindow <- ((recency >= i) & (recency <= i + datewindow*24))
#   print(i)
  eData.window <- eData[inwindow,]
  makeframe(eData.window, oldest-i)
}

