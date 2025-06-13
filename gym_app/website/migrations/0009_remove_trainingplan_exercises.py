# Generated manually to fix M2M field conversion

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_rename_isexpert_trainingplan_is_expert'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainingplan',
            name='exercises',
        ),
    ] 