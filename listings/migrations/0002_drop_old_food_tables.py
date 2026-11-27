from django.db import migrations


class Migration(migrations.Migration):
    """Remove leftovers of the old `food` app, which this project replaced.

    The `food_item` table still had a foreign key to users, so deleting a user
    who had posted a food item failed with "FOREIGN KEY constraint failed".
    """

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                'DROP TABLE IF EXISTS food_item',
                "DELETE FROM django_migrations WHERE app = 'food'",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
