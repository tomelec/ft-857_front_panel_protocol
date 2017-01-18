# FT-857D Front Panel Hardware
Some basic information on the hardware. For details please refer to the service manual.

## Connector TRX <-> PAN
Tranceiver and front panel both use a __RJ12 6P6C__ jack and a straight cable.

Pin |  Signal         | Remarks
----|-----------------|-------------------------------------------------
1   | Audio			      | Audio amp output for headphones or ext. speaker
2   | Power button    | Only connected to the TRX, not the panels uC
3   | GND             |
4   | 8V              | TO DO: measure current draw
5   | Data TRX->PAN   |
6   | Data PAN->TRX   |

__Hint__: RJ12 plugs do fit in RJ45 couplers -> Easy, non-destructive way to sniff the signal.


## Serial
This is a standard UART. The data lines operate at __5V__ logic level.

The bitrate is __62 kBit/s__.
 
