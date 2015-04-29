import os
import unittest
import logging
import random

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
        # Create some setting packets
        settings_commands = [
            (100, 1),
            (7, 6),
            (23, 189),
        ]
        settings_packets = [chdr.make_settings_packet([command]) for command in 
                            settings_commands]
        # Make some data packets.
        n_data_packets = 5
        data_packets = []
        possible_packet_sizes = [2, 10, 16]
        max_data = pow(2, 32)-1
        input_data_lumps = []
        input_combined_data_lumps = []
        for i in range(n_data_packets):
            packet_size = possible_packet_sizes[
                random.randint(0, len(possible_packet_sizes)-1)]
            assert(packet_size % 2 == 0)
            data_lump = [random.randint(0, max_data)
                         for i in range(packet_size)]
            input_data_lumps.append(data_lump)
            data_packets.append(chdr.make_data_packet(data_lump))
            combined_lump = []
            first = True
            combined = None
            for d in data_lump:
                if not first:
                    combined += d 
                    combined_lump.append(combined)
                else:
                    combined = d * pow(2, 32)
                first = not first
            input_combined_data_lumps.append(combined_lump)

        wait_data = []
        for i in range(10):
            wait_data.append(noc_shell.make_inputs(bus_rst=1, reset=1))
        for i in range(10):
            wait_data.append(noc_shell.make_inputs())

        noc_inputs = chdr.packets_to_noc_inputs(settings_packets)
        noc_inputs += chdr.packets_to_noc_inputs(data_packets)
        input_data = [noc_shell.make_inputs_from_noc_inputs(d, str_sink_tready=1)
                      for d in noc_inputs]
        for i in range(50):
            input_data.append(noc_shell.make_inputs(str_sink_tready=1))

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
        output_data_lumps = []
        data_packet = []
        for d in output_data:
            if d['str_sink_tvalid']:
                data_packet.append(d['str_sink_tdata'])
                if d['str_sink_tlast']:
                    output_data_lumps.append(data_packet[1:])
                    data_packet = []
        import pdb
        pdb.set_trace()
        self.assertEqual(settings_commands, output_settings)
        self.assertEqual(output_data_lumps, input_combined_data_lumps)
        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
