#!/usr/bin/python

import MPU6050
import math
import time
import numpy as np
import sys
import time
import datetime
import SDL_DS1307
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
#from measure import argv

InputSampleNumber = command

#TargetSampleNumber= 1024
#TargetRate =  33    # frequency =  8000 / ( integr value + 1)  minimum frequency=32,25

#InputSampleRate=raw_input("Sample Rate(32.25 ... 2000) ?")
#InputSampleNumber=raw_input("How many seconds ?")    

TargetSampleNumber= int(InputSampleNumber)*100
TargetRate= float(100)



mpu6050 = MPU6050.MPU6050()

mpu6050.setup()
mpu6050.setGResolution(2)
mpu6050.setSampleRate(TargetRate)
mpu6050.enableFifo(False)
time.sleep(0.01)

ds1307 = SDL_DS1307.SDL_DS1307(1, 0x68)
ds1307.write_now()
#ds1307._write(0x07, 0x10)

print "Capturing {0} samples at {1} samples/sec".format(TargetSampleNumber, mpu6050.SampleRate)

#raw_input("Press enter to start")

mpu6050.resetFifo()
mpu6050.enableFifo(True)
time.sleep(0.01)
starttime = ds1307.read_datetime()

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
  
  FO = open("RawData%s.txt" % starttime,"w")
  FO.write("Time\tGx\tGy\tGz\tTemp\tGyrox\tGyroy\tGyroz\n")
  fftdata = []
  for loop in range (TargetSampleNumber):
    SimpleSample = Values[loop*14 : loop*14+14]
    I = mpu6050.convertData(SimpleSample)
    Timestamp = mscounter - (mscounter-(10*loop))
    #fftdata.append(CurrentForce)
    FO.write("{0}\t{1:6.3f}\t{2:6.3f}\t{3:6.3f}\t".format(Timestamp, I.Gx , I.Gy, I.Gz))
    FO.write("{0:5.1f}\t{1:6.3f}\t{2:6.3f}\t{3:6.3f}\n".format(I.Temperature,I.Gyrox,I.Gyroy,I.Gyroz))

  FO.close()

##  print "Creating Data Plot"
##
##  fourier = numpy.fft.fft(fftdata)
##
  print "Saving Data Plot"

  timems = np.genfromtxt('RawData%s.txt' % starttime, delimiter='\t', dtype=None, usecols=[0], skip_header=1)
  accx = np.genfromtxt('RawData%s.txt' % starttime, delimiter='\t', dtype=None, usecols=[1], skip_header=1)
  accy = np.genfromtxt('RawData%s.txt' % starttime, delimiter='\t', dtype=None, usecols=[2], skip_header=1)
  accz = np.genfromtxt('RawData%s.txt' % starttime, delimiter='\t', dtype=None, usecols=[3], skip_header=1)
  
##  print "{0}".format(accz)

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

  plt.show()
  fig.savefig('DataPlot%s' % starttime)
##  
##  FO = open("FFTData.txt","w")
##  fftData = numpy.abs(fourier[0:len(fourier)/2+1])/TargetSampleNumber
##  frequency = []
##  FO.write( "Frequency\tFFT\n")
##  Peak=0
##  PeakIndex=0;
##  for loop in range(TargetSampleNumber/2 +1):
##    frequency.append( loop * TargetRate/ TargetSampleNumber)
##    FO.write("{0}\t{1}\n".format(frequency[loop],fftData[loop]))
##    if loop>0:
##       if fftData[loop] > Peak :
##         Peak=fftData[loop]
##         PeakIndex=loop

  #print "Peak at {0}Hz = {1}".format(frequency[PeakIndex],Peak)
   

print "Done!"
