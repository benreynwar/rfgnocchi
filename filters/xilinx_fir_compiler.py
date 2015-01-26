import os
import logging

from pyvivado import builder, interface, signal

from rfgnocchi import config

logger = logging.getLogger(__name__)

constants = {
    'coefficient_width': 25,
    'data_width': 16,
    'output_width': 48,
}

class XilinxFirCompilerBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = params['module_name']
        n_coefficients = params['n_coefficients']
        xco_filename = os.path.join(config.ettus_coregendir, 'simple_fir.xco')
        self.ip_params = builder.params_from_xco(xco_filename)
        # Override coefficients so that we get the correct number.
        # 21 is the xilinx default so this is probably a sensible choice.
        self.ip_params['coefficientvector'] = '1' + ',1'*(n_coefficients-1)
        self.ip_params['coefficient_file'] = 'no_coefficient_file_loaded'
        self.ip_params['coefficientsource'] = 'Vector'
        self.ips = [
            ('fir_compiler', self.ip_params, module_name),
        ]
        

def get_xilinx_fir_compiler_interface(params):
    factory_name = 'xilinx_fir_compiler'
    module_name = params['module_name']
    builder = XilinxFirCompilerBuilder(params)
    packages = []
    module_parameters = {}
    wires_in = (
        ('aresetn', signal.std_logic_type),
        ('s_axis_data_tvalid', signal.std_logic_type),
        ('s_axis_data_tlast', signal.std_logic_type),
        ('s_axis_config_tvalid', signal.std_logic_type),
        ('s_axis_reload_tvalid', signal.std_logic_type),
        ('s_axis_reload_tlast', signal.std_logic_type),
        ('m_axis_data_tready', signal.std_logic_type),
        ('s_axis_data_tdata', signal.StdLogicVector(width=32)),
        ('s_axis_config_tdata', signal.StdLogicVector(width=8)),
        ('s_axis_reload_tdata', signal.StdLogicVector(width=32)),
    )
    wires_out = (
        ('s_axis_data_tready', signal.std_logic_type),
        ('s_axis_config_tready', signal.std_logic_type),
        ('s_axis_reload_tready', signal.std_logic_type),
        ('m_axis_data_tvalid', signal.std_logic_type),
        ('m_axis_data_tlast', signal.std_logic_type),
        ('event_s_reload_tlast_missing', signal.std_logic_type),
        ('event_s_reload_tlast_unexpected', signal.std_logic_type),
        #('m_axis_data_tuser', signal.StdLogicVector(width=1)),
        ('m_axis_data_tdata', signal.StdLogicVector(width=96)),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, module_parameters=module_parameters,
        packages=packages, builder=builder, clock_name='aclk', needs_dummy=True,
        constants=constants, factory_name=factory_name,
    )
    return iface


assert('xilinx_fir_compiler' not in interface.module_register)
interface.module_register['xilinx_fir_compiler'] = get_xilinx_fir_compiler_interface
    

class XilinxFirCompiler(object):
    '''
    This is a python implementation of the Xilinx Fir Compiler.
    It is nowhere near complete and will only work correctly for the particular
    test cases where it has been tested.
    '''
    
    delay = 12

    def __init__(self, ip_params):
        self.ip_params = ip_params
        self.taps = [
            int(v) for v in ip_params['coefficientvector'].split(',')]
        self.n_taps = len(self.taps)
        self.reset()
        self.new_taps = []
        self.new_taps_full = False
        self.loading_tap_countdown = None
        
    def reset(self):
        self.old_values = [0] * self.n_taps
        self.output_pipe = [None] * (self.delay + self.n_taps)

    def process(self, inputs):
        if inputs['aresetn'] == 0:
            self.reset()
        if inputs['s_axis_data_tvalid'] == 1:
            data_tdata = signal.uint_to_sint(
                inputs['s_axis_data_tdata'], width=constants['data_width'])
            self.old_values.append(data_tdata)
            self.old_values.pop(0)
            new_output_data = sum([t*v for t, v in zip(self.taps, self.old_values)])
        else:
            new_output_data = None
        if inputs['s_axis_config_tvalid'] == 1:
            self.loading_tap_countdown = self.n_taps
            self.taps = self.new_taps
            self.new_taps = []
        else:
            if self.loading_tap_countdown == 0:
                self.loading_tap_countdown = None
                self.new_taps_full = False
            if self.loading_tap_countdown is not None:
                self.loading_tap_countdown -= 1
        if len(self.new_taps) == self.n_taps:
            self.new_taps_full = True
        if inputs['s_axis_reload_tvalid'] == 1:
            reload_tdata = signal.uint_to_sint(
                inputs['s_axis_reload_tdata'],
                width=constants['coefficient_width'])
            if not self.new_taps_full:
                self.new_taps.append(reload_tdata)
        self.output_pipe.append(new_output_data)
        current_output_data = self.output_pipe.pop(0)
        if current_output_data is None:
            m_axis_data_tvalid = 0
            m_axis_data_tdata = 0
        else:
            m_axis_data_tvalid = 1
            m_axis_data_tdata = signal.sint_to_uint(
                current_output_data, width=constants['output_width'])
        if self.new_taps_full:
            s_axis_reload_tready = 0
        else:
            s_axis_reload_tready = 1
        outputs = {
            's_axis_data_tready': 1,
            's_axis_config_tready': 1,
            's_axis_reload_tready': s_axis_reload_tready,
            'm_axis_data_tvalid': m_axis_data_tvalid,
            'm_axis_data_tlast': 0,
            'event_s_reload_tlast_missing': 0,
            'event_s_reload_tlast_unexpected': 0,
            'm_axis_data_tdata': m_axis_data_tdata,
        }
        return outputs
