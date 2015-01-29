import logging

from pyvivado import builder, interface, signal

logger = logging.getLogger(__name__)


class ComplexMultiplierBuilder(builder.Builder):

    def __init__(self, params):
        super().__init__(params)
        # Input width is 16+16 for inputs
        # Output is (33+7) + (33+7)
        self.ip_params = {
            'flowcontrol': 'blocking',
            'hasatlast': 'true',
        }
        self.ips = [
            ('cmpy', self.ip_params, params['module_name'])
        ] 
        self.constants = {
            'input_width': 16,
            'output_width': 33,
            'se_input_width': 16,
            'se_output_width': 40,
            'latency': 6,
        }


def get_complex_multiplier_interface(params):
    factory_name = 'xilinx_complex_multiplier'
    module_name = params['module_name']
    builder = ComplexMultiplierBuilder(params)
    input_width = builder.constants['input_width']
    se_input_width = builder.constants['se_input_width']
    output_width = builder.constants['output_width']
    se_output_width = builder.constants['se_output_width']
    constants = builder.constants
    wires_in = (
        ('s_axis_a_tdata', signal.StdLogicVector(width=2*se_input_width)),
        ('s_axis_a_tvalid', signal.std_logic_type),
        ('s_axis_a_tlast', signal.std_logic_type),
        ('s_axis_b_tdata', signal.StdLogicVector(width=2*se_input_width)),
        ('s_axis_b_tvalid', signal.std_logic_type),
        ('m_axis_dout_tready', signal.std_logic_type),
    )
    wires_out = (
        ('s_axis_a_tready', signal.std_logic_type),
        ('s_axis_b_tready', signal.std_logic_type),
        ('m_axis_dout_tvalid', signal.std_logic_type),
        ('m_axis_dout_tlast', signal.std_logic_type),
        ('m_axis_dout_tdata', signal.StdLogicVector(width=2*se_output_width)),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['aclk'],
        needs_dummy=True, factory_name=factory_name, constants=constants,
    )
    return iface


assert('xilinx_complex_multiplier' not in interface.module_register)
interface.module_register['xilinx_complex_multiplier'] = (
    get_complex_multiplier_interface)
