import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config
from rfgnocchi.xilinx import complex_multiplier, dds_compiler
from rfgnocchi.blocks import controller_inner

logger = logging.getLogger(__name__)

class ControllerBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.builders = [
            complex_multiplier.ComplexMultiplierBuilder({
                'module_name': 'complex_multiply',
            }),
            controller_inner.ControllerInnerBuilder({}),
            dds_compiler.DDSCompilerBuilder({
                'module_name': 'sincoslut',
                'phase_width': 16,
                'output_width': 16,
                'partspresent': 'sin_cos_lut_only',
            })
        ]
        self.simple_filenames = [
            os.path.join(config.basedir, 'blocks', 'controller.vhd'),
        ]
        
def get_controller_interface(params):
    module_name = 'controller'
    builder = ControllerBuilder()
    wires_in = (
        ('reset', signal.std_logic_type),
        ('clear', signal.std_logic_type),
        ('i_error_tdata', signal.StdLogicVector(width=16)),
        ('i_error_tvalid', signal.std_logic_type),
        ('i_data_tdata', signal.StdLogicVector(width=32)),
        ('i_data_tvalid', signal.std_logic_type),
        ('i_data_tlast', signal.std_logic_type),
        ('o_data_tready', signal.std_logic_type),
        ('i_config_tdata', signal.StdLogicVector(width=32)),
        ('i_config_tvalid', signal.std_logic_type),
    )
    wires_out = (
        ('o_data_tdata', signal.StdLogicVector(width=32)),
        ('o_data_tvalid', signal.std_logic_type),
        ('o_data_tlast', signal.std_logic_type),
        ('i_data_tready', signal.std_logic_type),
        ('i_config_tready', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk'],
    )
    return iface


assert('controller' not in interface.module_register)
interface.module_register['controller'] = get_controller_interface
