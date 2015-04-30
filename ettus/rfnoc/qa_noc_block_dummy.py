import os
import unittest
import random
import logging

import testfixtures

from pyvivado import project, signal

from rfgnocchi.ettus.rfnoc import noc_block_dummy
from rfgnocchi import config, chdr, noc

logger = logging.getLogger(__name__)

class TestNocBlockDummy(unittest.TestCase):
    
    def test_one(self):
        random.seed(0)
        directory = os.path.abspath('proj_qa_testnocblockdummy')
        interface = noc_block_dummy.get_noc_block_dummy_interface(params={})
        
        # Make some settings packets.
        # We have one config so addresses 129 and 130 will write to
        # that config (130 will assert tlast, 129 won't).
        settings_commands = [
            (130, 189),
            (129, 6),
            (131, 26),
            (128, 1),
        ]
        configed = 6
        settings_packets = [chdr.CHDRPacket.create_settings_packet(
            address=address, value=value)
                            for address, value in settings_commands]

        # Make some data packets.
        n_data_packets = 5
        data_packets = []
        possible_packet_sizes = [2, 10, 16]
        max_data = pow(2, 32)-1
        input_data_lumps = []
        expected_data_lumps = []
        for i in range(n_data_packets):
            packet_size = possible_packet_sizes[
                random.randint(0, len(possible_packet_sizes)-1)]
            assert(packet_size % 2 == 0)
            data_lump = list(range(packet_size))#[random.randint(0, max_data)
                         #for i in range(packet_size)]
            expected_output_lump = []
            extended_data_lump = [0, 0] + data_lump
            for i in range(len(data_lump)):
                expected_output_lump.append(sum(extended_data_lump[i: 3+i])+configed)
            expected_data_lumps.append(expected_output_lump)
            input_data_lumps.append(data_lump)
            data_packets.append(chdr.CHDRPacket.create_data_packet(data_lump))

        wait_data = []
        for i in range(10):
            wait_data.append(noc.make_inputs(bus_rst=1, ce_rst=1))
        for i in range(10):
            wait_data.append(noc.make_inputs(o_tready=1))

        input_data = chdr.packets_to_noc_inputs(settings_packets + data_packets)
        for i in range(50):
            input_data.append(noc.make_inputs(o_tready=1))

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
        output_packets = chdr.noc_outputs_to_packets(output_data)
        # Filter out the settings replies.
        output_lumps = [p.data() for p in output_packets if not p.is_extension_context]
        self.assertEqual(len(errors), 0)
        self.assertEqual(expected_data_lumps, output_lumps)

        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
