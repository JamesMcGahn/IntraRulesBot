import os
import re


class PathManager:
    @staticmethod
    def path_exists(path: str, makepath: bool, raiseError: bool = False):
        """
        Args:
            path (str): the path of the file
            makepath (bool): if the path doesn't exist, create the path
            raiseError (bool,optional): if the path doesn't exist' raise error

        Returns:
            bool: True the path exists or if the path doesnt exist but is then is created
        """
        if os.path.exists(path):
            return True
        elif not os.path.exists(path) and makepath:
            os.makedirs(path)
            return True
        else:
            if raiseError:
                import utils.logger as logger

                log = logger.Logger()
                log.insert("Filepath does not exist", "WARN")
                raise ValueError("Filepath does not exist")
            else:
                return False

    @staticmethod
    def regex_path(path):
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)

        return {"path": directory, "filename": name, "ext": ext}

    @staticmethod
    def check_dup(folderpath, filename, ext):
        # if folder path doesnt exist - create it
        PathManager.path_exists(folderpath, True)
        # remove linux illegal characters
        if isinstance(filename, int):
            filename = str(filename)
        filename = filename.replace("/", "-").replace("\0", "")
        path = f"{folderpath}{filename}{ext}"
        # check if filename exists
        if PathManager.path_exists(path, False):
            count = 1
            newpath = f"{folderpath}{filename}-({count}){ext}"
            # if filename exists append -(count) to make unique filename
            # check to see if filename already exists - if it does increase count in filename
            while PathManager.path_exists(newpath, False):
                newpath = f"{folderpath}{filename}-({count}){ext}"
                count += 1
            path = newpath
        return path
