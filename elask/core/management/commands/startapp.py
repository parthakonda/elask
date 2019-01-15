import os
from elask.core.management.base import BaseCommand
from jinja2 import Environment, PackageLoader, select_autoescape

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('name', help='Name of the application or project.')

    def handle(self, *args, **options):
        if 'name' not in options and options['name'] != '':
            raise ValueError("Invalid project name")
        # 1. Make sure app/directory doesn't exists
        if os.path.exists(options['name']):
            raise ValueError("Project with %s already exists"%(options['name']))
        # 2. Create project template
        os.makedirs("{0}".format(options['name']))
        # 3. Copy necessary templates
        env = Environment(
            loader=PackageLoader('elask', 'conf/templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        model_template = 'models.py', env.get_template('app/models.py.template')
        routes_template = 'routes.py', env.get_template('app/routes.py.template')
        serializer_template = 'serializers.py', env.get_template('app/serializers.py.template')
        viewset_template = 'viewsets.py', env.get_template('app/viewsets.py.template')
        # 4. Write server.py
        for file_name, evry_template in [model_template, routes_template, serializer_template, viewset_template]:
            file_instance = open("{0}/{1}".format(options['name'], file_name), 'w')
            file_instance.write(evry_template.render())
            file_instance.close()
        # 5. Write __init__
        init_file = open("{0}/__init__.py".format(options['name']), 'w')
        init_file.close()
