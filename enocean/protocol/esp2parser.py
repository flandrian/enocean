# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
from enocean.protocol.constants import PACKET, PARSE_RESULT, RORG
from enocean.protocol.packet import Packet, RadioPacket

class Esp2Parser():

    logger = logging.getLogger('enocean.protocol.esp2parser')

    @staticmethod
    def parse_msg(buf, communicator=None):
        '''
        Parses message from buffer.
        returns:
            - PARSE_RESULT
            - remaining buffer
            - Packet -object (if message was valid, else None)
        '''
        # If the buffer doesn't contain 0xA5 (start char)
        # the message isn't needed -> ignore
        if 0xA5 not in buf:
            return PARSE_RESULT.INCOMPLETE, [], None

        # Valid buffer starts from 0xA5
        # Convert to list, as index -method isn't defined for bytearray
        buf = [ord(x) if not isinstance(x, int) else x for x in buf[list(buf).index(0xA5):]]
        try:
            data_len = buf[2] & 0x1F
        except IndexError:
            # If the fields don't exist, message is incomplete
            return PARSE_RESULT.INCOMPLETE, buf, None

        # Packet Length: 3 bytes header, data
        msg_len = 3 + data_len
        if len(buf) < msg_len:
            # If buffer isn't long enough, the message is incomplete
            return PARSE_RESULT.INCOMPLETE, buf, None

        msg = buf[0:msg_len]
        buf = buf[msg_len:]

        h_seq = (msg[2] >> 5) & 0x07
        data = msg[3:-2]
        opt_data = []

        checksum = 0
        for data_byte in msg[2:-1]:
            checksum = checksum + data_byte
        checksum = checksum & 0xFF
        if checksum != msg[-1]:
            # Return CRC_MISMATCH
            Esp2Parser.logger.error('CRC error')
            return PARSE_RESULT.CRC_MISMATCH, buf, None

        if (h_seq == 0x00) or (h_seq == 0x01) or (h_seq == 0x02):
            if (data[0] == 0x05):
                data[0] = RORG.RPS
            elif (data[0] == 0x06):
                data[0] = RORG.BS1
            elif (data[0] == 0x07):
                data[0] = RORG.BS4
            packet = RadioPacket(PACKET.RADIO, data, opt_data)
        else:
            packet = Packet(PACKET.RESERVED, data, opt_data)
        
        return PARSE_RESULT.OK, buf, packet
