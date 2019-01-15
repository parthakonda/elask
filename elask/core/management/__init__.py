
import os
import os
import pkgutil
import sys
from collections import OrderedDict, defaultdict
from importlib import import_module


def find_commands(management_dir):
    """
    Given a path to a management directory, returns a list of all the command
    names that are available.

    Returns an empty list if no commands are defined.
    """
    command_dir = os.path.join(management_dir, 'commands')
    commands = [name for ins, name, is_pkg in pkgutil.iter_modules([command_dir])
            if not is_pkg and not name.startswith('_')]
    return commands


def load_command_class(app_name, name):
    """
    Given a command name and an application name, returns the Command
    class instance. All errors raised by the import process
    (ImportError, AttributeError) are allowed to propagate.
    """
    module = import_module('%s.management.commands.%s' % (app_name, name))
    return module.Command()


def get_commands():
    """
    Try to get all avaialble commands from elask.core 
    and also from installed apps
    """
    commands = {name: 'elask.core' for name in find_commands(__path__[0])}
    try:
        settings = import_module('settings.dev') # TODO: Need to get from env    
        for app in settings.INSTALLED_APPS:
            commands.update({
                name: app for name in find_commands("%s/management"%app)
            })
    except Exception as e:
        # handled as general exception
        pass
    return commands


class ManagementUtility(object):

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])

    def fetch_command(self, subcommand):
        kommands = get_commands()
        app_name = kommands[subcommand]
        klass = load_command_class(
            app_name, subcommand
        )
        return klass

    def execute(self):
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'  # Display help if no arguments were given.
        if subcommand == 'help':
            print("Please provide valid options")
        try:
            subcommand = self.argv[1]
            self.fetch_command(subcommand).run_from_argv(self.argv[1:])
        except Exception as e:
            print("Invalid Command")
            print(e)
            sys.exit()
        
def execute_from_command_line(argv=None):
    management = ManagementUtility(argv)
    management.execute()
