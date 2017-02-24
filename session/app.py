import sys
import os
import shutil
from ConfigParser import ConfigParser

import termcolor

from session.process_managers.chrome import ChromeManager
from session.process_managers.atom import AtomManager
from session.process_managers.finder import FinderManager


USAGE = """  Usage:
\tsession            :: give current state info
\tsession <label>    :: store current state, switch to existing state
\tsession -n <label> :: store current state, switch to new empty state
\tsession -c <label> :: store current state, switch to copied state (new label)
\tsession -d <label> :: delete session with this label
\tsession -l         :: list all stored sessions
\tsession -q         :: store current state and exit to normal use
\tsession -h         :: print usage
"""


ARGUMENT_COUNT = len(sys.argv) - 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DIR_CONFIG_PATH = os.path.join(SCRIPT_DIR, 'dir.ini')
CURRENT_CONFIG_FILENAME = '.config.ini'
STATE_STR_FMT = '  Current session:\n      {}\n  `$session -h` for help'
NO_STATE_STR = '  {}\n  `$session -h` for help.'.format(
    termcolor.colored('Not currently in a session...', 'yellow'))
NO_SESSION_STR_FMT = '  No such session {}'  # necessary..?
PROCESS_MANAGERS = [FinderManager, ChromeManager, AtomManager]


def run():
    ensure_data_setup()
    config = get_current_config()

    if ARGUMENT_COUNT == 0:
        print_state(config)

    elif ARGUMENT_COUNT == 1:
        if sys.argv[1][0] == '-':
            option = sys.argv[1]

            if option == '-l':
                list_sessions(config)
            elif option == '-q':
                if get_current_session(config) not in [None, '.default']:
                    switch_to_session(config, '.default')
                else:
                    print termcolor.colored(
                        '  Not currently in a session...', 'yellow')
            elif option == '-h':
                print_usage()
            else:
                print_usage_err('Bad option')

        else:
            session = sys.argv[1]
            switch_to_session(config, session)

    elif ARGUMENT_COUNT == 2:
        option = sys.argv[1]
        session = sys.argv[2]
        if not check_valid_session(session):
            print_usage_err('Invalid session label.')
            return

        if option == '-n':
            create_session(config, session, how='reset')
        elif option == '-c':
            create_session(config, session, how='copy')
        elif option == '-d':
            delete_session(config, session)
        else:
            print_usage_err('Bad option.')

    else:
        print_usage_err('Too many arguments.')

    save_current_config(config)


def switch_to_session(config, session):
    if not check_session_exists(config, session) and session != '.default':
        print '  Session with label {} does not exist!'.format(session)
        return

    save_current_session(config)

    set_current_session(config, session)
    load(config, session)


def create_session(config, session, how='reset'):
    if check_session_exists(config, session):
        print '  Session already exists with label {}'.format(session)
        return

    save_current_session(config)

    make_session_dir(session)
    config.add_section(session)
    set_current_session(config, session)

    if how == 'reset':
        reset(config)
    elif how == 'copy':
        pass
    else:
        raise ValueError


def delete_session(config, session):
    if get_current_session(config) == session:
        print '  Can\'t delete current session!'
        return

    if not check_session_exists(config, session):
        print NO_SESSION_STR_FMT.format(session)
        return

    # Remove directory for this session and its contents
    shutil.rmtree(os.path.join(get_data_dir(), session))

    # Also remove empty enclosing dirs related to this session label...
    prefix_dirs = [
        os.path.join(get_data_dir(), session.split('/' + x)[0])
        for x in session.split('/')[:0:-1]]
    for prefix_dir in prefix_dirs:
        if check_dir_empty(prefix_dir):
            shutil.rmtree(prefix_dir)

    config.remove_section(session)


def check_dir_empty(dir_):
    return os.listdir(dir_) in [[], ['.DS_Store']]


def save_current_session(config):
    current_session = get_current_session(config)
    if not current_session:
        current_session = '.default'

    for p in PROCESS_MANAGERS:
        p(config).save(current_session)


def load(config, session):
    for p in PROCESS_MANAGERS:
        p(config).load(session)


def reset(config):
    for p in PROCESS_MANAGERS:
        p(config).reset()


def make_session_dir(session):
    os.makedirs(os.path.join(get_data_dir(), session))


def check_session_exists(config, session):
    return session in config.sections()


def check_valid_session(session):
    if session[0] in ['-', '.']:
        return False
    if session[-1] in ['/']:
        return False
    return True


def print_usage_err(explanation):
    print explanation
    print_usage()


def print_usage():
    print USAGE


def print_state(config):
    current_session = get_current_session(config)
    if current_session and current_session != '.default':
        print STATE_STR_FMT.format(termcolor.colored(current_session, 'cyan'))
    else:
        print NO_STATE_STR


def set_current_session(config, session):
    config.set('.main', 'current_session', session)


def get_current_session(config):
    if 'current_session' in config.options('.main'):
        return config.get('.main', 'current_session')
    else:
        return None


def list_sessions(config):
    current_session = get_current_session(config)

    for session in get_session_list(config):
        color = 'cyan' if session == current_session else 'white'
        print termcolor.colored('  {}'.format(session), color)


def get_session_list(config):
    return [
        x for x in config.sections() if x not in ['.main', '.default']]


def save_current_config(config):
    with open(get_current_config_path(), 'wb') as config_file:
        config.write(config_file)


def get_current_config():
    return get_config(os.path.join(get_data_dir(), CURRENT_CONFIG_FILENAME))


def ensure_data_setup():
    data_dir = get_data_dir()
    current_config_path = get_current_config_path()
    default_dir = get_default_dir()

    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    if not os.path.isdir(default_dir):
        os.mkdir(default_dir)

    if not os.path.exists(current_config_path):
        with open(current_config_path, 'a') as f:
            f.write(
                '[.main]\ndata_dir: {}\n\n[.default]'.format(data_dir))


def get_current_config_path():
    return os.path.join(get_data_dir(), CURRENT_CONFIG_FILENAME)


def get_default_dir():
    return os.path.join(get_data_dir(), '.default')


def get_data_dir():
    return get_dir_config().get('.main', 'data_dir')


def get_dir_config():
    return get_config(DIR_CONFIG_PATH)


def get_config(path):
    config = ConfigParser()
    config.read(path)
    return config
