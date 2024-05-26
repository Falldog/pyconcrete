from django.core.management import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('msg', nargs='+', help='echo message')

    def handle(self, *args, **options):
        msg = ' '.join(options['msg'])
        print(msg)
