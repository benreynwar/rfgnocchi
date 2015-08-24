import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi.xilinx.fir_compiler import FirCompilerBuilder
from rfgnocchi.xilinx.fifo_generator import FifoGeneratorBuilder
from rfgnocchi import config, noc, ettus

logger = logging.getLogger(__name__)

class NocBlockFirFilterBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = 'noc_block_fir_filter'
        n_coefficients = 21
        # The simple_fir_builder specifies the Xilinx IP block.
        simple_fir_builder = FirCompilerBuilder({
            'module_name': 'axi_fir',
            'n_taps': n_coefficients,
        })
        # The constants are useful for tests that need to know these values.
        self.constants = {
            'n_coefficients': n_coefficients,
            'coefficient_width': int(
                simple_fir_builder.ip_params_dict['coefficient_width']),
            'data_width': int(
                simple_fir_builder.ip_params_dict['data_width']),
            'output_width': int(
                simple_fir_builder.constants['output_width']),
        }        
        # We also specify dependencies of a few Ettus modules.
        # Their dependencies will be retrieved by their builders.
        self.builders = [
            simple_fir_builder,
            ettus.get_builder('noc_shell'),
            ettus.get_builder('setting_reg'),
            ettus.get_builder('axi_wrapper'),
            ettus.get_builder('axi_round_and_clip_complex'),
        ]
        self.simple_filenames = [
            os.path.join(config.ettus_fpgadir, 'rfnoc', 'noc_block_fir_filter.v'),
        ]


def get_noc_block_fir_filter_interface(params):
    builder = NocBlockFirFilterBuilder(params)
    iface = interface.Interface(
        wires_in=noc.noc_input_wires,
        wires_out=noc.noc_output_wires,
        module_name='noc_block_fir_filter',
        parameters=params,
        builder=builder,
        clock_names=noc.noc_clocks,
        constants=builder.constants,
    )
    return iface


assert('noc_block_fir_filter' not in interface.module_register)
interface.module_register['noc_block_fir_filter'] = get_noc_block_fir_filter_interface

