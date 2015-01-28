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

from rfgnocchi.xilinx import dds_compiler
from rfgnocchi import config

logger = logging.getLogger(__name__)


class TestXilinxDDSCompiler(unittest.TestCase):

    def test_one(self):

        phase_width = 16
        output_width = 16
        params = {
            'phase_width': phase_width,
            'output_width': output_width,
            'module_name': 'nco'
        }
    
        directory = os.path.abspath('proj_qa_testxilinxddscompiler')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = dds_compiler.get_dds_compiler_interface(params)
        se_phase_width = interface.constants['se_phase_width']
        se_output_width = interface.constants['se_output_width']

        output_mag = pow(2, phase_width-1)-2

        # Make wait data.  Sent while initialising.
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index < 10:
                aresetn = 0
            else:
                aresetn = 1
            input_d = {
                'aresetn': aresetn,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                'm_axis_data_tready': 0,
            }
            wait_data.append(input_d)
        # Make input and expected data
        input_data = []
        # Do nothing for 40 steps
        for i in range(40):
            input_d = {
                'aresetn': 1,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                'm_axis_data_tready': 1,
            }
            input_data.append(input_d)
        # Set everything to 0
        offset = 0
        freq = 0
        input_d = {
            'aresetn': 1,
            's_axis_config_tvalid': 1,
            's_axis_config_tdata': offset * pow(2, se_phase_width) + freq,
            'm_axis_data_tready': 0,
        }
        input_data.append(input_d)
        # And gather data.
        n_data1 = 40
        for index1 in range(n_data1):
            input_d = {
                'aresetn': 1,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                'm_axis_data_tready': 1,
            }
            input_data.append(input_d)
        # Set a small offset
        offset = pow(2, phase_width-4)
        freq = 0
        input_d = {
            'aresetn': 1,
            's_axis_config_tvalid': 1,
            's_axis_config_tdata': offset * pow(2, se_phase_width) + freq,
            'm_axis_data_tready': 0,
        }
        input_data.append(input_d)
        # And gather data.
        n_data1 = 40
        for index1 in range(n_data1):
            input_d = {
                'aresetn': 1,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                'm_axis_data_tready': 1,
            }
            input_data.append(input_d)
        # Now go back to an offset of 0
        offset = 0
        freq = 0
        input_d = {
            'aresetn': 1,
            's_axis_config_tvalid': 1,
            's_axis_config_tdata': offset * pow(2, se_phase_width) + freq,
            'm_axis_data_tready': 0,
        }
        input_data.append(input_d)
        # And gather data.
        n_data1 = 40
        for index1 in range(n_data1):
            input_d = {
                'aresetn': 1,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                'm_axis_data_tready': 1,
            }
            input_data.append(input_d)
        # And finally apply a small frequency
        offset = 0
        freq = pow(2, phase_width-8)
        input_d = {
            'aresetn': 1,
            's_axis_config_tvalid': 1,
            's_axis_config_tdata': offset * pow(2, se_phase_width) + freq,
            'm_axis_data_tready': 0,
        }
        input_data.append(input_d)
        # And gather data.
        n_data1 = 40
        for index1 in range(n_data1):
            input_d = {
                'aresetn': 1,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                'm_axis_data_tready': 1,
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

        out_tdata = [d['m_axis_data_tdata'] for d in output_data if d['m_axis_data_tvalid']]
        f = pow(2, se_phase_width)
        cc = [d % f for d in out_tdata]
        ss = [d // f for d in out_tdata]
        
        def map_s_to_v(v, output_width):
            #  1 = 01111110 in full amplitude mode
            # http://www.xilinx.com/support/documentation/ip_documentation/dds_compiler/v6_0/pg141-dds-compiler.pdf (pg 44)
            sv = signal.uint_to_sint(v, width=output_width)
            mag = pow(2, phase_width-1)-2
            return sv/mag

        output_s = [map_s_to_v(d, output_width=se_output_width) for d in ss]
        output_c = [map_s_to_v(d, output_width=se_output_width) for d in cc]
        output_phase = [cmath.phase(complex(c, s))
                        for c, s in zip(output_c, output_s)]
        
        # First 40 outputs are before anything is set
        # Next 40 outputs are after we've set offset=0, freq=0
        base_phase = output_phase[79]
        # Next 40 outputs are after we've set offset=power(2,-4)*2*pi, freq=0
        next_phase = output_phase[119]
        phase_change = (next_phase - base_phase)
        if phase_change < 0:
            phase_change += math.pi * 2
        expected_phase_change = pow(2, -4)*2*math.pi
        # Then we go back to offset=0 for 40
        phase_0again = output_phase[159]
        # And finally apply a freq of pow(2,-8)*2*pi
        phase_with_freq_1 = output_phase[198]
        phase_with_freq_2 = output_phase[199]
        phase_step = (phase_with_freq_2 - phase_with_freq_1)
        if phase_step < 0:
            phase_step += math.pi * 2
        expected_phase_step = pow(2, -8)*2*math.pi

        import pdb
        pdb.set_trace()

        self.assertTrue(abs(phase_change-expected_phase_change) < 1e-6)
        self.assertTrue(abs(base_phase-phase_0again) < 1e-6)
        self.assertTrue(abs(phase_step-expected_phase_step) < 1e-6)
        self.assertEqual(len(errors), 0)

    def check_output(self, output_data, expected_data):
        self.assertTrue(len(output_data) >= len(expected_data))
        output_data = output_data[:len(expected_data)]
        testfixtures.compare(output_data, expected_data)
        
        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
