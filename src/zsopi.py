#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
#	@author github/ZsBT
#	@license WTFPL - www.wtfpl.net
#
########################################

import os.path
from time import sleep
from threading import Thread



class gpiopin:

#	read/write gpio via /sys/class/gpio_sw filesystem for Orange Pi

# examples:
#
# from zsopi import gpiopin
# gpi = gpiopin('PD14')
# gpi.write( 1)
# print( gpi.read() )

# possible pins on orange pi:
# PA0 PA1 PA2 PA3 PA6 PA7 PA8 PA9 PA10 PA13 PA14 PA21  PC4 PC7  PD14  PG6 PG7 PG8 PG9


#                                  physical layout
#
# +-----+-----+----------+------+---+--OrangePiPC--+---+------+---------+-----+--+
# | BCM | wPi |   Name   | Mode | V | Physical | V | Mode | Name     | wPi | BCM |
# +-----+-----+----------+------+---+----++----+---+------+----------+-----+-----+
# |     |     |     3.3v |      |   |  1 || 2  |   |      | 5v       |     |     |
# |   2 |  -1 |    SDA.0 |      |   |  3 || 4  |   |      | 5V       |     |     |
# |   3 |  -1 |    SCL.0 |      |   |  5 || 6  |   |      | 0v       |     |     |
# |   4 |  -1 |     ??   |      |   |  7 || 8  |   |      | TxD3     |     |     |
# |     |     |       0v |      |   |  9 || 10 |   |      | RxD3     |     |     |
# |  17 |  -1 |     RxD2 |      |   | 11 || 12 | 1 | OUT  | IO1 PD14 | 1   | 18  |
# |  27 |  -1 |     TxD2 |      |   | 13 || 14 |   |      | 0v       |     |     |
# |  22 |  -1 |     CTS2 |      |   | 15 || 16 | 1 | OUT  | IO4 PC04 | 4   | 23  |
# |     |     |     3.3v |      |   | 17 || 18 | 0 | OUT  | IO5 PC07 | 5   | 24  |
# |  10 |  -1 |     MOSI |      |   | 19 || 20 |   |      | 0v       |     |     |
# |   9 |  -1 |     MISO |      |   | 21 || 22 |   |      | RTS2     |     |     |
# |  11 |  -1 |     SCLK |      |   | 23 || 24 |   |      | SPI-CE0  |     |     |
# |     |     |       0v |      |   | 25 || 26 |   |      | CE1      |     |     |
# |   0 |  -1 |    SDA.1 |      |   | 27 || 28 |   |      | SCL.1    |     |     |
# |   5 |   7 |  IO7 PA7 |  OUT | 0 | 29 || 30 |   |      | 0v       |     |     |
# |   6 |   8 |  IO8 PA8 |  OUT | 0 | 31 || 32 | 1 | OUT  | IO9 PG08 | 9   | 12  |
# |  13 |  10 | IO10 PA9 |  OUT | 0 | 33 || 34 |   |      | 0v       |     |     |
# |  19 |  12 | IO12PA10 |  OUT | 0 | 35 || 36 | 0 | OUT  | IO13PG09 | 13  | 16  |
# |  26 |  14 | IO14PA20 | ALT3 | 0 | 37 || 38 | 0 | OUT  | IO15PG06 | 15  | 20  |
# |     |     |       0v |      |   | 39 || 40 | 0 | OUT  | IO16PG07 | 16  | 21  |
# +-----+-----+----------+------+---+----++----+---+------+----------+-----+-----+
# | BCM | wPi |   Name   | Mode | V | Physical | V | Mode | Name     | wPi | BCM |
# +-----+-----+----------+------+---+--OrangePIPC--+------+----------+-----+-----+
  PATH = '/sys/class/gpio_sw'
  MODE_IN = 0
  MODE_OUT = 2

  def __init__(self, pin):
    self.PIN = pin
    
  
  # set pin mode to gpiopin.MODE_IN or gpiopin.MODE_OUT
  def mode(self, mode):
    filename = '%s/%s/cfg' % (gpiopin.PATH, self.PIN)
    if not mode in [ gpiopin.MODE_IN, gpiopin.MODE_OUT ]:
      raise Exception('invalid gpio mode')
      
    if os.path.isfile(filename):
      self.MODE = mode
      with open( filename,'w') as fil:        
        return fil.write('%s' % mode)
    raise Exception('pin %s does not exist' % self.PIN)


  # read data, usually 0 or 1
  def read(self):
    filename = '%s/%s/data' % (gpiopin.PATH, self.PIN)
    if os.path.isfile(filename):
      with open( filename,'r') as fil:        
        return fil.read().strip()
    raise Exception('pin %s does not exist' % self.PIN)
    

  # write data, usually 0 or 1
  def write(self, data):
    filename = '%s/%s/data' % (gpiopin.PATH, self.PIN)
    if os.path.isfile(filename):
      self.mode(gpiopin.MODE_OUT)
      with open( filename,'w') as fil:        
        return fil.write('%s' % data)
    raise Exception('self.PIN %s does not exist' % self.PIN)
    



#
#	control on-board LEDs (green or red)
#

# example:

# from zsopi import builtinled
#
# builtinled.on('red')
# builtinled.off('green')

# builtinled.blink('green')
# builtinle.Blinking = False

class builtinled:

  BlinkSpeed1 = 0.5	# ON time
  BlinkSpeed2 = 0.5	# OFF time

  @staticmethod
  def setbrightness(color,content):
    with open("/sys/class/leds/%s_led/brightness" % color,'w') as file:
      file.write(content)
      file.close()

  @staticmethod
  def on(color):
    return builtinled.setbrightness(color,'1')

  @staticmethod
  def off(color):
    return builtinled.setbrightness(color,'0')


  Blinking = False
  
  @staticmethod
  def blink_thread(color):
    builtinled.Blinking = True
    while builtinled.Blinking:
      builtinled.on(color)
      sleep(builtinled.BlinkSpeed1)
      builtinled.off(color)
      sleep(builtinled.BlinkSpeed2)
  
  BlinkThread = None
  @staticmethod
  def blink(color):
    if ( type(builtinled.BlinkThread)!=type(None) ):
      builtinled.Blinking = False
      builtinled.BlinkThread.join()
    builtinled.BlinkThread = Thread(target = builtinled.blink_thread, args=(color,) )
    builtinled.BlinkThread.start()
    
  @staticmethod
  def status(color):
    with open('/sys/class/leds/%s_led/brightness' % color,'r') as file:
      s = file.read()
      file.close()
      return int(s.strip())

  @staticmethod
  def htmlstatus():
    s = ''
    if builtinled.status('green') > 0 :
      s += '<span style="background-color:green">__</span>'
    if builtinled.status('red') > 0 :
      s += '<span style="background-color:red">__</span>'
    return s
    
