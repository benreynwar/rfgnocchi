import os
import unittest
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.ettus.rfnoc import noc_block_fir_filter
from rfgnocchi import config, chdr

logger = logging.getLogger(__name__)

class TestNocBlockFirFilter(unittest.TestCase):
    
    def test_one(self):
        '''
        This doesn't test functionality. Just that everything gets built
        and simulations.

        Currently it is not functional.
        '''

        directory = os.path.abspath('proj_qa_testnocblockfirfilter')
        interface = noc_block_fir_filter.get_noc_block_fir_filter_interface(params={})
        coeff_width = interface.constants['coefficient_width']
        input_width = interface.constants['data_width']
        n_coefficients = interface.constants['n_coefficients']

        # Make a settings packet to set the taps of the filter.
        reload_address = 129
        config_address = 130

        max_coeff = pow(2, coeff_width-1)-1
        min_coeff = -pow(2, coeff_width-1)
        coefficients = [random.randint(min_coeff, max_coeff)
                       for i in range(n_coefficients)]
        uint_coefficients = [signal.sint_to_uint(c, width=coeff_width)
                             for c in coefficients]
        # The reload commands send the taps.
        settings_commands = [(reload_address, c) for c in uint_coefficients]
        # And the config command activatees them.
        settings_commands.append((config_address, 0))
        settings_packets = [chdr.CHDRPacket.create_settings_packet(
            address=address, value=value)
                            for address, value in settings_commands]
        
        # Make a packet with the data to filter.
        n_data = 30
        input_width = 16
        se_input_width = 16
        max_input = pow(2, input_width-1)-1
        min_input = -pow(2, input_width-1)
        f = pow(2, se_input_width)
        complex_data = [random.randint(min_input, max_input) 
                        + 1j*random.randint(min_input, max_input)
                        for i in range(n_data)]
        data = [signal.complex_to_uint(c, width=se_input_width)
                for c in complex_data]
        data_packet = chdr.CHDRPacket.create_data_packet(data)

        wait_data = []
        for i in range(10):
            wait_data.append({
                'bus_rst': 1,
                'ce_rst': 1,
                'i_tvalid': 0,
                'i_tlast': 0,
                'i_tdata': 0,
                'o_tready': 0,
            })
        for i in range(10):
            wait_data.append({
                'bus_rst': 0,
                'ce_rst': 0,
                'i_tvalid': 0,
                'i_tlast': 0,
                'i_tdata': 0,
                'o_tready': 1,
            })

        input_data = chdr.packets_to_noc_inputs(settings_packets + [data_packet])

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

        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
