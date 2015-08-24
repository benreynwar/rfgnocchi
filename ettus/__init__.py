import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config
from rfgnocchi.xilinx.fifo_generator import FifoGeneratorBuilder

logger = logging.getLogger(__name__)

# Define the more complicated builders first.
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
    
# And then a structure from which we can generate the simpler builders.
builder_structure = {
    # FIFO
    'axi_fifo_2clk_cascade': (('fifo', 'axi_fifo_2clk_cascade.v'),
                              'axi_fifo_short',
                              'axi_fifo_2clk',),
    'axi_fifo_short': (('fifo', 'axi_fifo_short.v'),),
    'axi_fifo_2clk': (('fifo', 'axi_fifo_2clk.v'),
                      fifo_short_2clk_builder,
                      fifo_4k_2clk_builder,
                      'axi_fifo',),
    'axi_fifo': (('fifo', 'axi_fifo.v'),
                 'axi_fifo_flop',
                 'axi_fifo_short',
                 'axi_fifo_bram',),
    'axi_fifo_flop': (('fifo', 'axi_fifo_flop.v'),),
    'axi_fifo_bram': (('fifo', 'axi_fifo_bram.v'),
                      'ram_2port',),
    'axi_mux4': (('fifo', 'axi_mux4.v'),
                 'axi_fifo_short'),
    'axi_demux4': (('fifo', 'axi_demux4.v'),),
    'axi_packet_gate': (('fifo', 'axi_packet_gate.v'),
                         'axi_fifo_cascade',),
    'axi_fifo_cascade': (('fifo', 'axi_fifo_cascade.v'),
                         'axi_fifo_short',),
    'axi_mux': (('fifo', 'axi_mux.v'),
                'axi_fifo_short',),
    'axi_demux': (('fifo', 'axi_demux.v'),),
    # RFNoC
    'noc_output_port': (('rfnoc', 'noc_output_port.v'),
                        'axi_packet_gate',
                        'source_flow_control',),
    'noc_input_port': (('rfnoc', 'noc_input_port.v'),
                       'axi_fifo_cascade',
                       'tx_responder',
                       ),
    'noc_shell': (('rfnoc', 'noc_shell.v'),
                  'axi_fifo_2clk_cascade',
                  'axi_mux4',
                  'axi_demux4',
                  'radio_ctrl_proc',
                  'setting_reg',
                  'noc_output_port',
                  'axi_mux',
                  'axi_demux',
                  'noc_input_port',),
    'axi_wrapper': (('rfnoc', 'axi_wrapper.v'),
                    'chdr_deframer',
                    'chdr_framer',
                    'axi_fifo_short',
                    'axi_fifo',),
    'chdr_deframer': (('rfnoc', 'chdr_deframer.v'),
                      'axi_fifo',),
    'chdr_framer': (('rfnoc', 'chdr_framer.v'),
                    'axi_fifo',
                    'axi_fifo_short',),
    'axi_round_and_clip_complex': (('rfnoc', 'axi_round_and_clip_complex.v'),
                                   'split_complex',
                                   'axi_round_and_clip',
                                   'join_complex',),
    'split_complex': (('rfnoc', 'split_complex.v'),),
    'axi_round_and_clip': (('rfnoc', 'axi_round_and_clip.v'),
                           'axi_round',
                           'axi_clip',),
    'axi_round': (('rfnoc', 'axi_round.v'),
                  'axi_fifo',),
    'axi_clip': (('rfnoc', 'axi_clip.v'),
                 'axi_fifo',),
    'join_complex': (('rfnoc', 'join_complex.v'),),
    'complex_to_magsq': (('rfnoc', 'complex_to_magsq.v'),
                         'split_complex',
                         'mult',
                         'mult_add',),
    'mult': (('rfnoc', 'mult.v'),
             'axi_pipe_join',
             'DSP48E1',),
    'mult_rc': (('rfnoc', 'mult_rc.v'),
                'mult',),
    'mult_add': (('rfnoc', 'mult_add.v'),
                 'axi_pipe_mac',
                 'DSP48E1',),
    'DSP48E1': (),
    'axi_pipe_join': (('rfnoc', 'axi_pipe_join.v'),
                      'axi_pipe',
                      'axi_join',),
    'axi_pipe': (('rfnoc', 'axi_pipe.v'),),
    'axi_join': (('rfnoc', 'axi_join.v'),),
    'axi_pipe_mac': (('rfnoc', 'axi_pipe_mac.v'),
                      'axi_pipe',
                      'axi_join',),
    # Vita
    'tx_responder': (('vita', 'tx_responder.v'),
                     'trigger_context_pkt',
                     'axi_fifo_short',
                     'context_packet_gen',),
    'trigger_context_pkt': (('vita', 'trigger_context_pkt.v'),
                            'setting_reg',),
    'context_packet_gen': (('vita', 'context_packet_gen.v'),),
    # Packet Proc
    'source_flow_control': (('packet_proc', 'source_flow_control.v'),
                            'setting_reg',),
    # Control
    'ram_2port': (('control', 'ram_2port.v'),),
    'radio_ctrl_proc': (('control', 'radio_ctrl_proc.v'),
                        'time_compare',),
    'setting_reg': (('control', 'setting_reg.v'),),
    # Timing
    'time_compare': (('timing', 'time_compare.v'),),
}

prepared_builders = {}
in_progress_builder_names = set()

def get_builder(name):
    if name in prepared_builders:
        b = prepared_builders[name]
    elif name not in builder_structure:
        raise Exception('Unknown name {}'.format(name))
    else:
        in_progress_builder_names.add(name)
        deps = builder_structure[name]
        filenames = []
        builders = []
        for dep in deps:
            if isinstance(dep, builder.Builder):
                builders.append(dep)
            elif isinstance(dep, tuple):
                filenames.append(os.path.join(
                    config.ettus_fpgadir, dep[0], dep[1]))
            elif dep in prepared_builders:
                builders.append(prepared_builders[dep])
            elif dep in in_progress_builder_names:
                raise Exception('Circular reference found: {}'.format(dep))
            elif dep in builder_structure:
                builders.append(get_builder(dep))
            else:
                raise Exception('Unknown dependency {}'.format(dep))
        in_progress_builder_names.remove(name)
        b = builder.make_simple_builder(
            filenames=filenames,
            builders=builders,
        )({})
    return b
