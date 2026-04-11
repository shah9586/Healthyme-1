from django.core.management.base import BaseCommand
from core.models import ProductIndex
import csv


class Command(BaseCommand):
    help = "Import Indian products dataset"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        count = 0
        skipped = 0

        with open(file_path, encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter='\t')

            for row in reader:
                try:
                    # ✅ CLEAN BARCODE
                    barcode = (row.get('code') or '').strip()

                    # ❌ Skip empty barcode
                    if not barcode:
                        skipped += 1
                        continue

                    # ❌ Skip very long/invalid barcode
                    if len(barcode) > 120:
                        skipped += 1
                        continue

                    # ✅ SAVE / UPDATE
                    ProductIndex.objects.update_or_create(
                        barcode=barcode,
                        defaults={
                            'name': row.get('product_name', ''),
                            'ingredients': row.get('ingredients_text', ''),
                            'categories': row.get('categories', ''),
                            'brands': row.get('brands', ''),
                            'countries': row.get('countries', '') or row.get('countries_en', ''),
                            'source': 'openfoodfacts',
                        }
                    )

                    count += 1

                    if count % 1000 == 0:
                        self.stdout.write(f"Imported {count} products...")

                except Exception as e:
                    skipped += 1
                    continue

        self.stdout.write(self.style.SUCCESS(
            f"✅ Done importing {count} products!"
        ))
        self.stdout.write(self.style.WARNING(
            f"⚠️ Skipped {skipped} invalid rows"
        ))