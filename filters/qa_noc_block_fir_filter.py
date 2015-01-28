import os
import unittest
import shutil
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.filters import noc_block_fir_filter
from rfgnocchi import config, chdr

logger = logging.getLogger(__name__)

class TestNocBlockFirFilter(unittest.TestCase):
    
    def test_one(self):

        directory = os.path.abspath('proj_qa_testnocblockfirfilter')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

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
        # And the config command actives them.
        settings_commands.append((config_address, 0))
        settings_packet = chdr.make_settings_packet(settings_commands)
        
        # Make a packet with the data to filter.
        n_data = 30
        input_width = 16
        se_input_width = 16
        max_input = pow(2, input_width-1)-1
        min_input = -pow(2, input_width-1)
        f = pow(2, se_input_width)
        data = [
            signal.sint_to_uint(
                random.randint(min_input, max_input), width=se_input_width) +
            signal.sint_to_uint(
                random.randint(min_input, max_input), width=se_input_width)*f                
            for i in range(n_data)]
        data_packet = chdr.make_data_packet(data)

        input_data = chdr.packets_to_noc_inputs((settings_packet, data_packet))

        p = project.FileTestBenchProject.create(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )
        t = p.wait_for_most_recent_task()
        errors = t.get_errors()
        self.assertEqual(len(errors), 0)

        runtime = '{} ns'.format((len(input_data) + 20) * 10)
        errors, output_data = p.run_hdl_simulation(
            input_data=[], runtime=runtime)
        self.assertEqual(len(errors), 0)
        import pdb
        pdb.set_trace()
        

        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
