import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config
from rfgnocchi.ettus.rfnoc import axi_round_and_clip_complex
from rfgnocchi.ettus.rfnoc import mult

logger = logging.getLogger(__name__)

class ControlLoopBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.builders = [
            mult.MultBuilder({}),
        ]
        self.simple_filenames = [
            os.path.join(config.basedir, 'blocks', 'control_loop.vhd'),
        ]
        
def get_control_loop_interface(params):
    module_name = 'control_loop'
    builder = ControlLoopBuilder()
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


assert('control_loop' not in interface.module_register)
interface.module_register['control_loop'] = get_control_loop_interface
