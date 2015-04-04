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

from rfgnocchi.filters import freq_xlating_fir_filter_ccf
from rfgnocchi import config

logger = logging.getLogger(__name__)


def make_blank_d():
    return {
        'reset': 0,
        'i_data_tdata': 0,
        'i_data_tlast': 0,
        'i_data_tvalid': 0,
        'i_fir_reload_tdata': 0,
        'i_fir_reload_tlast': 0,
        'i_fir_reload_tvalid': 0,
        'i_fir_config_tdata': 0,
        'i_fir_config_tlast': 0,
        'i_fir_config_tvalid': 0,
        'i_rotator_config_tdata': 0,
        'i_rotator_config_tvalid': 0,
        'o_tready': 1,
    }

def make_config_ds(new_center, decimation_rate, taps):
    '''
    new_center goes from -0.5 to 0.5
    '''
    freq = new_center * 2 * math.pi
    phase_width = 16
    f = pow(2, phase_width)
    freq_as_int = int(freq * f)
    while freq_as_int >= f:
        freq_as_int -= f
    while freq_as_int < 0:
        freq_as_int += f
        coefficients = [1] + [0]*params['n_coefficients']

def make_fir_config_ds(taps):
    config_ds = []
    # Set the new taps
    for i, tap in enumerate(taps):
        # We're assuming that s_axi_reload_tready is always active.
        if i == len(taps)-1:
            is_last = 1
        else:
            is_last = 0
        input_d = make_bank_d()
        input_d['s_axis_fir_reload_tvalid'] = 1
        input_d['s_axis_fir_reload_tdata'] = tap
        input_d['s_axis_fir_reload_tlast'] = is_last
        config_ds.append(input_d)
    # Activate the new taps
    input_d = make_bank_d()
    input_d['s_axis_fir_config_tvalid'] = 1
    config_ds.append(input_d)
    return config_ds
    
    

class TestFreqXlatingFirFilter(unittest.TestCase):

    def test_one(self):
    
        directory = os.path.abspath('proj_qa_testfreqxlatingfirfilterccf')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = freq_xlating_fir_filter_ccf.get_freq_xlating_fir_filter_ccf_interface({
            'n_taps': 21,
            'decimation_rate': 2,
        })

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

        # Make input and expected data
        input_data = []

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

        self.assertEqual(len(errors), 0)
        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
