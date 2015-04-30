'''
Python tools for making NoC blocks.
'''

import asyncio

from pyvivado import signal

noc_clocks = ['bus_clk', 'ce_clk']

# Define input wires for a NoC block
noc_input_wires = (
    ('bus_rst', signal.std_logic_type),
    ('ce_rst', signal.std_logic_type),
    ('i_tdata', signal.StdLogicVector(width=64)),
    ('i_tlast', signal.std_logic_type),
    ('i_tvalid', signal.std_logic_type),
    ('o_tready', signal.std_logic_type),
)

# Define output wires for a NoC block
noc_output_wires = (
    ('o_tdata', signal.StdLogicVector(width=64)),
    ('o_tlast', signal.std_logic_type),
    ('o_tvalid', signal.std_logic_type),
    ('i_tready', signal.std_logic_type),
    ('debug', signal.StdLogicVector(width=64)),
)

def make_inputs(bus_rst=0, ce_rst=0,
                i_tdata=0, i_tlast=0, i_tvalid=0, o_tready=0):
    return {
        'bus_rst': bus_rst,
        'ce_rst': ce_rst,
        'i_tdata': i_tdata,
        'i_tlast': i_tlast,
        'i_tvalid': i_tvalid,
        'o_tready': o_tready,
    }

def make_outputs(o_tdata=0, o_tlast=0, o_tvalid=0, i_tready=0):
    return {
        'o_tdata': o_tdata,
        'o_tlast': o_tlast,
        'o_tvalid': o_tvalid,
        'i_tready': i_tready,
    }
