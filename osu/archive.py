"""
osu! beatmap archive abstraction and implementations.
"""

import os
from zipfile import ZipFile
from typing import io, Iterable, Dict

import numpy

from osu.audio_decoder import decode_audio
from osu.beatmap import Beatmap


class Archive:
    """
    Abstract base for osu! beatmap archives.
    """
    
    def __init__(self):
        self.audios: Dict[str, numpy.ndarray] = {}
    
    def open_audio(self, filename: str) -> numpy.ndarray:
        """
        Open an audio file, with regard to cached audios.
        
        Parameters
        ----------
        filename : str
            Open the file with the given filename.

        Returns
        -------
        numpy.ndarray
            A numpy array which represents the audio content.
        """
        
        if filename not in self.audios:
            with self.__open_content(filename) as audio_file:
                self.audios[filename] = decode_audio(audio_file)
        return self.audios[filename]
    
    def __open_content(self, filename: str, mode: str = "r") -> io:
        raise NotImplementedError(
            'Abstract base class "Archive" does not provide an implementation for this.')
    
    def __list_content(self) -> Iterable[str]:
        raise NotImplementedError(
            'Abstract base class "Archive" does not provide an implementation for this.')
    
    def __iter__(self):
        for filename in self.__list_content():
            if filename[-4:] == '.osu':
                with self.__open_content(filename) as beatmap_file:
                    yield Beatmap(beatmap_file, self.open_audio)
    
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass


class OszArchive(Archive):
    """
    .osz archive implementation.
    """
    
    def __init__(self, oszfile):
        super().__init__()
        self.oszfile = oszfile if isinstance(oszfile, ZipFile) else ZipFile(oszfile)
    
    def __open_content(self, filename: str, mode: str = "r") -> io:
        return self.oszfile.open(filename, mode)
    
    def __list_content(self) -> Iterable[str]:
        return self.oszfile.namelist()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.oszfile.close()


class DirArchive(Archive):
    """
    Directory archive implementation.
    """
    
    def __init__(self, path: str):
        super().__init__()
        assert os.path.isdir(path)
        self.path = path
    
    def __open_content(self, filename: str, mode: str = "r") -> io:
        return open(os.path.join(self.path, filename, mode))
    
    def __list_content(self) -> Iterable[str]:
        return os.listdir(self.path)
