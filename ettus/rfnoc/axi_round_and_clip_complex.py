import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config

logger = logging.getLogger(__name__)

class AxiRoundAndClipComplexBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.simple_filenames = [
            os.path.join(config.ettus_rfnocdir, 'axi_round_and_clip_complex.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_round_and_clip.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_round.v'),
            os.path.join(config.ettus_rfnocdir, 'axi_clip.v'),
            os.path.join(config.ettus_rfnocdir, 'split_complex.v'),
            os.path.join(config.ettus_rfnocdir, 'join_complex.v'),
        ]

