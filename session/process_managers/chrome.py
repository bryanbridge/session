import os

from session.process_managers.common import ProcessManager


HOME_DIR = os.path.expanduser('~')
CHROME_DIR = os.path.join(
    HOME_DIR, 'Library', 'Application Support', 'Google', 'Chrome')
RELATIVE_DIRS = (
    ['Default'] + [x for x in os.listdir(CHROME_DIR) if x[:8] == 'Profile '])
FILENAMES = ['Current Session', 'Current Tabs']
RELATIVE_PATHS = [
    os.path.join(relative_dir, filename)
    for relative_dir in
    RELATIVE_DIRS
    for filename in
    FILENAMES
]


class ChromeManager(ProcessManager):
    name = 'chrome'
    pname = 'Google Chrome'
    filepaths = [
        os.path.join(CHROME_DIR, relative_path)
        for relative_path in
        RELATIVE_PATHS
    ]
