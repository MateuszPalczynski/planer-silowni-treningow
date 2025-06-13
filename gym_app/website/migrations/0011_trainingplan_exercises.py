# Generated manually to fix M2M field conversion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_trainingplanexercise'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingplan',
            name='exercises',
            field=models.ManyToManyField(
                related_name='plans', 
                through='website.TrainingPlanExercise', 
                to='website.exercise'
            ),
        ),
    ] 