"""
Audio decoder implemented with BASS dll.
"""

import ctypes
import ctypes.util
from typing import io

import numpy

BASS = ctypes.cdll.LoadLibrary(ctypes.util.find_library('bass'))


class AudioProcessError(Exception):
    """
    Error occurred during audio processing.
    """
    
    pass


def decode_audio(audio_file: io):
    """
    Decode audio from file-like object `audio_file`.
    
    Parameters
    ----------
    audio_file

    Returns
    -------

    """
    
    data = audio_file.read()
    if not BASS.BASS_Init(0):
        raise AudioProcessError("BASS Error: Initialization failed.")
    # Flags are Float, Mono, Decode, Prescan
    bass_stream = BASS.BASS_StreamCreateFile(
        True, data, 0, len(data), 0x220102)
    if bass_stream == 0:
        raise AudioProcessError("BASS Error: Failed to create stream with error code {}."
                                .format(BASS.BASS_ErrorGetCode()))
    # Flag is Frequency
    freq = ctypes.c_float()
    BASS.BASS_ChannelGetAttribute(bass_stream, 0x1, ctypes.byref(freq))
    if abs(freq.value - 44100) > 1e-3:
        raise AudioProcessError("Audio with non-44.1k sample rate not supported.")
    # Flag is Bytes
    decoded_len = BASS.BASS_ChannelGetLength(bass_stream, 0)
    if decoded_len == -1:
        raise AudioProcessError("BASS Error: Failed to get decoded length with error code {}."
                                .format(BASS.BASS_ErrorGetCode()))
    result = numpy.require(numpy.zeros(decoded_len // 4),
                           dtype='f', requirements=['A', 'O', 'W', 'C'])
    BASS.BASS_ChannelGetData(
        bass_stream, result.ctypes.data_as(ctypes.c_void_p), decoded_len)
    BASS.BASS_StreamFree(bass_stream)
    BASS.BASS_Free()
    return result
