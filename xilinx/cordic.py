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
        input_width = params['input_width']
        ip_params = [
            ('functional_selection', 'square_root'),
            ('cartesian_has_tlast', 'true'),
            ('flow_control', 'blocking'),
            ('out_tready', 'true'),
            ('data_format', 'unsignedinteger'),
            ('input_width', input_width),
            ('aresetn', 'true'),
        ]
        self.ip_params = OrderedDict(ip_params)
        self.ips = [
            ('cordic', self.ip_params, module_name),
        ]
        

def get_cordic_interface(params):
    factory_name = 'xilinx_cordic'
    module_name = params['module_name']
    input_width = params['input_width']
    output_width = math.ceil((math.floor(input_width/2)+1)/8)*8
    builder = CordicBuilder(params)
    wires_in = (
        ('aresetn', signal.std_logic_type),
        ('s_axis_cartesian_tdata', signal.StdLogicVector(width=input_width)),
        ('s_axis_cartesian_tvalid', signal.std_logic_type),
        ('s_axis_cartesian_tlast', signal.std_logic_type),
        ('m_axis_dout_tready', signal.std_logic_type),
    )
    wires_out = (
        ('m_axis_dout_tvalid', signal.std_logic_type),
        ('m_axis_dout_tlast', signal.std_logic_type), 
        # Only 9 of those bits are relevant but sign-extended up to 16.
        ('m_axis_dout_tdata', signal.StdLogicVector(width=output_width)),
        ('s_axis_cartesian_tready', signal.std_logic_type),
    )
    constants = {
        'output_width': output_width,
    }
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['aclk'],
        needs_dummy=True, factory_name=factory_name,
        constants=constants, 
    )
    return iface


assert('xilinx_cordic' not in interface.module_register)
interface.module_register['xilinx_cordic'] = get_cordic_interface
