import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi.xilinx.fir_compiler import FirCompilerBuilder
from rfgnocchi.xilinx.fifo_generator import FifoGeneratorBuilder
from rfgnocchi import config

logger = logging.getLogger(__name__)

class NocBlockFirFilterBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = 'noc_block_fir_filter'
        n_coefficients = 21
        simple_fir_builder = FirCompilerBuilder({
            'module_name': 'simple_fir',
            'n_taps': n_coefficients,
        })
        fifo_short_2clk_builder = FifoGeneratorBuilder({
            'implementation_type': 'independent_clocks_distributed_ram',
            'width': 72,
            'depth': 32,
            'module_name': 'fifo_short_2clk',
        })
        fifo_4k_2clk_builder = FifoGeneratorBuilder({
            'implementation_type': 'independent_clocks_block_ram',
            'width': 72,
            'depth': 512,
            'module_name': 'fifo_4k_2clk',
        })
        self.constants = {
            'n_coefficients': n_coefficients,
            'coefficient_width': int(
                simple_fir_builder.ip_params_dict['coefficient_width']),
            'data_width': int(
                simple_fir_builder.ip_params_dict['data_width']),
            'output_width': int(
                simple_fir_builder.constants['output_width']),
        }        
        self.builders = [
            simple_fir_builder,
            fifo_short_2clk_builder,
            fifo_4k_2clk_builder,
        ]
        ettus_dependencies = {
            'fifo': (
                'axi_fifo_2clk_cascade',
                'axi_fifo_2clk',
                'axi_fifo_short',
                'axi_fifo_cascade',
                'axi_fifo',
                'axi_fifo_flop',
                'axi_fifo_flop2',
                'axi_fifo_bram',
                'axi_mux4',
                'axi_demux4',
                'axi_mux',
                'axi_demux',
                'axi_packet_gate',
            ),
            'control': (
                'ram_2port',
                'radio_ctrl_proc',
                'setting_reg',
            ),
            'timing': (
                'time_compare',
            ),
            'rfnoc': (
                'noc_shell',
                'noc_output_port',
                'noc_input_port',
                'axi_wrapper',
                'chdr_deframer',
                'chdr_framer',
                # Specific to this block
                'noc_block_fir_filter',
                'axi_round_and_clip_complex',
                'split_complex',
                'axi_round_and_clip',
                'join_complex',
                'axi_round',
                'axi_clip',
            ),
            'packet_proc': (
                'source_flow_control',
            ),
            'vita': (
                'tx_responder',
                'trigger_context_pkt',
                'context_packet_gen',
            ),
        }
        self.simple_filenames = []
        for directoryname, modules in ettus_dependencies.items():
            for module in modules:
                fn = os.path.join(
                    config.ettus_fpgadir, directoryname, module + '.v')
                self.simple_filenames.append(fn)


def get_noc_block_fir_filter_interface(params):
    module_name = 'noc_block_fir_filter'
    builder = NocBlockFirFilterBuilder(params)
    wires_in = (
        ('bus_rst', signal.std_logic_type),
        ('ce_rst', signal.std_logic_type),
        ('i_tvalid', signal.std_logic_type),
        ('i_tlast', signal.std_logic_type),
        ('i_tdata', signal.StdLogicVector(width=64)),
        ('o_tready', signal.std_logic_type),
    )
    wires_out = (
        ('o_tvalid', signal.std_logic_type),
        ('o_tlast', signal.std_logic_type),
        ('o_tdata', signal.StdLogicVector(width=64)),
        ('i_tready', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['ce_clk', 'bus_clk'],
        constants=builder.constants,
    )
    return iface


assert('noc_block_fir_filter' not in interface.module_register)
interface.module_register['noc_block_fir_filter'] = get_noc_block_fir_filter_interface

