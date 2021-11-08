import os

from qnap import Qnap

class FileStation(Qnap):
    """
    Access QNAP FileStation.
    """

    def list_share(self):
        """
        List all shared folders.
        """
        return self.get(self.fstation_endpoint(
            func='get_tree',
            params={
                'is_iso': 0,
                'node': 'share_root',
            }
        ), False)

    def list(self, path, limit=10000):
        """
        List files in a folder.
        """
        return self.get(self.fstation_endpoint(
            func='get_list',
            params={
                'is_iso': 0,
                'limit': limit,
                'path': path
            }
        ), False)

    def get_file_info(self, path):
        """
        Get file information.
        """
        dir_path = os.path.dirname(path)
        file_name = os.path.basename(path)
        return self.get(self.fstation_endpoint(
            func='stat',
            params={
                'path': dir_path,
                'file_name': file_name
            }
        ), False)

    def search(self, path, pattern):
        """
        Search for files/folders.
        """
        return self.get(self.fstation_endpoint(
            func='search',
            params={
                'limit': 10000,
                'start': 0,
                'source_path': path,
                'keyword': pattern
            }
        ), False)