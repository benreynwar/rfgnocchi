import os
import unittest
import logging

import testfixtures

from pyvivado import project, signal

from rfgnocchi.ettus.rfnoc import noc_shell
from rfgnocchi import config, chdr

logger = logging.getLogger(__name__)

class TestNocShell(unittest.TestCase):
    
    def test_one(self):
        '''
        Currently just testing settings.
        N.B. Only one setting per settings packet.
        '''

        directory = os.path.abspath('proj_qa_testnocshell')
        params={
            'input_ports': 1,
            'output_ports': 1,
        }
        interface = noc_shell.get_noc_shell_interface(params=params)
        # Create a setting packet
        settings_commands = [
            (100, 1),
            (7, 6),
            (23, 189),
        ]
        settings_packets = [chdr.make_settings_packet([command]) for command in 
                            settings_commands]

        wait_data = []
        for i in range(10):
            wait_data.append(noc_shell.make_inputs(bus_rst=1, reset=1))
        for i in range(10):
            wait_data.append(noc_shell.make_inputs())

        noc_inputs = chdr.packets_to_noc_inputs(settings_packets)
        input_data = [noc_shell.make_inputs_from_noc_inputs(d)
                      for d in noc_inputs]
        for i in range(50):
            input_data.append(noc_shell.make_inputs())

        p = project.FileTestBenchProject.create_or_update(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )
        t = p.wait_for_most_recent_task()
        errors = t.get_errors()
        self.assertEqual(len(errors), 0)

        runtime = '{} ns'.format((len(wait_data+input_data) + 20) * 10)
        errors, output_data = p.run_simulation(
            input_data=wait_data+input_data, runtime=runtime)
        self.assertEqual(len(errors), 0)
        output_settings = [(d['set_addr'], d['set_data']) for d in output_data
                           if d['set_stb']]
        self.assertEqual(settings_commands, output_settings)
        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
