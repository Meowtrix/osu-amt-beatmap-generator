'''Data abstraction on osu! beatmaps.'''
from typing import io, Callable
import numpy

class Beatmap:
    '''Parsed beatmap information for an osu! beatmap.'''

    def __init__(self, beatmap_file: io, audio_provider: Callable[[str], numpy.ndarray]):
        raise NotImplementedError('TODO')
