import os
import logging
import math
from collections import OrderedDict

from pyvivado import builder, interface, signal

from rfgnocchi import config

logger = logging.getLogger(__name__)

class CordicBuilder(builder.Builder):

    def __init__(self, params):
        super().__init__(params)
        module_name = params['module_name']
        ip_params = [
            ('functional_selection', 'square_root'),
            ('data_format', 'unsignedinteger'),
            ('input_width', 16),
            ('aresetn', 'true'),
        ]
        self.ip_params = OrderedDict(ip_params)
        self.ips = [
            ('cordic', self.ip_params, module_name),
        ]
        

def get_cordic_interface(params):
    factory_name = 'xilinx_cordic'
    module_name = params['module_name']
    builder = CordicBuilder(params)
    wires_in = (
        ('aresetn', signal.std_logic_type),
        ('s_axis_cartesian_tdata', signal.StdLogicVector(width=16)),
        ('s_axis_cartesian_tvalid', signal.std_logic_type),
    )
    wires_out = (
        ('m_axis_dout_tvalid', signal.std_logic_type),
        # Only 9 of those bits are relevant but sign-extended up to 16.
        ('m_axis_dout_tdata', signal.StdLogicVector(width=16)),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['aclk'],
        needs_dummy=True, factory_name=factory_name,
    )
    return iface


assert('xilinx_cordic' not in interface.module_register)
interface.module_register['xilinx_cordic'] = get_cordic_interface
