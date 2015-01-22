import os
import logging
import testfixtures

from pyvivado import interface, signal, info

from rfgnocchi import config

logger = logging.getLogger(__name__)

class MultInfo(info.ModuleInfo):

    dut_name = 'Mult'

    def __init__(self, params, top_level=False):
        self.interface_packages = []
        if top_level:
            self.width_A = int(params['top']['width_A'])
            self.width_B = int(params['top']['width_B'])
            self.width_P = int(params['top']['width_P'])
            self.drop_top_P = int(params['top']['drop_top_P'])
            self.latency = int(params['top']['latency'])
            self.cascade_out = int(params['top']['cascade_out'])
        super().__init__(params=params, top_level=top_level)
        if self.top_level:
            self.dut_parameters = {
                'WIDTH_A': self.width_A,
                'WIDTH_B': self.width_B,
                'WIDTH_P': self.width_P,
                'DROP_TOP_P': self.drop_top_P,
                'LATENCY': self.latency,
                'CASCADE_OUT': self.cascade_out,
            }

    def make_dependencies(self):
        return []

    def make_interface(self):
        assert(self.top_level)
        wires_in = (
            ('a_tdata', signal.StdLogicVector(width=self.width_A)),
            ('a_tlast', signal.std_logic_type),
            ('a_tvalid', signal.std_logic_type),
            ('b_tdata', signal.StdLogicVector(width=self.width_B)),
            ('b_tlast', signal.std_logic_type),
            ('b_tvalid', signal.std_logic_type),
            ('p_tready', signal.std_logic_type),
        )
        wires_out = (
            ('a_tready', signal.std_logic_type),
            ('b_tready', signal.std_logic_type),
            ('p_tdata', signal.StdLogicVector(width=self.width_P)),
            ('p_tlast', signal.std_logic_type),
            ('p_tvalid', signal.std_logic_type),
        )
        iface = interface.Interface(wires_in, wires_out, takes_clock=True, takes_reset=True)
        return iface

    def get_my_files(self, directory):
        filenames = [
            os.path.join(config.ettus_rfnocdir, 'mult.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_pipe_join.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_pipe.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_join.v'),
        ]
        interface_filenames = []
        return filenames, interface_filenames

assert(MultInfo.dut_name not in info.module_register)
info.module_register[MultInfo.dut_name] = MultInfo
