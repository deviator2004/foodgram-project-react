import csv
import os
from django.conf import settings

from recipes import models


path = os.path.join(settings.CSV_FILES_DIR, 'ingredients.csv')

with open(path) as f:
    reader = csv.reader(f)
    for row in reader:
        _, created = models.Ingredients.objects.get_or_create(
            name=row[0],
            measurement_unit=row[1],
        )
