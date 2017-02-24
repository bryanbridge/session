import os

from session.process_managers.common import ProcessManager, copy_files

HOME_DIR = os.path.expanduser('~')
FINDER_STATE_DIR = os.path.join(
    HOME_DIR,
    'Library',
    'Saved Application State',
    'com.apple.finder.savedState',
)


class FinderManager(ProcessManager):
    name = 'finder'
    pname = 'Finder'

    def get_filepaths(self):
        return [
            os.path.join(FINDER_STATE_DIR, x)
            for x in os.listdir(FINDER_STATE_DIR)]

    def save(self, session):
        self.clear_stored_files(session)

        try:
            copy_files(self.build_paths(session, mode='save'))
        except IOError:
            pass  # ...(new) session created, process never started

    def load(self, session):
        self.clear_state()

        try:
            copy_files(self.build_paths_2(session))
        except IOError:
            self.clear_state()  # ...session has no state for this process

        self.shutdown()

    def reset(self):
        self.clear_state()
        self.shutdown()

    def shutdown(self):
        # ...Not sure why in regular version, check_running caught in inf. loop
        os.system('killall "{}"'.format(self.pname))

    def build_paths_2(self, session):
        storage_filepaths = [
            os.path.join(self.get_subdir(session), x)
            for x in os.listdir(self.get_subdir(session))
        ]
        dest_filepaths = [
            os.path.join(FINDER_STATE_DIR, x)
            for x in os.listdir(self.get_subdir(session))
        ]
        return zip(storage_filepaths, dest_filepaths)
