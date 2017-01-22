# FT-857D Front Panel Protocol
The following describes the serial protocol between the FT-857D tranceiver and the front panel. It is based on the analysis of __one device__. 

__Work in progress!__ The protocol description is far from being complete and verified! Use at your own risk.



## Communication
Both, the tranceiver (TRX) and the front panel (PAN) may initialize a data transfer. The scheme is:
 1. Sender transmits 0xA5
 2. Receiver replies 0x06 (ACK)
 3. Sender transmits data frame
 4. Receiver replies 0x06 (ACK)

__Example: TRX initiates a data transfer:__
 1. TRX -> PAN: 0xA5
 2. TRX <- PAN: 0x06
 3. TRX -> PAN: [data frame]
 4. TRX <- PAN: 0x06
 
When idle, the TRX sends 0x90 every second. PAN replies with 0x06.

## Data frames
After the initialisation (see above), the data frame is transmitted. It consists of a length byte, a command byte, one or more data bytes and the checksum.

`[1 len] [1 cmd] [len-2 data] [1 checksum]`

* __len__: Number of following bytes (rest of the frame), including checksum byte.
* __cmd__: "Command" byte
* __data__: Command specific data
* __checksum__: 8 bit checksum, the sum of cmd and all data bytes

Example:
`06 91 FF 8F 18 00 37`

## Commands TRX -> PAN
### 0x40 Menu Control
Data: `[0x40] [SubCommand]`

The PAN has most of the menu data locally stored. The content is just selected by the TRX. Some texts and symbols are directly written to the display. All functions seems to be controlled by sub commands.
#### Sub Commands
* `00 00`: Clears the display
* `06 00`: Writes _MENU MODE No_ to the top line
* `07 nn`: With nn = menu number - 1<br>Writes the menu number to the top line and the menu name to the line below.
* `08 00`: Unknown
* `09 nn`: Setting: MAIN/SEL
* `0A nn`: Setting: OFF/ON
* `0B nn`: Setting: ENABLE/DISABLE
* `0C nn`: Setting: 2.5KHz/5KHz/9KHz/10KHz/12.5KHz/25KHz
* `0D nn`: Setting: OFF/1h/2h/3h/4h/5h/6h
* `0E nn`: Setting: OFF/RANGE/ALL
* `10 nn`: Setting: 440Hz/880Hz/1760Hz
* `13 nn`: Setting: OFF/ON
* `14 nn`: Setting: USB/LSB/AUTO
* `15 nn`: Setting: NORMAL/REVERSE
* `16 nn`: Setting: 400Hz/500Hz/600Hz/700Hz/800Hz
* `17 nn`: Setting: 10ms/15ms/20ms/25ms/30ms
* `19 nn`: Setting: N:/A:/AN:
* `1A nn`: Setting: 1:3.0/1:3.1/1:3.2/1:3.3/.../1:4.5
* `1B nn`: Setting: Tn-Rn/Tn-Riv/Tiv-Rn/Tiv-Riv
* `1C nn`: Setting: FINE/COARSE
* `1D nn`: Setting: RTTY-L/RTTY-U/PSK31-L/PSK31-U/USER-L/USER-U
* `1E nn`: Setting: 1/2/3
* `20 nn`: Setting: OFF/AUTO1/AUTO2/ON
* `21 nn`: Setting: OFF/LPF/HPF/BOTH
* `22 nn`: Setting: 60Hz/120Hz/240Hz
* `23 nn`: Setting: 1000Hz/1160Hz/1320Hz/.../6000Hz
* `24 nn`: Setting: 100Hz/160Hz/220Hz/.../940Hz/1000Hz
* `25 nn`: Setting: 5KHz/6.25KHz/10KHz/12.5KHz/15KHz/20KHz/25KHz/50KHz
* `26 nn`: Setting: DIAL/FREQ/PANEL/ALL
* `27 nn`: Setting: PWR/ALC/MOD/SWR/VLT/N_A/OFF
* `2A nn`: Setting: TIME/BUSY/STOP
* `2C nn`: Setting: 4800bps/9600bps/38400bps
* `2D nn`: Setting: 1KHz/2.5KHz/5KHz
* `28 nn`: Setting: CAT/LINEAR/TUNER
* `30 nn`: Setting: 100ms/200ms/.../3000ms
* `31 nn`: Setting: OFF/XVTR A/XVTR B
* `32 nn`: Setting: 1200bps/9600bps/
* `33 nn`: Setting: RF-GAIN/SQL
* `34 nn`: Setting: ELEKEY/MICKEY
* `36 nn`: Setting: NOR/RMT/CAT
* `37 01`: Unknown
* `39 nn`: Setting: SIG/CTR/VLT/N_A/FS/OFF
* `3A nn`: Setting: nn=00 ... 89, List for user keys
* `3B nn`: Setting: CW SIDETONE/CW SPEED/MHZ_MEM GRP/MIC GAIN/NB LEVEL/RF POWER/STEP
* `3C 01`: Unknown
* `3E nn`: Setting: OFF/ATAS(HF)/ATAS(HF&50)/ATAS(ALL)/TUNER
* `4C nn`: Setting: (DCS CODES)
* `4D nn`: Setting: DCS T/R
* `4E 00`: Display the S value in line 0x03.
* `4F nn`: Setting: TONE T/R
* `50 nn`: Setting: TONE Freq.






### 0x41 Display Control
Data: `[0x41] [Line] [Position] [Chars ... ]`

Manipulate the display text and symbols. The display is organized in lines of different text styles and column counts. _Line_ selects the display line (see below), _Position_ the character position within the line where the characters _Chars_ to be placed.

