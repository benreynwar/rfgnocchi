import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config
from rfgnocchi.ettus.rfnoc import axi_round_and_clip_complex
from rfgnocchi.xilinx import dds_compiler, complex_multiplier

logger = logging.getLogger(__name__)

class RotatorCCBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.builders = [
            complex_multiplier.ComplexMultiplierBuilder({
                'module_name': 'complex_multiply',
            }),
            dds_compiler.DDSCompilerBuilder({
                'module_name': 'nco',
                'phase_width': 16,
                'output_width': 16,
            }),
            axi_round_and_clip_complex.AxiRoundAndClipComplexBuilder({}),
        ]
        self.simple_filenames = [
            os.path.join(config.basedir, 'blocks', 'rotator_cc.vhd'),
        ]
        
def get_rotator_cc_interface(params):
    module_name = 'rotator_cc'
    builder = RotatorCCBuilder()
    complex_width = 32
    se_phase_width = 16
    wires_in = (
        ('reset', signal.std_logic_type),
        ('i_data_tdata', signal.StdLogicVector(width=complex_width)),
        ('i_data_tlast', signal.std_logic_type),
        ('i_data_tvalid', signal.std_logic_type),
        ('i_config_tdata', signal.StdLogicVector(width=2*se_phase_width)),
        ('i_config_tvalid', signal.std_logic_type),
        ('o_tready', signal.std_logic_type),
    )
    wires_out = (
        ('o_tdata', signal.StdLogicVector(width=complex_width)),
        ('o_tlast', signal.std_logic_type),
        ('o_tvalid', signal.std_logic_type),
        ('i_data_tready', signal.std_logic_type),
        ('i_config_tready', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk'],
    )
    return iface


assert('rotator_cc' not in interface.module_register)
interface.module_register['rotator_cc'] = get_rotator_cc_interface
