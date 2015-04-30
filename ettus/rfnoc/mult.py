import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config, ettus

logger = logging.getLogger(__name__)


def get_mult_interface(params):
    module_name = 'Mult'
    width_A = params['width_A']
    width_B = params['width_B']
    width_P = params['width_P']
    drop_top_P = params['drop_top_P']
    latency = params['latency']
    cascade_out = params['cascade_out']
    builder = ettus.get_builder('mult')
    packages = []
    module_parameters = {
        'WIDTH_A': width_A,
        'WIDTH_B': width_B,
        'WIDTH_P': width_P,
        'DROP_TOP_P': drop_top_P,
        'LATENCY': latency,
        'CASCADE_OUT': cascade_out,
    }
    wires_in = (
        ('reset', signal.std_logic_type),
        ('a_tdata', signal.StdLogicVector(width=width_A)),
        ('a_tlast', signal.std_logic_type),
        ('a_tvalid', signal.std_logic_type),
        ('b_tdata', signal.StdLogicVector(width=width_B)),
        ('b_tlast', signal.std_logic_type),
        ('b_tvalid', signal.std_logic_type),
        ('p_tready', signal.std_logic_type),
    )
    wires_out = (
        ('a_tready', signal.std_logic_type),
        ('b_tready', signal.std_logic_type),
        ('p_tdata', signal.StdLogicVector(width=width_P)),
        ('p_tlast', signal.std_logic_type),
        ('p_tvalid', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, module_parameters=module_parameters,
        packages=packages, builder=builder, clock_names=['clk'])
    return iface


assert('Mult' not in interface.module_register)
interface.module_register['Mult'] = get_mult_interface
