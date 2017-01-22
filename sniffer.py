# Simple tool for displaying raw serial data frames sent by the FT-857 TRX or front panel.
# Use a suitable USB<->5V serial adapter and connect it to GND and one of the data lines.
# See doc/hardware.md for details.

# Set this to your serial port:
SERIAL_PORT = '/dev/ttyACM0'

# Show frames with an incorrect checksum?
SHOW_BROKEN_FRAMES = True

import serial
import hexdump
from enum import Enum
import ft857

port = serial.Serial(
	port = SERIAL_PORT,
	baudrate = ft857.BAUDRATE,
	stopbits = serial.STOPBITS_TWO,
	timeout = 1)

class state(Enum):
	start_byte = 1
	length = 2
	data = 3

rx_state = state.start_byte	

while True:
	byte = port.read(1)
	if byte:
		if rx_state == state.start_byte:
			if byte == ft857.RTS:
				rx_state = state.length
				data = byte
			elif not byte in [ft857.POLL, ft857.ACK]:
				if SHOW_BROKEN_FRAMES:
					print 'Unexpected start byte: %s' % byte.encode('hex').upper()
		elif rx_state == state.length:
			length = ord(byte)
			# Q&D: try to fix frames with double start byte.
			# PAN tends to send such from time to time (?)
			# This makes frames with a length of 0xA5 invalid by the way.
			if length == 0xA5:
				print 'Possible problem of the sort \"A5 A5\"'
			else:
				rx_state = state.data
				data += byte
		elif rx_state == state.data:
			# Q&D: try to fix frames corrupted by ACKs.
			# TRX likes to send those when interupted by PAN.
			# Note: A6 06 06 could be valid data but such was not yet seen on the wire.
			#       If it would be transmitted, the checksum error in the next frame would indicate that.
			if len(data) == 2 and length == 6 and ord(byte) == 0x06:
				print 'Possible problem of the sort \"A5 06 06\"'
				rx_state = state.start_byte
			else:
				data += byte
				if len(data) == length + 2:
					if ft857.checksumValid(data):
						ft857.printFrame(data)
					else:
						if SHOW_BROKEN_FRAMES:
							print 'Invalid checksum of frame:'
							hexdump.hexdump(data)
					rx_state = state.start_byte
			
	else:
		# timeout	
		rx_state = state.start_byte
