# Generated manually to fix M2M field conversion

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_remove_trainingplan_exercises'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingPlanExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repetitions', models.PositiveIntegerField(default=10)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.exercise')),
                ('training_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.trainingplan')),
            ],
            options={
                'unique_together': {('training_plan', 'exercise')},
            },
        ),
    ] 