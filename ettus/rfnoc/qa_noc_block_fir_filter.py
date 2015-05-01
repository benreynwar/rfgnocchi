import os
import unittest
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.ettus.rfnoc import noc_block_fir_filter
from rfgnocchi import config, chdr, noc

logger = logging.getLogger(__name__)

class TestNocBlockFirFilter(unittest.TestCase):
    
    def test_one(self):
        '''
        Tests the noc_block_fir_filter module using random coefficients and
        data.
        '''

        directory = os.path.abspath('proj_qa_testnocblockfirfilter')
        interface = noc_block_fir_filter.get_noc_block_fir_filter_interface(params={})
        coeff_width = interface.constants['coefficient_width']
        input_width = interface.constants['data_width']
        n_coefficients = interface.constants['n_coefficients']

        # Make a settings packet to set the taps of the filter.
        reload_address = 129
        config_address = 131

        max_coeff = pow(2, coeff_width-1)-1
        min_coeff = -pow(2, coeff_width-1)
        coefficients = [random.randint(min_coeff, max_coeff)
                       for i in range(n_coefficients)]
        uint_coefficients = [signal.sint_to_uint(c, width=coeff_width)
                             for c in coefficients]
        # The reload commands send the taps.
        settings_commands = [[reload_address, c] for c in uint_coefficients]
        # Change address in final setting to assert tlast.
        settings_commands[-1][0] = reload_address+1
        # And the config command activates them.
        settings_commands.append((config_address, 0))
        settings_packets = [chdr.CHDRPacket.create_settings_packet(
            address=address, value=value)
                            for address, value in settings_commands]
        
        # Make a packet with the data to filter.
        n_data = 100
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
        # Do the filtering in python so we know what data to expect out.
        expected_data = []
        extended_data = [0] * (n_coefficients-1) + complex_data
        for i in range(n_data):
            expected = sum([a*b for a, b in zip(
                coefficients, extended_data[i: i+n_coefficients])])
            # Divide the results by a scaling factor.
            # This implies coefficients go from 0 to 0.5 within their width.
            expected /= pow(2, coeff_width)
            maxval = pow(2, 15)-1
            minval = -pow(2, 15)
            def trunc_round(v):
                return round(max(minval, min(maxval, v)))
            expected = trunc_round(expected.real) + 1j * trunc_round(expected.imag)
            expected_data.append(expected)
                           
        data_packet = chdr.CHDRPacket.create_data_packet(data)

        # Create input simulation data.
        # Start off reseting for a bit.
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

        # Send the packets
        input_data = chdr.packets_to_noc_inputs(settings_packets + [data_packet])

        # And then wait for the output.
        for i in range(200):
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
        self.assertEqual(len(errors), 0)

        output_packets = chdr.noc_outputs_to_packets(output_data)
        # Filter out the settings replies.
        output_lumps = [p.data() for p in output_packets if not p.is_extension_context]
        # And check that we got the expected filtered data.
        self.assertEqual(len(output_lumps), 1)
        self.assertEqual(len(output_lumps[0]), n_data)
        output_uints = output_lumps[0]
        output_cs = [signal.uint_to_complex(ui, width=se_input_width)
                     for ui in output_uints]
        self.assertEqual(output_cs, expected_data)

        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
