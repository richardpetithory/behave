# Generated by Django 3.1.4 on 2020-12-05 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0005_removalaction_permanent_ban'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='removedpost',
            name='flair_text_set',
        ),
        migrations.AddField(
            model_name='removedpost',
            name='removal_action',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='reddit.removalaction'),
        ),
    ]