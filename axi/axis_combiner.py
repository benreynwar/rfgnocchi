from pyvivado import builder, interface, signal

class AxisCombinerBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        n_input_streams = params['n_input_streams']
        input_stream_width = params['input_stream_width']
        assert(input_stream_width % 8 == 0)
        module_name = params['module_name']
        ip_params = {
            'HAS_ACLKEN': 0,
            # Produces error signal if meta-info for input streams does not
            # match
            'HAS_CMD_ERR': 0, 
            'HAS_TKEEP': 0,
            'HAS_TLAST': 1,
            'HAS_TSTRB': 0,
            'MASTER_PORT_NUM': 0,
            'NUM_SI': n_input_streams,
            'TDATA_NUM_BYTES': input_stream_width//8,
            'TDEST_WIDTH': 0,
            'TID_WIDTH': 0,
            'TUSER_WIDTH': 0,
        }
        self.ips = [
            ('axis_combiner', ip_params, module_name),
        ]

        
def get_axis_combiner_interface(params):
    factory_name = 'AxisCombiner'
    module_name = params['module_name']
    n_input_streams = params['n_input_streams']
    input_stream_width = params['input_stream_width']
    builder = AxisCombinerBuilder(params)
    packages = []
    module_parameters = {}
    output_width = n_input_streams * input_stream_width
    wires_in = (
        ('aresetn', signal.std_logic_type),
        ('s_axis_tdata', signal.StdLogicVector(width=output_width)),
        ('s_axis_tlast', signal.StdLogicVector(width=n_input_streams)),
        ('s_axis_tvalid', signal.StdLogicVector(width=n_input_streams)),
        ('m_axis_tready', signal.std_logic_type),
    )
    wires_out = (
        ('m_axis_tdata', signal.StdLogicVector(width=output_width)),
        ('m_axis_tlast', signal.std_logic_type),
        ('m_axis_tvalid', signal.std_logic_type),
        ('s_axis_tready', signal.StdLogicVector(width=n_input_streams)),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name, factory_name=factory_name,
        parameters=params, module_parameters=module_parameters,
        packages=packages, builder=builder, clock_names=['aclk'], needs_dummy=True)
    return iface


assert('AxisCombiner' not in interface.module_register)
interface.module_register['AxisCombiner'] = get_axis_combiner_interface
