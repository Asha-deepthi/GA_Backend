# Generated by Django 4.2.20 on 2025-06-16 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('test_creation', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sectiontimer',
            name='session_id',
        ),
        migrations.AddField(
            model_name='sectiontimer',
            name='candidate_test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='timers', to='test_creation.candidate_test'),
        ),
    ]
