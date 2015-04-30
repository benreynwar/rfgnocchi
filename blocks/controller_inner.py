import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config, ettus

logger = logging.getLogger(__name__)

class ControllerInnerBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.builders = [
            ettus.get_builder('mult'),
        ]
        self.simple_filenames = [
            os.path.join(config.basedir, 'blocks', 'controller_inner.vhd'),
        ]
        
def get_controller_inner_interface(params):
    module_name = 'controller_inner'
    builder = ControllerInnerBuilder()
    wires_in = (
        ('reset', signal.std_logic_type),
        ('clear', signal.std_logic_type),
        ('i_error_tdata', signal.StdLogicVector(width=16)),
        ('i_error_tvalid', signal.std_logic_type),
        ('i_config_tdata', signal.StdLogicVector(width=32)),
        ('i_config_tvalid', signal.std_logic_type),
        ('o_phase_tready', signal.std_logic_type),
    )
    wires_out = (
        ('o_phase_tdata', signal.StdLogicVector(width=16)),
        ('o_phase_tvalid', signal.std_logic_type),
        ('i_config_tready', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk'],
    )
    return iface


assert('controller_inner' not in interface.module_register)
interface.module_register['controller_inner'] = get_controller_inner_interface
