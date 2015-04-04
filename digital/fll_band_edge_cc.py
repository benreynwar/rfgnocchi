import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config
from rfgnocchi.maths import complex_mag
from rfgnocchi.blocks import controller
from rfgnocchi.xilinx import fir_compiler

logger = logging.getLogger(__name__)

class FLLBandEdgeCCBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.builders = [
            complex_mag.ComplexMagBuilder({
                'width': 16,
            }),
            controller.ControllerBuilder({}),
            fir_compiler.FirCompiler({
                'module_name': 'fir_ccc',
                'n_taps': 21,
            })
        ]
        self.simple_filenames = [
            os.path.join(config.basedir, 'digital', 'fll_band_edge_cc.vhd'),
        ]
        
def get_fll_band_edge_cc_interface(params):
    module_name = 'fll_band_edge_cc'
    builder = FLLBandEdgeCCBuilder(params)
    data_width = 32
    tap_width = 32
    filter_config_width = 8
    controller_config_width = 32
    wires_in = (
        ('reset', signal.std_logic_type),
        ('clear', signal.std_logic_type),
        ('i_data_tdata', signal.StdLogicVector(width=data_width)),
        ('i_data_tvalid', signal.std_logic_type),
        ('i_data_tlast', signal.std_logic_type),
        ('i_reload_upper_filter_tdata', signal.StdLogicVector(width=tap_width)),
        ('i_reload_upper_filter_tvalid', signal.std_logic_type),
        ('i_reload_upper_filter_tlast', signal.std_logic_type),
        ('i_reload_lower_filter_tdata', signal.StdLogicVector(width=tap_width)),
        ('i_reload_lower_filter_tvalid', signal.std_logic_type),
        ('i_reload_lower_filter_tlast', signal.std_logic_type),
        ('i_config_filter_tdata', signal.StdLogicVector(
            width=filter_config_width)),
        ('i_config_filter_tvalid', signal.std_logic_type),
        ('i_config_controller_tdata', signal.StdLogicVector(
            width=controller_config_width)),
        ('i_config_controller_tvalid', signal.std_logic_type),
        ('o_tready', signal.std_logic_type),
    )
    wires_out = (
        ('i_data_tready', signal.std_logic_type),
        ('i_reload_upper_filter_tready', signal.std_logic_type),
        ('i_reload_lower_filter_tready', signal.std_logic_type),
        ('i_config_filter_tready', signal.std_logic_type),
        ('i_config_controller_tready', signal.std_logic_type),
        ('o_tdata', signal.StdLogicVector(width=data_width)),
        ('o_tvalid', signal.std_logic_type),
        ('o_tlast', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk'],
    )
    return iface


assert('fll_band_edge_cc' not in interface.module_register)
interface.module_register['fll_band_edge_cc'] = get_fll_band_edge_cc_interface
