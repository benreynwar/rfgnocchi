import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi import config

logger = logging.getLogger(__name__)

class BlkMemGenBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = params['module_name']
        write_width_A = params['write_width_A']
        write_depth_A = params['write_depth_A']
        read_width_A = params['read_width_A']
        self.ip_params = [
            ('write_width_A', write_width_A),
            ('write_depth_A', write_depth_A),
            ('read_width_A', read_width_A),
        ]
        self.ip_params_dict = dict(self.ip_params)
        self.ips = [
            ('blk_mem_gen', self.ip_params, module_name),
        ]
        

def get_blk_mem_gen_interface(params):
    factory_name = 'xilinx_blk_mem_gen'
    module_name = params['module_name']
    builder = BlkMemGenBuilder(params)
    packages = []
    width = params['write_width_A']
    depth = params['write_depth_A']
    wires_in = (
        ('aresetn', signal.std_logic_type),
        ('ena', signal.std_logic_type),
        ('wea', signal.StdLogicVector(width=1)),
        ('addra', signal.StdLogicVector(width=signal.logceil(depth))),
        ('dina', signal.StdLogicVector(width=width)),
    )
    wires_out = (
        ('douta', signal.StdLogicVector(width=width)),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, 
        packages=packages, builder=builder, clock_names=['clka'], needs_dummy=True,
        factory_name=factory_name,
    )
    return iface


assert('xilinx_blk_mem_gen' not in interface.module_register)
interface.module_register['xilinx_blk_mem_gen'] = get_blk_mem_gen_interface

class FirCompiler(object):
    '''
    This is a python implementation of the Xilinx Fir Compiler.
    It is nowhere near complete and will only work correctly for the particular
    test cases where it has been tested.
    '''
    
    delay = 12

    def __init__(self, ip_params):
        self.ip_params = ip_params
        self.data_width = int(ip_params_dict['data_width'])
        self.coefficient_width = int(ip_params_dict['coefficient_width'])
        self.decimation_rate = int(ip_params_dict['decimation_rate'])
        self.se_data_width = sign_extend_to_8_bit_boundary(self.data_width)
        self.taps = list(reversed([
            int(v) for v in ip_params_dict['coefficientvector'].split(',')]))
        self.n_taps = len(self.taps)
        self.output_width = (self.data_width + self.coefficient_width +
                             signal.logceil(self.n_taps))
        self.se_output_width = sign_extend_to_8_bit_boundary(self.output_width)
        self.reset()
        self.new_taps = []
        self.new_taps_full = False
        self.loading_tap_countdown = None
        self.decim_counter = 0
        
    def reset(self):
        self.old_values_A = [0] * self.n_taps
        self.old_values_B = [0] * self.n_taps
        pipe_length = (self.delay + self.n_taps - (self.decimation_rate-1)//2)
        self.output_pipe = [None] * pipe_length
        self.output_pipe_valid = [0] * pipe_length

    def process(self, inputs):
        if inputs['aresetn'] == 0:
            self.reset()
        if inputs['s_axis_data_tvalid'] == 1:
            f_data = pow(2, self.se_data_width)
            udata_A = inputs['s_axis_data_tdata'] // f_data
            udata_B = inputs['s_axis_data_tdata'] % f_data
            sdata_A = signal.uint_to_sint(
                udata_A, width=self.se_data_width)
            sdata_B = signal.uint_to_sint(
                udata_B, width=self.se_data_width)
            self.old_values_A.append(sdata_A)
            self.old_values_B.append(sdata_B)
            self.old_values_A.pop(0)
            self.old_values_B.pop(0)
            soutput_A = sum([t*v for t, v in zip(self.taps, self.old_values_A)])
            soutput_B = sum([t*v for t, v in zip(self.taps, self.old_values_B)])
            uoutput_A = signal.sint_to_uint(
                soutput_A, width=self.se_output_width)
            uoutput_B = signal.sint_to_uint(
                soutput_B, width=self.se_output_width)
            f_output = pow(2, self.se_output_width)
            new_output_data = uoutput_A * f_output + uoutput_B
        else:
            new_output_data = None
        if inputs['s_axis_config_tvalid'] == 1:
            self.loading_tap_countdown = self.n_taps
            self.taps = self.new_taps
            self.new_taps = []
            self.decim_counter = 0
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
                width=self.coefficient_width)
            if not self.new_taps_full:
                self.new_taps.append(reload_tdata)
        self.output_pipe.append(new_output_data)
        if new_output_data is None:
            new_valid = 0
        else:
            self.decim_counter = (self.decim_counter + 1) % self.decimation_rate
            if self.decim_counter == 0:
                new_valid = 1
            else:
                new_valid = 0
        self.output_pipe_valid.append(new_valid)
        current_output_data = self.output_pipe.pop(0)
        if current_output_data is None:
            m_axis_data_tdata = 0
        else:
            m_axis_data_tdata = current_output_data
        if self.new_taps_full:
            s_axis_reload_tready = 0
        else:
            s_axis_reload_tready = 1
        outputs = {
            's_axis_data_tready': 1,
            's_axis_config_tready': 1,
            's_axis_reload_tready': s_axis_reload_tready,
            'm_axis_data_tvalid': self.output_pipe_valid.pop(0),
            'm_axis_data_tlast': 0,
            'event_s_reload_tlast_missing': 0,
            'event_s_reload_tlast_unexpected': 0,
            'm_axis_data_tdata': m_axis_data_tdata,
        }
        return outputs
