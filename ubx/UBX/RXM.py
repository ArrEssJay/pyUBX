"""Monitoring Messages: Communication Status, CPU Load, Stack Usage, Task Status. """

from ubx.UBXMessage import initMessageClass, addGet
from ubx.Types import CH, U, U1, U2, U4, X1, X4, R8, I1, R4, E1
from ubx.Tables import GNSS_Identifiers
from .SFRBX import SFRBX

@initMessageClass
class RXM:
    """Message class RXM."""

    _class = 0x02

    @addGet
    class SFRBX:

        _id = 0x13

        class Fields:
            gnssId = E1(1, intEnumType=GNSS_Identifiers)
            svId = U1(2) # gnssId:svId numbering
            reserved0 = U1(3)
            freqId = U1(4) #Only used for GLONASS: This is the frequency slot + 7 (range from 0 to 13)
            numWords = U1(5) #The number of data words contained in this message (up to 10, for currently supported signals)
            chn = U1(6) # The tracking channel number the message was received on
            version = U1(7, allowed={2: "SFRBX v2"}) # Message version, (0x02 for this version)
            reserved1 = U1(8)
            class Repeated:
                dwrd = U4(1) #data words, repeated numWords times

        @property
        def words(self):
            words = [0]*self.numWords
            for i in range(self.numWords):
                #data = data | self.__getattribute__(f'dwrd_{word+1}') << 32*(word)
                words[i] = self.__getattribute__(f'dwrd_{i+1}')
            return words

        @property
        def parsed(self):
            return SFRBX(self.words, self.gnssId, self.svId, self.freqId, self.chn)


    @addGet
    class RAWX:

        _id = 0x15

        class Fields:
            rcvTow = R8(1) #Measurement time of week
            week = U2(2) #GPS Week Number
            leapS = I1(3) #GPS Leap Seconds
            numMeas = U1(4) #numMeas
            recStat = X1(5, masks={'leapSec':0x1,'clkReset':0x2}) # Flags: Leap Seconds Determined, Clock Reset
            version = U1(6, allowed={2: "RAWX v1"}) #Message version (0x01)
            reserved0_0 = U1(7) # The tracking channel number the message was received on
            reserved0_1 = U1(8) # The tracking channel number the message was received on
            class Repeated:
                prMes = R8(1) #Pseudorange
                cpMes = R8(2) #Carrier Phase cycles
                doMes = R4(3) #Doppler Measurement
                gnssId = E1(4, intEnumType=GNSS_Identifiers) #gnssId
                svId = U1(5)
                sigId = U1(6)
                freqId = U1(7)
                locktime = U2(8)
                cno = U1(9)
                prStdev = X1(10, masks={'prStdev':0xF})
                cpStdev = X1(11, masks={'cpStdev':0xF})
                doStdev = X1(12, masks={'doStdev':0xF})
                trkStat = X1(13, masks={'prValid':0x1, 'cpValid':0x2, 'halfCyc':0x4, 'subHalfCyc':0x8})
                reserved1 = U1(14)

       # Transform into a more readable object
        @property
        def frame(self):

            frame = {
            'rcvTow' : self.rcvTow,
            'week' : self.week,
            'leapS' : self.leapS,
            'numMeas' : self.numMeas,
            'leapSecDetermined' : bool( self.recStat['leapSec']),
            'clkReset' : bool( self.recStat['clkReset'])
            }
            frame['measurements'] = [
                {
                    'prMes' : self.__getattribute__(f'prMes_{i}'),
                    'cpMes' : self.__getattribute__(f'cpMes_{i}'),
                    'doMes' : self.__getattribute__(f'doMes_{i}'),
                    'gnssId' : self.__getattribute__(f'gnssId_{i}'),
                    'svId' : self.__getattribute__(f'svId_{i}'),
                    'sigId' : self.__getattribute__(f'sigId_{i}'),
                    'freqId' : self.__getattribute__(f'freqId_{i}'),
                    'locktime' : self.__getattribute__(f'locktime_{i}'),
                    'prStdev' : self.__getattribute__(f'prStdev_{i}')['prStdev'],
                    'cpStdev' : self.__getattribute__(f'cpStdev_{i}')['cpStdev'],
                    'doStdev' : self.__getattribute__(f'doStdev_{i}')['doStdev'],
                    'prValid' :  bool(self.__getattribute__(f'trkStat_{i}')['prValid']),
                    'cpValid' :  bool(self.__getattribute__(f'trkStat_{i}')['cpValid']),
                    'halfCyc' :  bool(self.__getattribute__(f'trkStat_{i}')['halfCyc']),
                    'subHalfCyc' :  bool(self.__getattribute__(f'trkStat_{i}')['subHalfCyc'])
                }
                for i in range(1,self.numMeas+1)
            ]
            return frame