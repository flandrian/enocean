from __future__ import print_function, unicode_literals, division, absolute_import
import unittest

from enocean.protocol.eep import EEP
from enocean.protocol.esp2parser import Esp2Parser
from enocean.protocol.constants import RORG, PACKET
from enocean.protocol.packet import RadioPacket

eep = EEP()


class Test(unittest.TestCase):


    def test_temperature(self):
        data = [
            0xa5, 0x0, 0x8a, 0x76, 0xf, 0x1, 0x84, 0x34, 0x57, 0x0
        ]
        packet = RadioPacket(PACKET.RADIO, data, [])
        
        packet.parse_eep(0x10, 0x03)
        
        assert packet.parsed['TMP']['value'] == 21.49019607843137


if __name__ == "__main__":
    #import sys;sys.argv = [, Test.test_temperature]
    unittest.main()