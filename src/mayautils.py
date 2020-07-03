import logging
import os
import maya.cmds as cmds

import pymel.core as pmc
from pymel.core.system import Path
from pymel.core.system import versions

log = logging.getLogger(__name__)

class SceneFile(object):
    """This class represents a DCC software scene file
    The class will be a convenient object that we can use to manipulate our scene files.
    Attributes:
        dir (Path, optional): Directory to the scene file. Defaults to ''.
        descriptor (str, optional): Short descriptor of the scene file. Defaults to "main".
        version (int, optional): Version number. Defaults to 1.
        ext (str, optional): Extension. Defaults to "ma".
    """

    def __init__(self, dir='', descriptor='main', version=1, ext="ma"):
        #Delineates between new scene vs open scene with naming conventions
        if pmc.system.isModified():
            self._dir = Path(dir)
            self.descriptor = descriptor
            self.version = version
            self.ext = ext
        else:
            temp_path = Path(pmc.system.sceneName())
            self.dir = temp_path.parent
            file_name = temp_path.name
            self.descriptor = file_name.split("_v")[0]
            version = file_name.split("_v")[1].split(".")[0]
            self.version = int(version)
            self.ext = file_name.split(".")[1]

    @property
    def dir(self):
        return self._dir

    @dir.setter
    def dir(self, val):
        self._dir = Path(val)

    def basename(self):
        """Returns the DCC scene file's name"""
        name_pattern = "{descriptor}_v{version:03d}.{ext}"
        name = name_pattern.format(descriptor=self.descriptor,
                                    version=self.version,
                                    ext=self.ext)
        return name

    def path(self):
        """The function returns a path to scene file.
        This includes the drive letter, any directory path and the file name.
        Returns:
            Path: The path to the scene file.
        """
        return Path(self.dir) / self.basename()


    def save(self):
        """Saves the scene file.
        Returns:
            :obj:'Path': The path to the scene file if successful, None, otherwise.
        """
        try:
            pmc.system.saveAs(self.path())
        except RuntimeError:
            log.warning("Missing directories. Creating directories...")
            self.dir.makedirs_p()
            pmc.system.saveAs(self.path())

    def increment_and_save(self):
        files_list = self.dir.listdir()
        scene_list = list()
        for file in files_list:
            file_path = Path(file)
            scene = file_path.name
            scene_list.append(scene)
        highest_version = self.version

        for scene in scene_list:
            descriptor = scene.split("_v")[0]

            if descriptor == self.descriptor:
                version_str = scene.split("_v")[1].split(".")[0]
                version = int(version_str)

                if version > self.version:
                    highest_version = version

        self.version = highest_version + 1
        self.save()