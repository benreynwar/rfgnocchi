import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi import config

logger = logging.getLogger(__name__)

class DDSCompilerBuilder(builder.Builder):

    partspresent_options = (
        'sin_cos_lut_only',
        'phase_generator_and_sin_cos_lut',
    )
    
    def __init__(self, params):
        super().__init__(params)
        module_name = params['module_name']
        phase_width = params['phase_width']
        output_width = params['output_width']
        partspresent = params.get(
            'partspresent', 'phase_generator_and_sin_cos_lut')
        has_aresetn = params.get('has_resetn', 'true')
        assert(partspresent in self.partspresent_options)
        self.ip_params = [
            ('partspresent', partspresent),
        ]
        if partspresent == 'phase_generator_and_sin_cos_lut':
            self.ip_params += [
                ('parameter_entry', 'hardware_parameters'),
                ('phase_increment', 'programmable'),
                ('phase_offset', 'programmable'),
                ('phase_width', phase_width),
                ('has_phase_out', 'false'),
            ]
        self.ip_params += [
            ('has_tready', 'true'),
            ('output_width', output_width),
            ('has_aresetn', has_aresetn),
        ]
        self.ips = [
            ('dds_compiler', self.ip_params, module_name),
        ]
        

def get_dds_compiler_interface(params):
    factory_name = 'xilinx_dds_compiler'
    module_name = params['module_name']
    builder = DDSCompilerBuilder(params)
    se_phase_width = int(math.ceil(params['phase_width']/8)*8)
    se_output_width = int(math.ceil(params['output_width']/8)*8)
    constants = {
        'se_phase_width': se_phase_width,
        'se_output_width': se_output_width,
    }
    # Significant (mostly < 20?) latency between applying configs and effect.
    # Very weird behavior close to initialization.
    wires_in = (
        ('aresetn', signal.std_logic_type),
        ('s_axis_config_tvalid', signal.std_logic_type),
        # Config has phase_offset in MSBs and freq in LSBs.
        # Freq and offset 0->2pi maps to 0->2^phase_width
        ('s_axis_config_tdata', signal.StdLogicVector(width=se_phase_width*2)),
        ('m_axis_data_tready', signal.std_logic_type),
    )
    wires_out = (
        ('s_axis_config_tready', signal.std_logic_type),
        ('m_axis_data_tvalid', signal.std_logic_type),
        # Output 
        ('m_axis_data_tdata', signal.StdLogicVector(width=2*se_output_width)),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['aclk'],
        needs_dummy=True, factory_name=factory_name, constants=constants,
    )
    return iface


assert('xilinx_dds_compiler' not in interface.module_register)
interface.module_register['xilinx_dds_compiler'] = get_dds_compiler_interface

