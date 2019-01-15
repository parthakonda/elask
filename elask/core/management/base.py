import os
import sys
from argparse import ArgumentParser


class CommandParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent
    SystemExit in several occasions, as SystemExit is unacceptable when a
    command is called programmatically.
    """
    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        super(CommandParser, self).__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if (hasattr(self.cmd, 'missing_args_message') and
                not (args or any(not arg.startswith('-') for arg in args))):
            self.error(self.cmd.missing_args_message)
        return super(CommandParser, self).parse_args(args, namespace)

    def error(self, message):
        if self.cmd._called_from_command_line:
            super(CommandParser, self).error(message)
        else:
            raise CommandError("Error: %s" % message)

class BaseCommand(object):

    help = ''

    def get_version(self):
        """
        Return the Elask version, which should be correct for all built-in
        Elask commands. User-supplied commands can override this method to
        return their own version.
        """
        return '0.0.1'

    def create_parser(self, prog_name, subcommand):
        """
        To add default arguments
        """
        parser = CommandParser(
            self, prog="%s %s" % (os.path.basename(prog_name), subcommand),
            description=self.help or None,
        )
        parser.add_argument('--version', action='version', version=self.get_version())
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        Initial hook and executed from commandline
        """
        self._called_from_command_line = True
        try:
            option = argv[1]
        except:
            option = None
        parser = self.create_parser(argv[0], option)
        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())
        
        self.execute(*args, **cmd_options)

    def execute(self, *args, **options):
        """
        Invoked from run argv
        """
        self.handle(*args, **options)

    def handle(self, *args, **kwargs):
        """
        User should implement this method
        """
        raise(NotImplementedError, "Command not implemented")
