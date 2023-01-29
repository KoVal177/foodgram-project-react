import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')
FILE_TAGS = 'tags.csv'
FILE_INGREDIENTS = 'ingredients.csv'


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument(
            'datafiles', 
            default=[FILE_TAGS, FILE_INGREDIENTS], 
            nargs='?',
            type=list
        )

    def handle(self, *args, **kwargs):
        for file in kwargs['datafiles']:
            try:
                with open(
                    os.path.join(DATA_ROOT, file),
                    'r',
                    encoding='utf-8'
                ) as f:
                    data = csv.reader(f)
                    for row in data:
                        if file == FILE_TAGS:
                            name, color, slug = row
                            Tag.objects.get_or_create(
                                name=name,
                                color=color,
                                slug=slug,
                            )
                        elif file == FILE_INGREDIENTS:
                            name, measurement_unit = row
                            Ingredient.objects.get_or_create(
                                name=name,
                                measurement_unit=measurement_unit
                            )
                print(f'Data from {file} successfully uploaded to database')
            except FileNotFoundError:
                raise CommandError(f'Не найден файл {file} в папке data')
