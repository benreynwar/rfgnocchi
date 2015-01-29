import os
import unittest
import shutil
import random
import logging
import math
import cmath

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.xilinx import complex_multiplier
from rfgnocchi import config

logger = logging.getLogger(__name__)


class TestComplexMultiplier(unittest.TestCase):

    def test_one(self):

        params = {
            'module_name': 'complex_multiplier'
        }
    
        directory = os.path.abspath('proj_qa_testcomplexmultplier')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = complex_multiplier.get_complex_multiplier_interface(params)
        input_width = interface.constants['input_width']
        output_width = interface.constants['output_width']
        se_input_width = interface.constants['se_input_width']
        se_output_width = interface.constants['se_output_width']

        # Make wait data.  Sent while initialising.
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            input_d = {
                's_axis_a_tvalid': 0,
                's_axis_a_tlast': 0,
                's_axis_a_tdata': 0,
                's_axis_b_tvalid': 0,
                's_axis_b_tdata': 0,
                'm_axis_dout_tready': 0,
            }
            wait_data.append(input_d)
        # Make input and expected data
        input_data = []
        # Try to multiply real numbers first
        n_data = 100
        inputs_A = [pow(2, input_width-1)]*100
        inputs_B = range(n_data)
        for a, b in zip(inputs_A, inputs_B):
            input_d = {
                's_axis_a_tvalid': 1,
                's_axis_a_tlast': 0,
                's_axis_a_tdata': a,
                's_axis_b_tvalid': 1,
                's_axis_b_tdata': b,
                'm_axis_dout_tready': 1,
            }
            input_data.append(input_d)

        p = project.FileTestBenchProject.create(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )
        t = p.wait_for_most_recent_task()
        errors = t.get_errors_and_warnings()
        self.assertEqual(len(errors), 0)

        # Run the simulation
        runtime = '{} ns'.format((len(input_data) + 20) * 10)
        errors, output_data = p.run_hdl_simulation(
            input_data=wait_data+input_data, runtime=runtime)

        out_tdata = [d['m_axis_dout_tdata']
                     for d in output_data if d['m_axis_dout_tvalid']]

        out_cs = [signal.uint_to_complex(d, width=se_output_width)
                  for d in out_tdata]

        import pdb
        pdb.set_trace()

        self.assertEqual(len(errors), 0)

    def check_output(self, output_data, expected_data):
        self.assertTrue(len(output_data) >= len(expected_data))
        output_data = output_data[:len(expected_data)]
        testfixtures.compare(output_data, expected_data)
        
        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
