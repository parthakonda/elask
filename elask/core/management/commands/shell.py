from elask.core.management.base import BaseCommand
import sys

class Command(BaseCommand):

    def python(self):
        import code
        imported_objects = {}
        code.interact(local=imported_objects)

    def ipython(self):
        from IPython import start_ipython
        start_ipython(argv=[])

    def bpython(self, options):
        import bpython
        bpython.embed()

    def handle(self, *args, **options):
        # TODO: need to get read interface option and invoke accordingly
        self.python()
        