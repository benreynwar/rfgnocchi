import os
import unittest
import shutil
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.xilinx import fir_compiler
from rfgnocchi import config

logger = logging.getLogger(__name__)


class TestFirCompiler(unittest.TestCase):

    def test_one(self):
        n_coefficients = 6
        params = {
            'module_name': 'simple_fir',
            'n_taps': n_coefficients,
            'decimation_rate': 3,
        }
        self.helper(params)

    def helper(self, params):
    
        directory = os.path.abspath('proj_qa_testfircompiler')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = fir_compiler.get_fir_compiler_interface(params)
        coeff_width = interface.constants['coefficient_width']
        input_width = interface.constants['data_width']
        se_input_width = interface.constants['se_data_width']
        se_output_width = interface.constants['se_output_width']
        decimation_rate = interface.constants['decimation_rate']

        # Make wait data.  Sent while initialising.
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index in (10, 11):
                aresetn = 0
            else:
                aresetn = 1
            input_d = {
                'aresetn': aresetn,
                's_axis_data_tvalid': 0, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': 0,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 0, 
                's_axis_reload_tlast': 0,
                's_axis_reload_tdata': 0,
                'm_axis_data_tready': 0,
            }
            wait_data.append(input_d)
        # Make input and expected data
        input_data = []
        # Confirm that initially the taps have a single 1 entry.
        n_data0 = (20//decimation_rate) * decimation_rate
        max_input = pow(2, input_width-1)-1
        min_input = -pow(2, input_width-1)
        f = pow(2, input_width)
        #data0 = [
        #    signal.sint_to_uint(
        #        random.randint(min_input, max_input), width=se_input_width) +
        #    signal.sint_to_uint(
        #        random.randint(min_input, max_input), width=se_input_width)*f*0                
        #    for i in range(n_data0)]
        data0 = range(n_data0)
        for d0 in data0:
            input_d = {
                'aresetn': 1,
                's_axis_data_tvalid': 1, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': d0,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 0, 
                's_axis_reload_tlast': 0,
                's_axis_reload_tdata': 0,
                'm_axis_data_tready': 1,
            }
            input_data.append(input_d)
        for i in range(25):
            input_d = {
                'aresetn': 1,
                's_axis_data_tvalid': 0, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': 0,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 0, 
                's_axis_reload_tlast': 0,
                's_axis_reload_tdata': 0,
                'm_axis_data_tready': 1,
            }
            input_data.append(input_d)
        
        max_coeff = pow(2, coeff_width-1)-1
        min_coeff = -pow(2, coeff_width-1)
        filter1 = [random.randint(min_coeff, max_coeff)
                   for i in range(params['n_taps'])]
        filter1 = (1, 1, 1, 1, 1, 0)
        assert(len(filter1) % decimation_rate == 0)
        coefficients = []
        for i in range(len(filter1)//decimation_rate, 0, -1):
            coefficients += filter1[(i-1)*decimation_rate:i*decimation_rate]
        for i, coeff in enumerate(coefficients):
            # We're assuming that s_axi_reload_tready is always active.
            if i == len(coefficients)-1:
                is_last = 1
            else:
                is_last = 0
            input_d = {
                'aresetn': 1,
                's_axis_data_tvalid': 0, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': 0,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 1, 
                's_axis_reload_tlast': is_last,
                's_axis_reload_tdata': signal.sint_to_uint(
                    coeff, width=coeff_width),
                'm_axis_data_tready': 1,
            }
            input_data.append(input_d)
        # Do nothing for a couple clock cycles
        long_enough_wait_A = 10
        long_enough_wait_B = 20
        for i in range(long_enough_wait_A):
            input_data.append({
                'aresetn': 1,
                's_axis_data_tvalid': 0, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': 0,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 0, 
                's_axis_reload_tlast': 0,
                's_axis_reload_tdata': 0,
                'm_axis_data_tready': 1,
            })
        # Use the new coefficients
        input_data.append({
            'aresetn': 1,
            's_axis_data_tvalid': 0, 
            's_axis_data_tlast': 0,
            's_axis_data_tdata': 0,
            's_axis_config_tvalid': 1,
            's_axis_config_tdata': 0,
            's_axis_reload_tvalid': 0, 
            's_axis_reload_tlast': 0,
            's_axis_reload_tdata': 0,
            'm_axis_data_tready': 1,
        })
        for i in range(long_enough_wait_B):
            input_data.append({
                'aresetn': 1,
                's_axis_data_tvalid': 0, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': 0,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 0, 
                's_axis_reload_tlast': 0,
                's_axis_reload_tdata': 0,
                'm_axis_data_tready': 1,
            })
        # Test new coefficients
        n_data1 = (30//decimation_rate) * decimation_rate
        max_input = pow(2, input_width-1)-1
        min_input = -pow(2, input_width-1)
        #data1 = [random.randint(min_input, max_input) 
        #         + 1j*random.randint(min_input, max_input)
        #         for i in range(n_data1)]
        data1 = range(n_data1)
        for d1 in data1:
            input_d = {
                'aresetn': 1,
                's_axis_data_tvalid': 1, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': signal.complex_to_uint(
                    d1, width=se_output_width),
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 0, 
                's_axis_reload_tlast': 0,
                's_axis_reload_tdata': 0,
                'm_axis_data_tready': 1,
            }
            input_data.append(input_d)
        for i in range(20):
            input_data.append({
                'aresetn': 1,
                's_axis_data_tvalid': 0, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': 0,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 0, 
                's_axis_reload_tlast': 0,
                's_axis_reload_tdata': 0,
                'm_axis_data_tready': 1,
            })
            
        # We are running data0 through filter 1, 0, 0....
        filter0 = [1] + [0] * (params['n_taps']-1)
        data0 = [0]*(params['n_taps']-1) + list(data0)
        filtered0 = []
        for i in range(params['n_taps']-1, len(data0)):
            f = 0
            for j, tap in enumerate(filter0):
                f += data0[i-j]*tap
            filtered0.append(f)
        decimated0 = filtered0[2::3]
        # Then data1 through filter coefficients
        data1 = data0[-(params['n_taps']-1):] + list(data1)
        filtered1 = []
        for i in range(params['n_taps']-1, len(data1)):
            f = 0
            for j, tap in enumerate(filter1):
                f += data1[i-j]*tap
            filtered1.append(f)
        decimated1 = filtered1[2::3]

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
        self.assertEqual(len(errors), 0)

        out_decimated = [
            signal.uint_to_complex(d['m_axis_data_tdata'], width=se_output_width)
            for d in output_data if d['m_axis_data_tvalid']]
        import pdb
        pdb.set_trace()
        self.assertEqual((decimated0 + decimated1), out_decimated)

        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
