import os
import time
import shutil
from subprocess import check_output
from ConfigParser import NoOptionError


class ProcessManager(object):
    name = None
    pname = None
    filepaths = []  # NOTE: Must never be accessed directly.

    def __init__(self, config):
        self.config = config

    def get_filepaths(self):
        return self.filepaths

    def save(self, session):
        self.clear_stored_files(session)

        try:
            copy_files(self.build_paths(session, mode='save'))
        except IOError:
            pass  # ...(new) session created, process never started

        self.config.set(
            session, '{}_running'.format(self.name), self.check_running())

    def load(self, session):
        if self.check_running():
            self.shutdown()

        try:
            copy_files(self.build_paths(session, mode='load'))
        except IOError:
            self.clear_state()  # ...session has no state for this process

        try:
            if self.config.getboolean(session, '{}_running'.format(self.name)):
                self.start()
        except NoOptionError:
            pass

    def reset(self):
        if self.check_running():
            self.shutdown()
        self.clear_state()

    def clear_state(self):
        for filepath in self.get_filepaths():
            try:
                os.remove(filepath)
            except OSError:
                pass

    def start(self):
        os.system('open -a "{}"'.format(self.pname))

    def shutdown(self):
        os.system('killall "{}"'.format(self.pname))
        while self.check_running():
            time.sleep(0.1)

    def get_process_count(self):
        # deprecated
        return int(check_output(
            'pgrep "{}" -x | wc -l'.format(self.pname), shell=True))

    def check_running(self):
        return int(check_output(
            'pgrep "^{}$" --exact | wc -l'.format(self.pname), shell=True
        )) > 0

    def build_paths(self, session, mode='save'):
        storage_filepaths = [
            os.path.join(
                self.get_subdir(session, mode=mode),
                os.path.relpath(
                    filepath,
                    os.path.commonprefix(
                        [os.path.dirname(x) for x in self.get_filepaths()]),
                )
            )
            for filepath in self.get_filepaths()
        ]

        if mode == 'save':
            return zip(self.get_filepaths(), storage_filepaths)
        elif mode == 'load':
            return zip(storage_filepaths, self.get_filepaths())
        else:
            raise ValueError

    def clear_stored_files(self, session):
        try:
            shutil.rmtree(self.get_subdir(session, mode='clear'))
        except IOError:
            pass

    def get_subdir(self, session, mode='save'):
        subdir = os.path.join(get_session_dir(self.config, session), self.name)

        if not os.path.isdir(subdir):
            if mode == 'save':
                os.mkdir(subdir)
            elif mode in ['load', 'clear']:
                raise IOError
            else:
                raise ValueError

        return subdir


def copy_files(paths):
    for src, dest in paths:
        dest_dir = os.path.dirname(dest)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        shutil.copy2(src, dest)


def get_session_dir(config, session):
    return os.path.join(config.get('.main', 'data_dir'), session)
