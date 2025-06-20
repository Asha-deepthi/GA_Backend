# Generated by Django 5.2.1 on 2025-06-16 07:27

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate_Test',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique ID for the test invitation link.', primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('SENT', 'Sent'), ('STARTED', 'Started'), ('COMPLETED', 'Completed')], default='PENDING', max_length=20)),
                ('score', models.FloatField(blank=True, null=True)),
                ('date_invited', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('weightage', models.CharField(blank=True, max_length=50)),
                ('is_correct', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('text', models.TextField(help_text='The prompt or question text')),
                ('allow_multiple', models.BooleanField(default=False, help_text='For MCQ, allow multiple correct answers')),
                ('paragraph_content', models.TextField(blank=True, null=True)),
                ('fib_answer', models.CharField(blank=True, max_length=255, null=True)),
                ('video_time', models.PositiveIntegerField(default=60, help_text='Max seconds for video')),
                ('audio_time', models.PositiveIntegerField(default=60, help_text='Max seconds for audio')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(help_text='e.g., mcq, fib, audio, video, paragraph', max_length=100)),
                ('time_limit', models.CharField(blank=True, default=30, help_text='e.g., 00:00:00', max_length=20)),
                ('num_questions', models.PositiveIntegerField(blank=True, null=True)),
                ('marks_per_question', models.FloatField(blank=True, null=True)),
                ('max_marks', models.FloatField(blank=True, null=True)),
                ('min_marks', models.FloatField(blank=True, null=True)),
                ('negative_marks', models.FloatField(blank=True, null=True)),
                ('shuffle_questions', models.BooleanField(default=False)),
                ('shuffle_answers', models.BooleanField(default=False)),
                ('instructions', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SectionTimer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_id', models.IntegerField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('remaining_time', models.IntegerField()),
                ('session_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('level', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('duration', models.PositiveIntegerField(blank=True, help_text='Total duration in minutes', null=True)),
                ('tags', models.CharField(blank=True, max_length=255)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('passing_percentage', models.PositiveIntegerField(blank=True, null=True)),
                ('scoring_type', models.CharField(default='per_question', max_length=50)),
                ('negative_marking_type', models.CharField(default='no_negative_marking', max_length=50)),
                ('allow_back_navigation', models.BooleanField(default=False)),
                ('results_display_type', models.CharField(default='immediately', max_length=50)),
                ('attempts_type', models.CharField(default='unlimited', max_length=50)),
                ('number_of_attempts', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
    ]
