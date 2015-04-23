from pyvivado import builder

class FifoGeneratorBuilder(builder.Builder):
    
    implementation_types = (
        'independent_clocks_distributed_ram',
        'independent_clocks_block_ram',
    )

    def __init__(self, params):
        '''
        We assume that the fifo generator is being used to create a 
        2 clock native FIFO.  We assume that because that's what it's
        being used for in the NocShell and that's our only reason
        for implementing this at the moment.
        '''
        super().__init__(params)
        self.implementation_type = params['implementation_type']
        self.width = params['width']
        self.depth = params['depth']
        assert(self.implementation_type in self.implementation_types)
        self.ip_params = (
            ('fifo_implementation', self.implementation_type),
            ('performance_options', 'first_word_fall_through'),
            ('interface_type', 'native'),
            ('input_data_width', self.width),
            ('output_data_width', self.width),
            ('input_depth', self.depth),
            ('output_depth', self.depth),
            # These counts seem unused, but they're required so we get
            # the same interface as expected.
            ('read_data_count', 'true'),
            ('write_data_count', 'true'),
        ))
        self.ips = (
            ('fifo_generator', self.ip_params, params['module_name']),
        )

