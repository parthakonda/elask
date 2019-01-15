import os
from elask.core.management.base import BaseCommand
from jinja2 import Environment, PackageLoader, select_autoescape

class Command(BaseCommand):

    help = ("""
    To create the project
    """)

    def add_arguments(self, parser):
        parser.add_argument('name', help='Name of the application or project.')

    def handle(self, *args, **options):
        if 'name' not in options and options['name'] != '':
            raise ValueError("Invalid project name")
        # 1. Make sure app/directory doesn't exists
        if os.path.exists(options['name']):
            raise ValueError("Project with %s already exists"%(options['name']))
        # 2. Create project template
        os.makedirs("{0}/settings".format(options['name']))
        # 3. Copy necessary templates
        env = Environment(
            loader=PackageLoader('elask', 'conf/templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        server_template = env.get_template('project/server.py.template')
        dev_template = env.get_template('project/dev.py.template')
        zappa_template = env.get_template('project/zappa_settings.json.template')        
        # 4. Write server.py
        srvr_file = open("{0}/server.py".format(options['name']), 'w')
        srvr_file.write(server_template.render())
        srvr_file.close()
        # 5. Write __init__, dev
        init_file = open("{0}/settings/__init__.py".format(options['name']), 'w')
        init_file.close()
        dev_file = open("{0}/settings/dev.py".format(options['name']), 'w')
        dev_file.write(dev_template.render())
        dev_file.close()
        # 6. Write zappa_settings
        zappa_file = open("{0}/zappa_settings.json".format(options['name']), 'w')
        init_file.close()

