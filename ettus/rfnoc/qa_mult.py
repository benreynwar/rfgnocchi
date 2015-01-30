import os
import unittest
import shutil
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.ettus.rfnoc import mult
from rfgnocchi import config

logger = logging.getLogger(__name__)

class TestMult(unittest.TestCase):
    
    def test_one(self):

        directory = os.path.abspath('proj_qa_testmult')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        MAX_WIDTH_A = 25
        MAX_WIDTH_B = 18
        MAX_WIDTH_P = 48

        width_A = 16
        width_B = 16
        drop_bottom_P = 15
        zeros_on_A = MAX_WIDTH_A - width_A
        zeros_on_B = MAX_WIDTH_B - width_B
        max_width_P = MAX_WIDTH_P - zeros_on_A - zeros_on_B
        drop_top_P = 6
        width_P = max_width_P - drop_top_P - drop_bottom_P

        params = {
            'width_A': width_A,
            'width_B': width_B,
            'width_P': width_P,
            'drop_top_P': drop_top_P,
            'latency': 3,
            'cascade_out': 0,
        }
        n_discard_bits = width_A + width_B - 1 - width_P
        discard_f = pow(2, n_discard_bits)

        # Make wait data.  Sent while initialising.
        n_data = 100
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            input_d = {
                'reset': 1,
                'a_tdata': 0,
                'a_tlast': 0,
                'a_tvalid': 0,
                'b_tdata': 0,
                'b_tlast': 0,
                'b_tvalid': 0,
                'p_tready': 0,
            }
            wait_data.append(input_d)
        # Make input and expected data
        input_data = []
        expected_data = []
        max_data_A = pow(2, width_A)-1
        max_data_B = pow(2, width_B)-1
        for data_index in range(n_data):
            a = random.randint(0, max_data_A)
            b = random.randint(0, max_data_B)
            sa = signal.uint_to_sint(a, width_A)
            sb = signal.uint_to_sint(b, width_B)
            sp = sa * sb
            p = signal.sint_to_uint(sp, width_A+width_B-1)
            p = p//discard_f
            input_d = {
                'reset': 0,
                'a_tdata': a,
                'a_tlast': 1,
                'a_tvalid': 1,
                'b_tdata': b,
                'b_tlast': 1,
                'b_tvalid': 1,
                'p_tready': 1,
            }
            expected_d = {
                'a_tready': 1,
                'b_tready': 1,
                'p_tdata': p,
                'p_tlast': 1,
                'p_tvalid': 1,
            }
            input_data.append(input_d)
            expected_data.append(expected_d)

        interface = mult.get_mult_interface(params)
        p = project.FileTestBenchProject.create(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )
        t = p.wait_for_most_recent_task()
        errors = t.get_errors()
        self.assertEqual(len(errors), 0)

        # Run the simulation
        runtime = '{} ns'.format((len(wait_data+input_data) + 20) * 10)
        errors, output_data = p.run_hdl_simulation(
            input_data=wait_data+input_data, runtime=runtime)
        latency = 3
        delay = 1 + n_wait_lines + latency
        import pdb
        pdb.set_trace()
        self.check_output(output_data[delay:], expected_data)
        self.assertEqual(len(errors), 0)

    def check_output(self, output_data, expected_data):
        self.assertTrue(len(output_data) >= len(expected_data))
        output_data = output_data[:len(expected_data)]
        testfixtures.compare(output_data, expected_data)
        
        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
