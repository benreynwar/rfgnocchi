import os
import unittest
import shutil
import random
import logging
import cmath
import math

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.blocks import rotator_cc
from rfgnocchi import config

logger = logging.getLogger(__name__)


class TestRotatorCCCompiler(unittest.TestCase):

    def test_one(self):
    
        directory = os.path.abspath('proj_qa_testrotatorcc')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = rotator_cc.get_rotator_cc_interface({})

        # Make wait data.  Sent while initialising.
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index < 10:
                reset = 1
            else:
                reset = 0
            input_d = {
                'reset': reset,
                'i_data_tdata': 0,
                'i_data_tvalid': 0,
                'i_data_tlast': 0,
                'i_config_tdata': 0,
                'i_config_tvalid': 0,
                'o_tready': 0,
            }
            wait_data.append(input_d)
        # Make input and expected data
        input_data = []
        # Set the rotation frequency
        # Rotate every 2^6 samples
        phase_width = 16
        se_phase_width = 16
        freq = pow(2, phase_width-6)
        input_d = {
            'reset': 0,
            'i_data_tdata': 0,
            'i_data_tvalid': 0,
            'i_data_tlast': 0,
            'i_config_tdata': freq,
            'i_config_tvalid': 1,
            'o_tready': 0,
        }
        input_data.append(input_d)
        scale = pow(2, 8)
        c_data = [d*scale for d in range(100)]
        for c in c_data:
            input_d = { 
                'reset': 0,
                'i_data_tdata': c,
                'i_data_tvalid': 1,
                'i_data_tlast': 0,
                'i_config_tdata': 0,
                'i_config_tvalid': 0,
                'o_tready': 1,
            }
            input_data.append(input_d)
        # Flush all the results out.
        for i in range(20):
            input_d = { 
                'reset': 0,
                'i_data_tdata': 0,
                'i_data_tvalid': 0,
                'i_data_tlast': 0,
                'i_config_tdata': 0,
                'i_config_tvalid': 0,
                'o_tready': 1,
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

        complex_width = 32
        output_cs = [
            signal.uint_to_complex(d['o_tdata'], width=complex_width//2)
            for d in output_data if d['o_tvalid']
        ]
        polars = [cmath.polar(c) for c in output_cs]
        mags = [p[0] for p in polars]
        phases = [p[1] for p in polars]

        # phase of first 10 outputs is nonsense due to initialization of nco.
        # Chop first 20 results off
        delta_phase = freq*2*math.pi/pow(2, phase_width)
        input_polars = [cmath.polar(c) for c in c_data]
        input_mags = [p[0] for p in input_polars]
        input_phases = [p[1] for p in input_polars]
        base_phase = phases[20] - input_phases[20] - 20*delta_phase

        expected_rotations = [cmath.rect(1, base_phase + delta_phase*i)
                              for i in range(len(c_data))]
        expected_cs = [c*r for c, r in zip(c_data, expected_rotations)]

        import pdb
        pdb.set_trace()

        self.assertTrue(len(output_cs) >= len(expected_cs))
        for o, e in zip(output_cs[20:], expected_cs[20:]):
            distance = abs(o-e)
            self.assertTrue(distance < 4)

        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
