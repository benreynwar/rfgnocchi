import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config
from rfgnocchi.blocks import rotator_cc
from rfgnocchi.xilinx import fir_compiler

logger = logging.getLogger(__name__)

class FreqXlatingFirFilterCCFBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.builders = [
            rotator_cc.RotatorCCBuilder({}),
            fir_compiler.FirCompilerBuilder({
                'module_name': 'simple_fir',
                'n_taps': params['n_taps'],
                'decimation_rate': params['decimation_rate'],
            }),
        ]
        self.simple_filenames = [
            os.path.join(config.basedir, 'filters', 'freq_xlating_fir_filter_ccf.vhd'),
        ]
        
def get_freq_xlating_fir_filter_ccf_interface(params):
    factory_name = 'freq_xlating_fir_filter_ccf'
    module_name = factory_name
    builder = FreqXlatingFirFilterCCFBuilder(params)
    wires_in = (
        ('reset', signal.std_logic_type),
        ('i_data_tdata', signal.StdLogicVector(width=32)),
        ('i_data_tlast', signal.std_logic_type),
        ('i_data_tvalid', signal.std_logic_type),
        ('i_fir_reload_tdata', signal.StdLogicVector(width=32)), 
        ('i_fir_reload_tlast', signal.std_logic_type),
        ('i_fir_reload_tvalid', signal.std_logic_type),
        ('i_fir_config_tdata', signal.StdLogicVector(width=8)), 
        ('i_fir_config_tvalid', signal.std_logic_type),
        ('i_rotator_config_tdata', signal.StdLogicVector(width=32)),
        ('i_rotator_config_tvalid', signal.std_logic_type),
        ('o_tready', signal.std_logic_type),
    )
    wires_out = (
        ('o_tdata', signal.StdLogicVector(width=32)),
        ('o_tlast', signal.std_logic_type),
        ('o_tvalid', signal.std_logic_type),
        ('i_data_tready', signal.std_logic_type),
        ('i_reload_config_tready', signal.std_logic_type),
        ('i_fir_config_tready', signal.std_logic_type),
        ('i_rotator_config_tready', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk'],
        factory_name=factory_name,
    )
    return iface


assert('freq_xlating_fir_filter_ccf' not in interface.module_register)
interface.module_register['freq_xlating_fir_filter_ccf'] = (
    get_freq_xlating_fir_filter_ccf_interface)