![Display Line Arrangement](images/display_lines.jpg)

 * __Line 0x00__: 19 chars, Top line with symbols and volt meter
 * __Line 0x01__: 20 chars, VFOx/Mem, Mode
 * __Line 0x02__: 12 chars, Frequency <br>
  Position 0 collides with line 0x03. Use 1 or higher.<br> 
  Special characters 0x12: IF shift dot, 0x16/0x17: clar arrow down/up, ...
 * __Line 0x03__: 3 chars, S/MFx area left of frequency line
 * __Line 0x04__: 22 chars, Menu Bar (button labels) <br>
	special character 0x7D: lock symbol
 
Examples:<br>
`41 04 15 7D D7` -> sets the lock symbol<br>
`41 02 01 20 20 35 30 2E 32 34 37 2E 37 37 20 70` -> sets frequency display to "  50.247.77 "

Here is still some work to do! Valid and special characters to be verified. Note that the menu structure works differently from the normal display control.

### 0x43 Display Meter
Data: `[0x43] [Value]`

Value for the on-screen meter, eg. S-meter. Range: 0x00 - 0x64 (=100, full scale). For some reason, the meter aperantly must first be written 0x00 before it accepts higher values correctly.

### 0x45 Cursor
Data: `[0x45] [Line] [Position]`

Places a blinking cursor at the given line and position. Only used (usable) in line 2?

### 0x47 Display Meter Stuff
Data: `[0x47] [...]`

This is a bit of a mystery.

* `47 00 00`: Probably some initialisation for the on-screen meter
* `47 00 40`: Unknown
* `47 00 80`: used for band scope with max width
* `47 00 88`: used for band scope with med width
* `47 00 90`: used for band scope with min width
* `47 03 00`: Peak-hold off
* `47 03 40`: Peak-hold on

### 0x48 Band Scope Data
Data: `[0x48] [X] [Y]`

Data for the on-screen band scope. _X_ range depends on the selected width, _y_ is 0x00 ... 0x64.
Initialisation is a bis tricky, proper method to be investigated.

### 0x4A Display Backlight Control
Data: `[0x4A] [BL0] [BL1]`

Controls the RGB LED backlight of the LC display. 4 bit per color:

Bit   |     7     |     6     |     5     |      4     |     3     |     2     |     1     |     0     
------|-----------|-----------|-----------|------------|-----------|-----------|-----------|----------
BL0   | green MSB | green     | green     | green LSB  | blue MSB  | blue      | blue      | blue LSB
BL1   | ?         | ?         | ?         | ?          | red MSB   | red       | red       | red LSB

### 0x4B LED Control
Data: `[0x4B] [LED]`

Controls the BUSY/TX/CW RGB LED and button backlight.

Bit   |     7     |     6     |     5     |      4     |     3     |     2     |     1     |     0     
------|-----------|-----------|-----------|------------|-----------|-----------|-----------|----------
LED   | Buttons   | 0         | 0         | 0          | /BUSY bl  | 0         | /BUSY gn  | /BUSY rd

Note that the BUSY LED is active low while the button backlight is active high. Trying to set bit 4, 5 or 6 locks up the panel. Function unclear.

Examples:<br>
`4B 89` -> buttons on, green LED on<br>
`4B 8B` -> buttons on, green LED off,

### 0x4C Ext Meter
Data: `[0x4C] [Value]`

Output value for the external analog meter. Depends on the setting of menu 60 "MTR ARX SEL" and 61 "MTR ATX SEL". Range: 0x00 - 0xFF


### 0x4D Display Contrast
Data: `[0x4D] [Contrast]`

LC Display contrast 0x03 ... 0x0F 


## Commands PAN -> TRX
### 0x91 Buttons
Data: `[0x91] [Btn0] [Btn1] [Btn2] [Btn3]`

A change in the set of buttons triggers a data frame, containing all button states. If a button is pressed, the corresponding bit is 0. __Btn3__ seems to be always 0x00 but might have a special function. HP bit is 0 if the headphone jack is in use.

Bit   |     7     |     6     |     5     |      4     |     3     |     2     |     1     |     0     
------|-----------|-----------|-----------|------------|-----------|-----------|-----------|----------
Btn0  | MODE <    | MODE >    | BAND DWN  | BAND UP    | FUNC      | V/M       | LOCK      | DSP
Btn1  | HP (in)   | 0         | 0         | 0          | HOME      | A         | B         | C
Btn2  | 0         | 0         | 0         | SELECT     | CLA       | 0         | 0         | 0

Example: 
 * __A__ pressed, no headphones connected: `06 91 FF 8B 18 00`
 * __A__ released again: `06 91 FF 8F 18 00`

The same data is being sent as command __0x9A__ during startup. Maybe a button query reply?
 
### 0x92 Dial
Data: `[0x92] [Direction] [Steps]`

This frame is sent, when the __main dial__ is operated.
 * __Direction__: __0x00 for clockwise__ or __0x80 for counterclockwise__
 * __Steps__: Number of steps since the last transmission. 0x01 when operated very slowly, higher values up to ~0x06 when operated really fast. 
 
### 0x93 Select
Data: `[0x93] [Direction] [Steps]`
 
This frame is sent, when the __select knob__ is operated.
Works like the main dail (0x92 above). Knob presses are sent using the buttons-method (0x91).

### 0x95 SQL/RF
Data: `[0x95] [Value]`

Sent on change of the SQL/RF knob setting. Value range 0x00 ... 0xFF.

### 0x97 Volume
Data: `[0x97] [Volume]`

Sent on change of the VOL knob setting. Volume range 0x00 ... 0xFF.


# Sharing
This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
Thomas Kottek 2017
