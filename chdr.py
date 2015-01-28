import math
import logging

logger = logging.getLogger(__name__)

def make_control_header(size, seqnum=0, is_extension_context=False,
                        end_of_burst=False, time=None, sid=0):
    if time is not None:
        raise Exception('Cannot deal with time yet.')
    is_extension_context_offset = pow(2, 63)
    has_time_offset = pow(2, 61)
    end_of_burst_offset = pow(2, 60)
    seqnum_offset = pow(2, 48)
    size_offset = pow(2, 32)
    sid_offset = 1
    header = sid * sid_offset
    header += size * size_offset
    header += seqnum * seqnum_offset
    if end_of_burst:
        header += end_of_burst_offset
    if time is not None:
        header += has_time_offset
    if is_extension_context:
        header += is_extension_context_offset
    return header
    
def make_setting_bus_command(address, setting):
    address_offset = pow(2, 32)
    command = address * address_offset + setting
    return command

def make_settings_packet(commands, time=None, sid=0):
    '''
    Make a CHDR extension context packet.
    This does a bunch of settings bus commands.
    '''
    packet = []
    header = make_control_header(
        len(commands), is_extension_context=True, time=time, sid=sid)
    packet.append(header)
    for address, command in commands:
        packet.append(make_setting_bus_command(address, command))
    return packet
        
def make_data_packet(data, time=None, sid=0, seqnum=0):
    '''
    Make a CHDR IF packet.
    A stream of 32 bit data is compressed into a stream of 64 bit data.
    '''
    packet = []
    # Make copy so we don't change original
    data = [d for d in data]
    if len(data) % 2 == 1:
        data.append(0)
    header = make_control_header(
        size=len(data)//2, seqnum=seqnum, time=time, sid=sid)
    packet.append(header)
    pp = pow(2, 32)
    paired_data = [(data[2*i], data[2*i+1]) for i in range(len(data)//2)]
    combined_data = [d0*pp+d1 for d0, d1 in paired_data]
    packet += combined_data
    return packet

def packets_to_noc_inputs(packets):
    '''
    Turns packets to inputs for Noc Block.
    Interspaces data with 2 empty clock cycles.
    '''
    inputs = []
    empty_d = {
        'i_tdata': 0,
        'i_tlast': 0,
        'i_tvalid': 0,
        'o_tready': 1,
        'ce_rst': 0,
        'bus_rst': 0,
    }
    for packet in packets:
        for line in packet:
            d = {
                'i_tdata': line,
                'i_tlast': 0,
                'i_tvalid': 1,
                'o_tready': 1,
                'ce_rst': 0,
                'bus_rst': 0,
            }
            inputs.append(d)
            inputs.append(empty_d)
            inputs.append(empty_d)
    return inputs

def noc_outputs_to_packets(outputs):
    '''
    Only deals with IF packets at the moment.
    '''
    pass
        
