#!/usr/bin/env python

import cgi
import cgitb;
cgitb.enable()

from subprocess import call

import MPU6050
import math
import time
import numpy as np
import sys
import time
import datetime
import SDL_DS1307
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook

# Output the headers
print "Content-Type: text/html"		# html content to follow
print 					# blank line, end of headers

def capture_data(InputSampleNumber):
	
	TargetSampleNumber= int(InputSampleNumber)*100
	TargetRate= float(100)
		
	mpu6050 = MPU6050.MPU6050()
	
	mpu6050.setup()
	mpu6050.setGResolution(2)
	mpu6050.setSampleRate(TargetRate)
	mpu6050.enableFifo(False)
	time.sleep(0.01)
	
	ds1307 = SDL_DS1307.SDL_DS1307(1, 0x68)
	#ds1307.write_now()
	
	print "Capturing {0} samples at {1} samples/sec".format(TargetSampleNumber, mpu6050.SampleRate)
		
	mpu6050.resetFifo()
	mpu6050.enableFifo(True)
	time.sleep(0.01)
	#starttime = ds1307.read_datetime()
	starttime = datetime.datetime.now()
	
	Values = []
	Total = 0
	mscounter = int(0)
	counter = []
	
	while True:
		
	 if mpu6050.fifoCount == 0:
	     Status= mpu6050.readStatus()
	
	     # print "Status",Status
	     if (Status & 0x10) == 0x10 :
	        print "Overrun Error! Quitting.\n"
	        quit()
	
	     if (Status & 0x01) == 0x01:
	        Values.extend(mpu6050.readDataFromFifo())
	        mscounter += 10
	 else:
	        Values.extend(mpu6050.readDataFromFifo())
	        mscounter += 10
	        
	 #read Total number of data taken
	 Total = len(Values)/14
	 # print Total
	 if Total >= TargetSampleNumber :
	   break;
	
	 #now that we have the data let's write the files
	if Total > 0:
	  Status = mpu6050.readStatus()
	  # print "Status",Status
	  if (Status & 0x10) == 0x10 :
	    print "Overrun Error! Quitting.\n"
	    quit()
	
	  print "Saving RawData.txt  file."
	  filename = "data/RawData%s.txt" % starttime
	  
	  FO = open(filename,"w")
	  FO.write("Time\tGx\tGy\tGz\tTemp\tGyrox\tGyroy\tGyroz\n")
	  fftdata = []
	  for loop in range (TargetSampleNumber):
	    SimpleSample = Values[loop*14 : loop*14+14]
	    I = mpu6050.convertData(SimpleSample)
	    Timestamp = mscounter - (mscounter-(10*loop))
	    FO.write("{0}\t{1:6.3f}\t{2:6.3f}\t{3:6.3f}\t".format(Timestamp, I.Gx , I.Gy, I.Gz))
	    FO.write("{0:5.1f}\t{1:6.3f}\t{2:6.3f}\t{3:6.3f}\n".format(I.Temperature,I.Gyrox,I.Gyroy,I.Gyroz))
	
	  FO.close()
	
	  print "Saving Data Plot"
	
	  timems = np.genfromtxt(filename, delimiter='\t', dtype=None, usecols=[0], skip_header=1)
	  accx = np.genfromtxt(filename, delimiter='\t', dtype=None, usecols=[1], skip_header=1)
	  accy = np.genfromtxt(filename, delimiter='\t', dtype=None, usecols=[2], skip_header=1)
	  accz = np.genfromtxt(filename, delimiter='\t', dtype=None, usecols=[3], skip_header=1)

	  fig, (ax0, ax1, ax2) = plt.subplots(nrows=3)
	
	  ax0.set_title("Acceleration x-axis")
	  ax0.set_xlabel('Time(ms)')
	  ax0.set_ylabel('g')
	
	  ax0.plot(timems, accx, c='r')
	
	  ax1.set_title("Acceleration y-axis")
	  ax1.set_xlabel('Time(ms)')
	  ax1.set_ylabel('g')
	
	  ax1.plot(timems, accy, c='g')
	
	  ax2.set_title("Acceleration z-axis")
	  ax2.set_xlabel('Time(ms)')
	  ax2.set_ylabel('g')
	
	  ax2.plot(timems, accz, c='b')
	
	  plt.subplots_adjust(hspace=0.8)
	  for label in (ax0.get_yticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels()):
	      label.set_fontsize(10)
	
	  fig.savefig('data/DataPlot%s.png' % starttime, format='png')
	
# here you would possibly print out prettier html. 
# maybe an img src = 
# possibly you don't even write the png, you just output the mime-type directly
# anyway, here is where your output presentation logic goes.
	print "Done!"
	

# Output the content
print """
<html>
	<head>
		<title>Motion Measurement Interface</title>
	</head>
	<body>
		<h1>Motion Measurement Interface</h1>
		<p>Enter a duration time.</p>
		<form method="get" action="foo.py">
			<p>command: <input type="text" name="command"/></p>
		</form>
"""
form = cgi.FieldStorage()
if "command" in form:
    command = form["command"].value
    if command != "" :
        print "<p>You gave duration: " + command + "</p>"
        capture_data(command)
	print """
    </body>
</html>
"""
