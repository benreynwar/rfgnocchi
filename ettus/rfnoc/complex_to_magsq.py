import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi.ettus.rfnoc import mult
from rfgnocchi import config

logger = logging.getLogger(__name__)


class ComplexToMagSqBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.simple_filenames = [
            os.path.join(config.ettus_rfnocdir, 'complex_to_magsq.v'),
            os.path.join(config.ettus_rfnocdir, 'split_complex.v'),
        ]
        self.builders = [
            mult.MultBuilder({}),
            mult.MultAddBuilder({}),
        ]
