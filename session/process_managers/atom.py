import os

from session.process_managers.common import ProcessManager

HOME_DIR = os.path.expanduser('~')
ATOM_DIR = os.path.join(HOME_DIR, '.atom')


class AtomManager(ProcessManager):
    name = 'atom'
    pname = 'Atom'
    filepaths = [
        os.path.join(ATOM_DIR, 'storage', 'application.json'),
        os.path.join(ATOM_DIR, 'blob-store', 'BLOB')]


# def get_loaded_dirs():
#     with open(os.path.join(FILEPATHS[0])) as data_file:
#         return json.load(data_file)[0]['initialPaths']
