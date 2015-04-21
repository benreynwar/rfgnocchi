import os
import unittest
import shutil
import logging
import cmath
import math

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.blocks import controller_inner
from rfgnocchi import config

logger = logging.getLogger(__name__)

def make_blank_d():
    return {
        'reset': 0,
        'clear': 0,
        'i_error_tdata': 0,
        'i_error_tvalid': 0,
        'i_config_tdata': 0,
        'i_config_tvalid': 0,
        'o_phase_tready': 0,
    }


class TestControllerInnerCompiler(unittest.TestCase):

    def test_one(self):
    
        directory = os.path.abspath('proj_qa_testcontrollerinner')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = controller_inner.get_controller_inner_interface({})

        # Make wait data.  Sent while initialising.
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index < 10:
                reset = 1
            else:
                reset = 0
            input_d = make_blank_d()
            input_d['reset'] = reset
            wait_data.append(input_d)
        input_data = []
        # Initially set the alpha and beta to 0.
        input_d = make_blank_d()
        input_d['clear'] = 1
        input_d['i_config_tvalid'] = 1
        input_d['i_config_tdata'] = 0
        input_data.append(input_d)
        # It shouldn't matter what values of error we send
        # in now we should always get 0's out.
        error_width = 16
        es = [d*pow(2, error_width-6) for d in range(20)]
        for e in es:
            input_d = make_blank_d()
            input_d['o_phase_tready'] = 1
            input_d['i_error_tdata'] = e
            input_d['i_error_tvalid'] = 1
            input_data.append(input_d)
        # Wait for 10 to flush.
        for i in range(10):
            input_d = make_blank_d()
            input_d['o_phase_tready'] = 1
            input_data.append(input_d)
        # Set alpha to pow(2, 14).
        # This should divide error by 2 and add it to phase.
        alpha = pow(2, 14)
        beta = 0
        config_data = alpha * pow(2, 16) + beta
        input_d = make_blank_d()
        input_d['clear'] = 1
        input_d['i_config_tvalid'] = 1
        input_d['i_config_tdata'] = config_data
        input_data.append(input_d)
        # Now outputs should be errors input divided by 2.
        error_width = 16
        phase_width = 16
        es = [d*pow(2, error_width-6) for d in range(20)]
        for e in es:
            input_d = make_blank_d()
            input_d['o_phase_tready'] = 1
            input_d['i_error_tdata'] = e
            input_d['i_error_tvalid'] = 1
            input_data.append(input_d)
        # Wait for 10 to flush.
        for i in range(10):
            input_d = make_blank_d()
            input_d['o_phase_tready'] = 1
            input_data.append(input_d)
        # Set beta to pow(2, 14)
        alpha = 0
        beta = pow(2, 14)
        config_data = alpha * pow(2, 16) + beta
        input_d = make_blank_d()
        input_d['clear'] = 1
        input_d['i_config_tvalid'] = 1
        input_d['i_config_tdata'] = config_data
        input_data.append(input_d)
        # Send nothing for 10 to flush multipliers
        for i in range(10):
            input_d = make_blank_d()
            input_d['i_error_tdata'] = 0
            input_d['i_error_tvalid'] = 1
            input_d['o_phase_tready'] = 1
            input_data.append(input_d)
        # Send in a single error of value 8
        # This should set freq to 4
        input_d = make_blank_d()
        input_d['o_phase_tready'] = 1
        input_d['i_error_tdata'] = 8
        input_d['i_error_tvalid'] = 1
        input_data.append(input_d)
        for i in range(19):
            input_d = make_blank_d()
            input_d['o_phase_tready'] = 1
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
        errors, output_data = p.run_simulation(
            input_data=wait_data+input_data, runtime=runtime)

        phases = [d['o_phase_tdata'] for d in output_data if d['o_phase_tvalid']]
        # After 50 inputs we should have 0 phase
        self.assertEqual(phases[49], 0)
        # After 80 inputs the phase should be half the sum of errors
        self.assertEqual(phases[79], (sum(es)/2) % pow(2, phase_width))
        # After 110 inputs we should have a freq of 4
        freq = (phases[109] - phases[108]) % pow(2, phase_width)
        self.assertEqual(freq, 4)

        self.assertEqual(len(errors), 0)

        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
