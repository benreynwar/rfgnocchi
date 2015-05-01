import os

from pyvivado import builder, interface, signal, utils

from rfgnocchi import config

minimum_2inputs_builder = builder.make_simple_builder(
    filenames=[os.path.join(config.basedir, 'maths', 'minimum_2inputs.vhd')],
)({})

minimum_stage_builder = builder.make_simple_builder(
    filenames=[os.path.join(config.basedir, 'maths', 'minimum_stage.vhd')],
    builders=[minimum_2inputs_builder],
    )({})


class MinimumBuilder(builder.Builder):

    template_fn=os.path.join(config.basedir, 'maths', 'minimum.vhd.t')

    def __init__(self, params):
        super().__init__(params)
        self.n_inputs = params['n_inputs']
        self.n_stages = signal.logceil(self.n_inputs)
        self.builders = [minimum_stage_builder]

    def output_filename(self, directory):
        return os.path.join(directory, builder.template_fn_to_output_fn(
            self.template_fn, self.params))
        

    def required_filenames(self, directory):
        return [self.output_filename(directory)]

    def build(self, directory):
        utils.format_file(
            template_filename=self.template_fn,
            output_filename=self.output_filename(directory),
            parameters={'n_inputs': self.n_inputs, 'n_stages': self.n_stages})


def get_minimum_interface(params):
    module_name = 'minimum'
    width = params['width']
    n_inputs = params['n_inputs']
    module_parameters = {
        'WIDTH': width,
    }
    builder = MinimumBuilder({
        'n_inputs': n_inputs,
    })
    wires_in = (
        ('reset', signal.std_logic_type),
        ('i_valid', signal.std_logic_type),
        ('i_data', signal.StdLogicVector(width=n_inputs*width)),
        ('o_ready', signal.std_logic_type),
    )
    wires_out = (
        ('o_data', signal.StdLogicVector(width=width)),
        ('o_valid', signal.std_logic_type),
        ('o_index', signal.StdLogicVector(width=signal.logceil(n_inputs))),
        ('i_ready', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk'],
        module_parameters=module_parameters,
    )
    return iface

interface.add_to_module_register('minimum', get_minimum_interface)


