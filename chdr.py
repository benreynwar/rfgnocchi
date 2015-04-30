import math
import logging

from rfgnocchi import noc

logger = logging.getLogger(__name__)

class BadPacket(object):
    
    def data(self):
        return None


class CHDRPacket(object):

    is_extension_context_offset = pow(2, 63)
    has_time_offset = pow(2, 61)
    end_of_burst_offset = pow(2, 60)
    seqnum_offset = pow(2, 48)
    size_offset = pow(2, 32)
    sid_offset = 1

    def __init__(self, seqnum=0, is_extension_context=False,
                 end_of_burst=False, time=None, sid=0, payload=[]):
        self.size = (len(payload)+1)*8
        self.seqnum = seqnum
        self.is_extension_context = is_extension_context
        self.end_of_burst = end_of_burst
        self.time = time
        self.sid = sid
        self.payload = payload
        
    def make_control_header(self):
        if self.time is not None:
            raise Exception('Cannot deal with time yet.')
        header = self.sid * self.sid_offset
        header += self.size * self.size_offset
        header += self.seqnum * self.seqnum_offset
        if self.end_of_burst:
            header += self.end_of_burst_offset
        if self.time is not None:
            header += self.has_time_offset
        if self.is_extension_context:
            header += self.is_extension_context_offset
        return header

    @classmethod
    def parse_control_header(cls, header):
        remainder = header
        is_extension_context = remainder // cls.is_extension_context_offset
        remainder -= is_extension_context * cls.is_extension_context_offset
        has_time = remainder // cls.has_time_offset
        remainder -= has_time * cls.has_time_offset
        end_of_burst = remainder // cls.end_of_burst_offset
        remainder -= end_of_burst * cls.end_of_burst_offset
        seqnum = remainder // cls.seqnum_offset
        remainder -= seqnum * cls.seqnum_offset
        size = remainder // cls.size_offset
        remainder -= size * cls.size_offset
        sid = remainder // cls.sid_offset
        remainder -= sid * cls.sid_offset
        assert(has_time == 0)
        to_boolean = {0: False, 1: True}
        return {
            'is_extension_context': to_boolean[is_extension_context],
            'time': None,
            'end_of_burst': to_boolean[end_of_burst],
            'seqnum': seqnum,
            'size': size,
            'sid': sid,
        }

    @classmethod
    def create_from_lump(cls, lump):
        if lump[0] is None:
            packet = BadPacket()
        else:
            header = cls.parse_control_header(lump[0])
            payload = lump[1:]
            if (header['size'] != (len(payload)+1)*8):
                raise ValueError('Size of payload does not match the header.')
            del header['size']
            packet = cls(payload=payload, **header)
        return packet

    @classmethod
    def create_settings_packet(cls, address, value, sid=0, time=None):
        '''
        Make a CHDR extension context packet.
        This does a single settings bus command.
        '''
        address_offset = pow(2, 32)
        command = address * address_offset + value
        packet = cls(is_extension_context=True,
                     sid=sid,
                     time=time,
                     payload=[command],
                 )
        return packet
    
    @classmethod
    def create_data_packet(cls, data, time=None, sid=0, seqnum=0):
        '''
        Make a CHDR IF packet.
        A stream of 32 bit data is compressed into a stream of 64 bit data.
        '''
        packet = []
        # Make copy so we don't change original
        data = [d for d in data]
        if len(data) % 2 == 1:
            data.append(0)
        pp = pow(2, 32)
        for d in data:
            if d > pp-1:
                raise ValueError('Integer does not fit in 32 bits.')
        paired_data = [(data[2*i], data[2*i+1]) for i in range(len(data)//2)]
        payload = [d0*pp+d1 for d0, d1 in paired_data]
        packet = cls(payload=payload, time=time, sid=sid, seqnum=seqnum)
        return packet

    def data(self):
        pp = pow(2, 32)
        ds = []
        for p in self.payload:
            ds.append(p // pp)
            ds.append(p % pp)
        return ds


def packets_to_noc_inputs(packets):
    '''
    Turns packets to inputs for Noc Block.
    Interspaces data with 2 empty clock cycles.
    '''
    inputs = []
    for packet in packets:
        inputs.append(
            noc.make_inputs(i_tdata=packet.make_control_header(),
                            i_tvalid=1, o_tready=1,
                        ))
        for p_index, p in enumerate(packet.payload):
            if p_index+1 == len(packet.payload):
                i_tlast = 1
            else:
                i_tlast = 0
                    
            inputs.append(
                noc.make_inputs(i_tdata=p,
                                i_tvalid=1, o_tready=1,
                                i_tlast=i_tlast))
        inputs.append(noc.make_inputs(o_tready=1))
        inputs.append(noc.make_inputs(o_tready=1))
    return inputs


def noc_outputs_to_packets(outputs):
    current_lump = []
    lumps = []
    for d in outputs:
        if d['o_tvalid']:
            current_lump.append(d['o_tdata'])
            if d['o_tlast']:
                lumps.append(current_lump)
                current_lump = []
    packets = [CHDRPacket.create_from_lump(lump=lump) for lump in lumps]
    return packets
