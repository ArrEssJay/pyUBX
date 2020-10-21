from enum import IntEnum
"""Various tables collected from the datasheet."""

# map gnssId to GNSS string. §31.6
class GNSS_Identifiers(IntEnum):
    GPS = 0,
    SBAS = 1,
    Galileo = 2,
    BeiDou = 3,
    IMES = 4,
    QZSS = 5,
    GLONASS = 6

class Nav_Subframes(IntEnum):
    GPS_LNAV = 0,
    GPS_CNAV = 1

#GPS CNAV
class GPS_CNAV_Msg_IDs(IntEnum):
    Ephemeris_1 = 10,
    Ephemeris = 11,
    Reduced_Almanac = 12,
    Clock_Differential_Correction = 13,
    Ephemeris_Differential_Correction = 14,
    Text = 15,
    Clock_And_IONO_Group_Delay = 16,
    Clock_And_Reduced_Almanac = 17,
    Clock_And_EOP = 18,
    Clock_And_UTC = 19,
    Clock_And_Differential_Correction = 20,
    Clock_And_GGTO = 21,
    Clock_And_Text = 22,
    Clock_And_Midi_Almanac = 23
