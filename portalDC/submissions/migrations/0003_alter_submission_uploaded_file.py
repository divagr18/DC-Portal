# Generated by Django 5.2 on 2025-04-08 14:16

import submissions.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0002_alter_submission_uploaded_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='uploaded_file',
            field=models.FileField(upload_to=submissions.models.submission_upload_path),
        ),
    ]
