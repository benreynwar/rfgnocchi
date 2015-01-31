import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config

logger = logging.getLogger(__name__)


class MultBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.simple_filenames = [
            os.path.join(config.ettus_rfnocdir, 'mult.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_pipe_join.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_pipe.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_join.v'),
        ]

class MultAddBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.simple_filenames = [
            os.path.join(config.ettus_rfnocdir, 'mult_add.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_pipe_mac.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_join.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_pipe.v'),
        ]

class MultRCBuilder(builder.Builder):
    
    def __init__(self, params={}):
        super().__init__(params)
        self.builders = [
            MultBuilder(params),
        ]
        self.simple_filenames = [
            os.path.join(config.ettus_rfnocdir, 'mult_rc.v'),
        ]


def get_mult_interface(params):
    module_name = 'Mult'
    width_A = params['width_A']
    width_B = params['width_B']
    width_P = params['width_P']
    drop_top_P = params['drop_top_P']
    latency = params['latency']
    cascade_out = params['cascade_out']
    builder = MultBuilder()
    packages = []
    module_parameters = {
        'WIDTH_A': width_A,
        'WIDTH_B': width_B,
        'WIDTH_P': width_P,
        'DROP_TOP_P': drop_top_P,
        'LATENCY': latency,
        'CASCADE_OUT': cascade_out,
    }
    wires_in = (
        ('reset', signal.std_logic_type),
        ('a_tdata', signal.StdLogicVector(width=width_A)),
        ('a_tlast', signal.std_logic_type),
        ('a_tvalid', signal.std_logic_type),
        ('b_tdata', signal.StdLogicVector(width=width_B)),
        ('b_tlast', signal.std_logic_type),
        ('b_tvalid', signal.std_logic_type),
        ('p_tready', signal.std_logic_type),
    )
    wires_out = (
        ('a_tready', signal.std_logic_type),
        ('b_tready', signal.std_logic_type),
        ('p_tdata', signal.StdLogicVector(width=width_P)),
        ('p_tlast', signal.std_logic_type),
        ('p_tvalid', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, module_parameters=module_parameters,
        packages=packages, builder=builder, clock_names=['clk'])
    return iface


assert('Mult' not in interface.module_register)
interface.module_register['Mult'] = get_mult_interface
