# Generated by Django 4.2.20 on 2025-05-29 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_execution', '0013_remove_answer_question_remove_answer_session_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='question_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
