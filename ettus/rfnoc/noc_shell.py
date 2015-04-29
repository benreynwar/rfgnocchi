import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi import ettus
from rfgnocchi import config

logger = logging.getLogger(__name__)

noc_shell_builder = ettus.get_builder('noc_shell')

def get_noc_shell_interface(params):
    module_name = 'noc_shell'
    builder = noc_shell_builder
    input_ports = params['input_ports']
    output_ports = params['output_ports']
    wires_in = (
        # RFNoC interfaces
        ('bus_rst', signal.std_logic_type),
        ('i_tdata', signal.StdLogicVector(width=64)),
        ('i_tlast', signal.std_logic_type),
        ('i_tvalid', signal.std_logic_type),
        ('o_tready', signal.std_logic_type),
        # Computation Engine interfaces
        ('reset', signal.std_logic_type),
        # Control Sink
        ('rb_data', signal.StdLogicVector(width=64)),
        # Control Source
        ('cmdout_tdata', signal.StdLogicVector(width=64)),
        ('cmdout_tlast', signal.std_logic_type),
        ('cmdout_tvalid', signal.std_logic_type),
        ('ackin_tready', signal.std_logic_type),
        # Stream Sink
        ('str_sink_tready', signal.StdLogicVector(width=input_ports)),
        # Stream Source
        ('str_src_tdata', signal.StdLogicVector(width=output_ports*64)),
        ('str_src_tlast', signal.StdLogicVector(width=output_ports)),
        ('str_src_tvalid', signal.StdLogicVector(width=output_ports)),
    )
    wires_out = (
        # RFNoC interfaces
        ('i_tready', signal.std_logic_type),
        ('o_tdata', signal.StdLogicVector(width=64)),
        ('o_tlast', signal.std_logic_type),
        ('o_tvalid', signal.std_logic_type),
        # Computation Engine interfaces
        # Control Sink
        ('set_data', signal.StdLogicVector(width=32)),
        ('set_addr', signal.StdLogicVector(width=8)),
        ('set_stb', signal.std_logic_type),
        # Control Source
        ('cmdout_tready', signal.std_logic_type),
        ('ackin_tdata', signal.StdLogicVector(width=64)),
        ('ackin_tlast', signal.std_logic_type),
        ('ackin_tvalid', signal.std_logic_type),
        # Stream Sink
        ('str_sink_tdata', signal.StdLogicVector(width=input_ports*64)),
        ('str_sink_tlast', signal.StdLogicVector(width=input_ports)),
        ('str_sink_tvalid', signal.StdLogicVector(width=input_ports)),
        # Stream Source
        ('str_src_tready', signal.StdLogicVector(width=output_ports)),
        # Clear TX Sequence Number
        ('clear_tx_seqnum', signal.std_logic_type),
        # Debug
        ('debug', signal.StdLogicVector(width=64)),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk', 'bus_clk'],
        constants=builder.constants,
    )
    return iface

def make_inputs(bus_rst=0,
                i_tdata=0,
                i_tlast=0,
                i_tvalid=0,
                o_tready=0,
                reset=0,
                rb_data=0,
                cmdout_tdata=0,
                cmdout_tlast=0,
                cmdout_tvalid=0,
                ackin_tready=0,
                str_sink_tready=0,
                str_src_tdata=0,
                str_src_tlast=0,
                str_src_tvalid=0,
            ):
    return {
        # RFNoC interfaces
        'bus_rst': bus_rst,
        'i_tdata': i_tdata,
        'i_tlast': i_tlast,
        'i_tvalid': i_tvalid,
        'o_tready': o_tready,
        # Computation Engine interfaces
        'reset': reset,
        # Control Sink
        'rb_data': rb_data,
        # Control Source
        'cmdout_tdata': cmdout_tdata,
        'cmdout_tlast': cmdout_tlast,
        'cmdout_tvalid': cmdout_tvalid,
        'ackin_tready': ackin_tready,
        # Stream Sink
        'str_sink_tready': str_sink_tready,
        # Stream Source
        'str_src_tdata': str_src_tdata,
        'str_src_tlast': str_src_tlast,
        'str_src_tvalid': str_src_tvalid,
    }    

def make_inputs_from_noc_inputs(noc_inputs, str_sink_tready=0):
    return make_inputs(
        i_tdata=noc_inputs['i_tdata'],
        i_tlast=noc_inputs['i_tlast'],
        i_tvalid=noc_inputs['i_tvalid'],
        o_tready=noc_inputs['o_tready'],
        reset=noc_inputs['ce_rst'],
        bus_rst=noc_inputs['bus_rst'],
        str_sink_tready=str_sink_tready,
    )
    

name = 'noc_shell'
interface.add_to_module_register(name, get_noc_shell_interface)

