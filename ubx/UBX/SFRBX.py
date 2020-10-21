#Decodes Ublox SFRBX Ephemeris/Almanac Subframes
from ubx.Tables import GNSS_Identifiers, Nav_Subframes, GPS_CNAV_Msg_IDs

GPS_L1CA_PREAMBLE = 0x8b

class GPS_CNAV:
  def __init__(self,words):
    self.words = words
    self.preamble = self.words[0] >> 24

class GPS_LNAV:
  def __init__(self,words):
    self.preamble = self.words[0] >> 24
    self.msgid = (words[0] >> 12) & 0x3f
    self.prn = (words[0] >> 18) & 0x3f

class SFRBX:

  def __init__(self,words, gnssId, svId, gloFreqId, chn):
    self.words = words
    self.gnssId = gnssId
    self.svId = svId
    self.gloFreqId = gloFreqId
    self.chn = chn
    self.subframeType = None
    self.subframe = None

    if self.gnssId == GNSS_Identifiers.GPS:
      # GPS
      preamble = self.words[0] >> 24
      if preamble == GPS_L1CA_PREAMBLE:
        self.subframeType = Nav_Subframes.GPS_CNAV
        self.subframe = GPS_CNAV(self.words)
      else:

          # IS-GPS-200, Figure 20-2
          # LNAV-L, from sat is 10 words of 30 bits
          # from u-blox each of 10 words right aligned into 32 bits
          #             plus something in top 2 bits?
          preamble = words[0] >> 22
          subframe = (words[1] >> 8) & 0x07
          s += ("\n  LNAV-L: preamble %#x TLM %#x ISF %u" %
                (preamble, (words[0] >> 8) & 0xffff,
                 1 if (words[0] & 0x40) else 0))

          s += ("\n  TOW17 %u Alert %u A-S %u Subframe %u" %
                (unpack_u17(words[1], 13) * 6,
                 1 if (words[0] & 0x1000) else 0,
                 1 if (words[0] & 0x800) else 0,
                 subframe))

          if 1 == subframe:
              # not well validated decode, possibly wrong...
              # [1] Figure 20-1 Sheet 1, Table 20-I
              # WN = GPS week number
              # TGD = Group Delay Differential
              # tOC = Time of Clock
              # af0 = SV Clock Bias Correction Coefficient
              # af1 = SV Clock Drift Correction Coefficient
              # af2 = Drift Rate Correction Coefficient
              ura = (words[2] >> 14) & 0x0f
              c_on_l2 = (words[2] >> 18) & 0x03
              iodc = ((((words[2] >> 6) & 0x03) << 8) |
                      (words[7] >> 24) & 0xff)
              s += ("\n   WN %u Codes on L2 %u (%s) URA %u (%s) "
                    "SVH %#04x IODC %u" %
                    (words[2] >> 20,
                     c_on_l2, index_s(c_on_l2, self.codes_on_l2),
                     ura, index_s(ura, self.ura_meters),
                     (words[2] >> 8) & 0x3f, iodc))
              # tOC = Clock Data Reference Time of Week
              s += ("\n   L2 P DF %u TGD %e tOC %u\n"
                    "   af2 %e af1 %e af0 %e" %
                    ((words[2] >> 29) & 0x03,
                     unpack_s8(words[6], 6) * (2 ** -31),
                     unpack_u16(words[7], 6) * 16,
                     unpack_s8(words[8], 22) * (2 ** -55),
                     unpack_s16(words[8], 6) * (2 ** -43),
                     unpack_s22(words[9], 8) * (2 ** -31)))

          elif 2 == subframe:
              # not well validated decode, possibly wrong...
              # [1] Figure 20-1 Sheet 1, Tables 20-II and 20-III
              # IODE = Issue of Data (Ephemeris)
              # Crs = Amplitude of the Sine Harmonic Correction
              #       Term to the Orbit Radius
              # Deltan = Mean Motion Difference From Computed Value
              # M0 = Mean Anomaly at Reference Time
              # Cuc = Amplitude of the Cosine Harmonic Correction
              #       Term to the Argument of Latitude
              # e = Eccentricity
              # Cus = Amplitude of the Sine Harmonic Correction Term
              #       to the Argument of Latitude
              # sqrtA = Square Root of the Semi-Major Axis
              # tOE = Reference Time Ephemeris
              s += ("\n   IODE %u Crs %e Deltan %e M0 %e"
                    "\n   Cuc %e e %e Cus %e sqrtA %f"
                    "\n   tOE %u" %
                    (unpack_u8(words[2], 22),
                     unpack_s16(words[2], 6) * (2 ** -5),
                     unpack_s16(words[3], 14) * (2 ** -43),
                     # M0
                     unpack_s32s(words[4], words[3]) * (2 ** -31),
                     unpack_s16(words[5], 14) * (2 ** -29),
                     unpack_u32s(words[6], words[5]) * (2 ** -33),
                     unpack_s16(words[7], 14) * (2 ** -29),
                     unpack_u32s(words[8], words[7]) * (2 ** -19),
                     unpack_u16(words[9], 14) * 16))

          elif 3 == subframe:
              # not well validated decode, possibly wrong...
              # [1] Figure 20-1 Sheet 3, Table 20-II, Table 20-III
              # Cic = Amplitude of the Cosine Harmonic Correction
              #       Term to the Angle of Inclination
              # Omega0 = Longitude of Ascending Node of Orbit
              #          Plane at Weekly Epoch
              # Cis = Amplitude of the Sine Harmonic Correction
              #       Term to the Orbit Radius
              # i0 = Inclination Angle at Reference Time
              # Crc = Amplitude of the Cosine Harmonic Correction
              #       Term to the Orbit Radius
              # omega = Argument of Perigee
              # Omegadot = Rate of Right Ascension
              # IODE = Issue of Data (Ephemeris)
              # IODT = Rate of Inclination Angle
              s += ("\n   Cic %e Omega0 %e Cis %e i0 %e"
                    "\n   Crc %e omega %e Omegadot %e"
                    "\n   IDOE %u IDOT %e" %
                    (unpack_s16(words[2], 14) * (2 ** -29),
                     unpack_s32s(words[3], words[2]) * (2 ** -31),
                     unpack_s16(words[4], 14) * (2 ** -29),
                     unpack_s32s(words[5], words[4]) * (2 ** -31),
                     # Crc
                     unpack_s16(words[6], 14) * (2 ** -5),
                     unpack_s32s(words[7], words[6]) * (2 ** -31),
                     # Omegadot
                     unpack_s24(words[8], 6) * (2 ** -43),
                     unpack_u8(words[9], 22),
                     unpack_s14(words[9], 8) * (2 ** -43)))

          elif 4 == subframe:
              # pages:
              #  2 to 5, 7 to 10 almanac data for SV 25 through 32
              #  13 navigation message correction table (NMCT_
              #  17 Special Messages
              #  18 Ionospheric and UTC data
              #  25 A-S flags/ SV health
              #  1, 6, 11, 16 and 21 reserved
              #  12, 19, 20, 22, 23 and 24 reserved
              #  14 and 15 reserved
              # as of 2018, data ID is always 1.
              svid = (words[2] >> 22) & 0x3f
              # 0 === svid is dummy SV
              # almanac for dummy sat 0, same as transmitting sat
              # Sec 3.2.1: "Users shall only use non-dummy satellites"
              page = index_s(svid, self.sbfr4_svid_page)

              s += ("\n   dataid %u svid %u (page %s)\n" %
                    (words[2] >> 28, svid, page))

              if 6 == page:
                  s += "    reserved"
              elif 2 <= page <= 10:
                  s += self.almanac(words)
              elif 13 == page:
                  # 20.3.3.5.1.9 NMCT.
                  # 30 ERDs, but more sats. A sat skips own ERD.
                  # no ERD for sat 32
                  # erds are signed! 0x20 == NA
                  s += ("    NMCT AI %u(%s)"
                        "\n      ERD1:  %s %s %s %s %s %s %s %s"
                        "\n      ERD9:  %s %s %s %s %s %s %s %s"
                        "\n      ERD17: %s %s %s %s %s %s %s %s"
                        "\n      ERD25: %s %s %s %s %s %s" %
                        ((words[2] >> 22) & 0x3,    # AI
                         index_s((words[2] >> 22) & 0x3, self.nmct_ai),
                         erd_s((words[2] >> 16) & 0x3f),   # erd1
                         erd_s((words[2] >> 8) & 0x3f),
                         erd_s((((words[2] >> 2) & 0x30) |
                                (words[3] >> 26) & 0x0f)),
                         erd_s((words[3] >> 20) & 0x3f),
                         erd_s((words[3] >> 14) & 0x3f),   # erd5
                         erd_s((words[3] >> 8) & 0x3f),
                         erd_s((((words[3] >> 2) & 0x30) |
                                (words[4] >> 26) & 0x0f)),
                         erd_s((words[4] >> 20) & 0x3f),
                         erd_s((words[4] >> 14) & 0x3f),   # erd9
                         erd_s((words[4] >> 8) & 0x3f),
                         erd_s((((words[4] >> 2) & 0x30) |
                                (words[5] >> 26) & 0x0f)),
                         erd_s((words[5] >> 20) & 0x3f),
                         erd_s((words[5] >> 14) & 0x3f),   # erd 13
                         erd_s((words[5] >> 8) & 0x3f),
                         erd_s((((words[5] >> 2) & 0x30) |
                                (words[6] >> 26) & 0x0f)),
                         erd_s((words[6] >> 20) & 0x3f),
                         erd_s((words[6] >> 14) & 0x3f),   # erd17
                         erd_s((words[6] >> 8) & 0x3f),
                         erd_s((((words[6] >> 2) & 0x30) |
                                (words[7] >> 26) & 0x0f)),
                         erd_s((words[7] >> 20) & 0x3f),
                         erd_s((words[7] >> 14) & 0x3f),   # erd21
                         erd_s((words[7] >> 8) & 0x3f),
                         erd_s((((words[7] >> 2) & 0x30) |
                                (words[8] >> 26) & 0x0f)),
                         erd_s((words[8] >> 20) & 0x3f),
                         erd_s((words[8] >> 14) & 0x3f),   # erd25
                         erd_s((words[8] >> 8) & 0x3f),
                         erd_s((((words[8] >> 2) & 0x30) |
                                (words[9] >> 26) & 0x0f)),
                         erd_s((words[9] >> 20) & 0x3f),
                         erd_s((words[9] >> 14) & 0x3f),   # erd29
                         erd_s((words[9] >> 8) & 0x3f),    # erd30
                         ))
              elif 17 == page:
                  s += ("    Special messages: " +
                        chr((words[2] >> 14) & 0xff) +
                        chr((words[2] >> 6) & 0xff) +
                        chr((words[3] >> 22) & 0xff) +
                        chr((words[3] >> 14) & 0xff) +
                        chr((words[3] >> 6) & 0xff) +
                        chr((words[4] >> 22) & 0xff) +
                        chr((words[4] >> 14) & 0xff) +
                        chr((words[4] >> 6) & 0xff) +
                        chr((words[5] >> 22) & 0xff) +
                        chr((words[5] >> 14) & 0xff) +
                        chr((words[5] >> 6) & 0xff) +
                        chr((words[6] >> 22) & 0xff) +
                        chr((words[6] >> 14) & 0xff) +
                        chr((words[6] >> 6) & 0xff) +
                        chr((words[7] >> 22) & 0xff) +
                        chr((words[7] >> 14) & 0xff) +
                        chr((words[7] >> 6) & 0xff) +
                        chr((words[8] >> 22) & 0xff) +
                        chr((words[8] >> 14) & 0xff) +
                        chr((words[8] >> 6) & 0xff) +
                        chr((words[9] >> 22) & 0xff) +
                        chr((words[9] >> 14) & 0xff))

              elif 18 == page:
                  alpha1 = (words[2] >> 14) & 0xff
                  alpha0 = (words[2] >> 6) & 0xff
                  alpha2 = (words[3] >> 22) & 0xff
                  alpha3 = (words[3] >> 14) & 0xff
                  beta0 = (words[3] >> 6) & 0xff
                  beta1 = (words[4] >> 6) & 0xff
                  beta2 = (words[4] >> 22) & 0xff
                  beta3 = (words[4] >> 14) & 0xff
                  A1 = (words[5] >> 6) & 0xffffff
                  A0 = (((words[6] << 2) & 0xffffff00) |
                        ((words[7] >> 22) & 0xff))
                  tot = (words[7] >> 14) & 0xff
                  WNt = (words[7] >> 6) & 0xff
                  deltatls = (words[8] >> 22) & 0xff
                  WNlsf = (words[8] >> 14) & 0xff
                  DN = (words[8] >> 6) & 0xff
                  deltatlsf = (words[9] >> 22) & 0xff
                  s += ("    Ionospheric and UTC data\n"
                        "     alpah0 x%02x alpah1 x%02x "
                        "alpah2 x%02x alpah3 x%02x\n"
                        "     beta0  x%02x beta1  x%02x "
                        "beta2  x%02x beta3  x%02x\n"
                        "     A0  x%08x A1  x%06x tot x%02x WNt x%02x\n"
                        "     deltatls x%02x WNlsf x%02x DN x%02x "
                        "deltatlsf x%02x" %
                        (alpha0, alpha1, alpha2, alpha3,
                         beta0, beta1, beta2, beta3,
                         A0, A1, tot, WNt,
                         deltatls, WNlsf, DN, deltatlsf))
              elif 25 == page:
                  aspoof = []
                  aspoof.append((words[2] >> 18) & 0x0f)
                  aspoof.append((words[2] >> 14) & 0x0f)
                  aspoof.append((words[2] >> 10) & 0x0f)
                  aspoof.append((words[2] >> 6) & 0x0f)
                  for i in range(3, 7):
                      aspoof.append((words[i] >> 26) & 0x0f)
                      aspoof.append((words[i] >> 22) & 0x0f)
                      aspoof.append((words[i] >> 18) & 0x0f)
                      aspoof.append((words[i] >> 14) & 0x0f)
                      aspoof.append((words[i] >> 10) & 0x0f)
                      aspoof.append((words[i] >> 6) & 0x0f)
                  aspoof.append((words[7] >> 26) & 0x0f)
                  aspoof.append((words[7] >> 22) & 0x0f)
                  aspoof.append((words[7] >> 18) & 0x0f)
                  aspoof.append((words[7] >> 14) & 0x0f)

                  sv = []
                  sv.append((words[7] >> 6) & 0x3f)
                  sv.append((words[8] >> 24) & 0x3f)
                  sv.append((words[8] >> 18) & 0x3f)
                  sv.append((words[8] >> 12) & 0x3f)
                  sv.append((words[8] >> 6) & 0x3f)
                  sv.append((words[9] >> 24) & 0x3f)
                  sv.append((words[9] >> 18) & 0x3f)
                  sv.append((words[9] >> 12) & 0x3f)
                  s += ("    A/S flags:\n"
                        "     as01 x%x as02 x%x as03 x%x as04 x%x "
                        "as05 x%x as06 x%x as07 x%x as08 x%x\n"
                        "     as09 x%x as10 x%x as11 x%x as12 x%x "
                        "as13 x%x as14 x%x as15 x%x as16 x%x\n"
                        "     as17 x%x as18 x%x as19 x%x as20 x%x "
                        "as21 x%x as22 x%x as23 x%x as24 x%x\n"
                        "     as25 x%x as26 x%x as27 x%x as28 x%x "
                        "as29 x%x as30 x%x as31 x%x as32 x%x\n" %
                        tuple(aspoof))
                  if VERB_DECODE <= opts['verbosity']:
                      for i in range(1, 33):
                          f = aspoof[i - 1]
                          s += ("      as%02d x%x (A-S %s, Conf %s)\n" %
                                (i, f,
                                 'On' if (f & 8) else 'Off',
                                 index_s(f & 7, self.sv_conf)))

                  s += ("    SV HEALTH:\n"
                        "      sv25 x%2x sv26 x%2x sv27 x%2x sv28 x%2x "
                        "sv29 x%2x sv30 x%2x sv31 x%2x sv32 x%2x" %
                        tuple(sv))
              else:
                  s += "    Reserved"

          elif 5 == subframe:
              svid = (words[2] >> 22) & 0x3f
              # 0 === svid is dummy SV
              # almanac for dummy sat 0, same as transmitting sat
              # Sec 3.2.1: "Users shall only use non-dummy satellites"
              page = index_s(svid, self.sbfr5_svid_page)

              s += ("\n   dataid %u svid %u (page %s)\n" %
                    (words[2] >> 28, svid, page))

              if 1 <= page <= 24:
                  s += self.almanac(words)
              elif 25 == page:
                  toa = (words[2] >> 14) & 0xff
                  WNa = (words[2] >> 6) & 0xff
                  sv = []
                  for i in range(3, 9):
                      sv.append((words[i] >> 24) & 0x3f)
                      sv.append((words[i] >> 18) & 0x3f)
                      sv.append((words[i] >> 12) & 0x3f)
                      sv.append((words[i] >> 6) & 0x3f)
                  s += "    SV HEALTH toa %u WNa %u\n" % (toa, WNa)
                  s += ("     sv01 x%2x sv02 x%2x sv03 x%2x sv04 x%2x "
                        "sv05 x%2x sv06 x%2x sv07 x%2x sv08 x%2x\n"
                        "     sv09 x%2x sv10 x%2x sv11 x%2x sv12 x%2x "
                        "sv13 x%2x sv14 x%2x sv15 x%2x sv16 x%2x\n"
                        "     sv17 x%2x sv18 x%2x sv19 x%2x sv20 x%2x "
                        "sv21 x%2x sv22 x%2x sv23 x%2x sv24 x%2x" %
                        tuple(sv))
              else:
                  s += "    Reserved"