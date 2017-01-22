# Simple module to control the FT-857's front panel and analyze the protocol.
# This is intended to play around with the protocol, not to build applications on top of it ;)
# Can easily be used interactively in python, like:
#		>>import ft857
#		>>pan = ft857.frontPanel('/dev/ttyUSB0')
#		>>pan.setBacklight(0,15,0)

import serial
import time
import hexdump

DEFAULT_PORT = '/dev/ttyACM0'
BAUDRATE = 62000

# Commands
MENU_CTL = 0x40
DISPLAY_CTL = 0x41
METER_CTL = 0x43
CURSOR = 0x45
BACKLIGHT_CTL = 0x4A
LED_CTL = 0x4B
EXT_METER_CTL = 0x4C
CONTRAST_CTL = 0x4D
START_BYTE = 0xA5

# Handshake bytes
ACK = '\x06'
RTS = '\xa5'
POLL = '\x90'

# Rate limiting delay for serial data tx
DELAY = 0.05

# Some display content to start with
displayContent = { 0: ' '*19, 1: ' '*20, 2: ' '*12,	3: '   ',	4: ' '*22 }
# Example:
#displayContent = {
#	0: '              13.5V',
#	1: 'M-123 CW            ',
#	2: '  144.300.00 ',
#	3: '   ', 
#	4: '  SPOT   BK    \x0cKYR   '
#}

def checksumValid(data):
	cs = 0
	for byte in data[2:len(data)-1]:
	 cs += ord(byte)
	cs &= 0xFF
	return cs == ord(data[len(data)-1])


def buildChecksum(data):
	cs = 0
	for byte in data:
		cs += ord(byte)
	cs &= 0xFF
	return cs


def printFrame(data):
	# At this point we are pretty sure to have a valid frame
	# The format is: [A5] [1 len] [1 cmd] [len-2 data] [1 checksum]
	lengh = ord(data[1])
	cmd = ord(data[2])

	# Remove start byte, length and checksum
	data = data[2:len(data)-1]

	# Display Control
	if cmd == DISPLAY_CTL:
		line = ord(data[1])
		position = ord(data[2])
		chars = data[3:]
		if line in displayContent.keys():
			current_text = displayContent[line]
			displayContent[line] = displayContent[line][:position] \
				+	chars \
				+ displayContent[line][(position + len(chars)):]
			print 'DISPLAY:', displayContent
		else:
			print 'DISPLAY: invalid line', line

	# Meter Value
	elif cmd == METER_CTL:
		if len(data) == 2:
			print 'METER: value=0x%X' % ord(data[1])
		else:
			print 'METER: unknonw length:'
			hexdump.hexdump(data)

	# Cursor
	elif cmd == CURSOR:
		if len(data) == 3:
			print 'CURSOR: line=0x%X, position=0x%X' % (ord(data[1]), ord(data[2]))
		else:
			print 'CURSOR: unknonw length:'
			hexdump.hexdump(data)

	# Backlight
	elif cmd == BACKLIGHT_CTL:
		if len(data) == 3:
			print 'BACKLIGHT: bl0=0x%X, bl1=0x%X' % (ord(data[1]), ord(data[2]))
		else:
			print 'BACKLIGHT: unknonw length:'
			hexdump.hexdump(data)

	# LED Control
	elif cmd == LED_CTL:
		if len(data) == 2:
			print 'LED: value=0x%X' % ord(data[1])
		else:
			print 'LED: unknonw length:'
			hexdump.hexdump(data)

	# Ext Meter Value
	elif cmd == EXT_METER_CTL:
		if len(data) == 2:
			print 'EXT METER: value=0x%X' % ord(data[1])
		else:
			print 'EXT METER: unknonw length:'
			hexdump.hexdump(data)
	
	# Contrast Setting
	elif cmd == CONTRAST_CTL:
		if len(data) == 2:
			print 'CONTRAST: value=0x%X' % ord(data[1])
		else:
			print 'CONTRAST: unknonw length:'
			hexdump.hexdump(data)
		
	# Not yet implemented command
	else:
		hexdump.hexdump(data)


class frontPanel():

	def __init__(self, port=DEFAULT_PORT):
		self.serialPort = serial.Serial(
			port = port,
			baudrate = BAUDRATE,
			stopbits = serial.STOPBITS_TWO,
			timeout = 1)

		# Check if the panel is ready.
		# First start this function, then apply power to the panel! 
		self.prepareTx()

	def receive(self):
		self.serialPort.reset_input_buffer()
		self.serialPort.write(ACK)
		dataLen = self.serialPort.read(1)
		if not dataLen:
			print 'receive(): timeout'
			return
		# For some reason, we often receive another 0xa5
		if dataLen == '\xa5':
			dataLen = self.serialPort.read(1)
			if not dataLen:
				print 'receive(): timeout'
				return
		data = self.serialPort.read(ord(dataLen))
		self.serialPort.write(ACK)
		import hexdump
		hexdump.hexdump(data)

	def prepareTx(self):
		self.serialPort.reset_input_buffer()
		while True:
			self.serialPort.write(POLL)
			if self.serialPort.in_waiting:
				reply = self.serialPort.read_all()
				if RTS in reply:
					self.receive()
				elif ACK in reply:
					return
			time.sleep(DELAY)

	def send(self, data):
		self.prepareTx()
		cs = buildChecksum(data)
		dataLen = len(data) + 1
		txString = chr(dataLen) + data + chr(cs)
		self.serialPort.write(RTS)
		reply = self.serialPort.read(1)
		if not reply:
			print 'send(): timeout'
		else:
			if not reply == ACK:
				print 'send(): Expected ACK for RTS, got', reply.encode('hex')
		print 'Sending:'
		hexdump.hexdump(txString)
		self.serialPort.write(txString)
		reply = self.serialPort.read(1)
		if not reply:
			print 'send(): timeout'
		else:
			if reply == ACK:
				print 'OK, got ACK'
			else:
				print 'send(): Expected ACK for data, got', reply.encode('hex')
				# FIXME: Add retransmit
	
	def setContrast(self, contrast=0x07):
		if contrast < 0x03:
			contrast = 0x03
		elif contrast > 0x0f:
			contrast = 0x0f
		self.send(chr(CONTRAST_CTL)+chr(contrast))

	def setBacklight(self, r=0, g=0, b=0):
		bl0 = ( (g & 0x0f) << 4 ) | ( b & 0x0f)
		bl1 = r & 0x0f
		self.send(chr(BACKLIGHT_CTL)+chr(bl0)+chr(bl1))

	def clearDisplay(self):
		#clears the text content
		self.send(chr(MENU_CTL)+'\x00\x00')

	def initDisplay(self):
		# Stuff the dislplay likes after power on
		self.send('\x47\x00\x00')
		self.send(chr(METER_CTL)+chr(0x00))

	def printLine(self, line, position, string):
		self.send(chr(DISPLAY_CTL)+chr(line)+chr(position)+string)
		# FIXME: This is ugly. Sending invalid data easily causes the panel to stop responding.
		# A few checks on the parameters would be nice!
		

if __name__ == '__main__':
	pan = frontPanel()
	
	pan.setContrast(7)	
	pan.setBacklight(0,15,0)
	pan.initDisplay()
	pan.send(chr(MENU_CTL)+'\x00\x00')
	pan.clearDisplay()
	
	pan.printLine(0,0,'FT-857D FRONT PANEL')
	pan.printLine(1,4,'Hello')
	pan.printLine(2,5,'World!')

#	for n in range(0,100,5):
#		pan.send(chr(METER_CTL)+chr(n))
#		time.sleep(DELAY)
