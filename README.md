# Yaesu FT-857D front panel protocol 
Goal of this project is to explore the undocumented serial protocol, that connects the FT-857D tranceiver and its front panel and create simple tools to control both, the radio tranceiver and the front panel.

## Why?
Knowing the protocol enables us, for exmple, to
 * Establish a remote connection
 * Develop additional or replacement displays or control panels
 * Add features to the radio
  * Band plan display
  * Simultanous QRG and label display
 * Modify the menu structure
  * Add custom menu items
  * Pretty labels for the custom MFq function keys
 
Also because I personally do not like undocumented protocols. And for the fun of it.

## Docs
See [doc/](doc/) for the work-in-progress protocol documentation.

# Take care!
Although the FT857´s front panel serial port hardware seems to be very well protected against over voltage and short circuit, take care not to damage your hardware. Playing around with the serial protocol, especially transmitting own data frames, may lead to unpredictable behavior of the tranceiver. It is even possible to key the transmitter that way. Also, changes of the calibration data or even a complete lockup might be possible. Make sure you have at least an EEPROM backup, including the soft calibration data.

Note that the documentation ist far from being complete and probably contains errors.

Use everything at your own risk. 

And have a lot of fun!
