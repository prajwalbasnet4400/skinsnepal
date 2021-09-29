from django.core.management.base import BaseCommand
from csgo.models import Item

class Command(BaseCommand):
    help = 'Updates the CSGO skins database'

    def handle(self, *args, **kwargs):
        update = Item.get_update()
        self.stdout.write("%s item added" % update)