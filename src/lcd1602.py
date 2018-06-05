#!/usr/bin/python
#
#	control 1602 LCD (16x2 characters) via i2c
#
#	@author github/ZsBT
#	@license WTFPL

# sudo apt-get install -y python-smbus i2c-tools
# sudo i2cdetect -y 0
# sudo i2cdetect -y 1


import smbus
import time
from syslog import syslog as sylog

LCD_WIDTH = 16   # Maximum characters per line
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # 1st line
LCD_LINE_2 = 0xC0 # 2nd line
LCD_LINE_3 = 0x94 # 3rd line
LCD_LINE_4 = 0xD4 # 4th line

ENABLE = 0b00000100 # Enable bit

E_PULSE = 0.0005
E_DELAY = 0.0005

POSSIBLE_ADDRESSES = [ 0x27, 0x3f ]



class lcd1602:

  BACKLIGHT_ON  = 0x08  # On
  BACKLIGHT_OFF = 0x00  # Off


  def __init__(self, bus=-1, addr=-1 ):	# -1 means autodetect
    self.I2C_BUS = bus
    self.I2C_ADDR  = addr
    self.BACKLIGHT = lcd1602.BACKLIGHT_ON
    self.stdout = False
    
    if addr == -1 :
      ( self.I2C_BUS, self.I2C_ADDR ) = self.deviceSearch( POSSIBLE_ADDRESSES, bus )

    if self.I2C_BUS == -1 :
      raise lcd1602.DeviceNotFound('nothing on POSSIBLE_ADDRESSES' )

    self.bus = smbus.SMBus(self.I2C_BUS)
    self.lcd_init()
    

  def deviceSearch(self, possible_addresses, buses=-1 ):
    if buses == -1:
      buses = [0,1]
      
    for busid in buses:
      bus = smbus.SMBus(busid)
      for device in range(128):
        try:
          bus.read_byte(device)
          if device in possible_addresses :
            return (busid,device)	# device found
        except: # exception if read_byte fails
          pass
    return (-1,-1)	# no device found


  def lcd_init(self):
    # Initialise display
    self.lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    self.lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    self.lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    self.lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
    self.lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    self.clear()
    time.sleep(E_DELAY)


      
  def lcd_byte(self,bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command

    bits_high = mode | (bits & 0xF0) | self.BACKLIGHT
    bits_low = mode | ((bits<<4) & 0xF0) | self.BACKLIGHT

    # High bits
    self.bus.write_byte(self.I2C_ADDR, bits_high)
    self.lcd_toggle_enable(bits_high)

    # Low bits
    self.bus.write_byte(self.I2C_ADDR, bits_low)
    self.lcd_toggle_enable(bits_low)

  def lcd_toggle_enable(self,bits):
    # Toggle enable
    time.sleep(E_DELAY)
    self.bus.write_byte(self.I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    self.bus.write_byte(self.I2C_ADDR,(bits & ~ENABLE))
    time.sleep(E_DELAY)

  def lcd_string(self,message,line):
    message = message.ljust(LCD_WIDTH," ")
    self.lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
      self.lcd_byte(ord(message[i]),LCD_CHR)

  def clear(self):
    self.lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    

  def destroy(self):
    self.clear()
    self.BACKLIGHT = lcd1602.BACKLIGHT_OFF
    self.line1('shut off display')
    self.lcd_byte(0x08, LCD_CMD) # Display Off
    self.lcd_byte(0x01, LCD_CMD)


  def line1(self,message):
    self.lcd_string(message,LCD_LINE_1)
    if self.stdout:
      sylog("%sLCD#1: %s" % ('*' if self.BACKLIGHT==lcd1602.BACKLIGHT_ON else '', message))

  def line2(self,message):
    self.lcd_string(message,LCD_LINE_2)
    if self.stdout:
      sylog("%sLCD#2: %s" % ('*' if self.BACKLIGHT==lcd1602.BACKLIGHT_ON else '', message))



  class DeviceNotFound(Exception):
    ''' there is no 1602 device '''

