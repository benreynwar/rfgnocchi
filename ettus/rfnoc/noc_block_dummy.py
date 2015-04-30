import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi import config, noc, ettus

logger = logging.getLogger(__name__)

class NocBlockDummyBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = 'noc_block_dummy'
        self.builders = [
            ettus.get_builder('noc_shell'),
            ettus.get_builder('setting_reg'),
            ettus.get_builder('axi_wrapper'),
            ettus.get_builder('axi_round_and_clip_complex'),
        ]
        self.simple_filenames = [
            os.path.join(config.basedir, 'ettus', 'rfnoc', 'noc_block_dummy.vhd'),
        ]


def get_noc_block_dummy_interface(params):
    builder = NocBlockDummyBuilder(params)
    iface = interface.Interface(
        wires_in=noc.noc_input_wires,
        wires_out=noc.noc_output_wires,
        module_name='noc_block_dummy',
        parameters=params,
        builder=builder,
        clock_names=noc.noc_clocks,
        constants=builder.constants,
    )
    return iface


assert('noc_block_dummy' not in interface.module_register)
interface.module_register['noc_block_dummy'] = get_noc_block_dummy_interface

