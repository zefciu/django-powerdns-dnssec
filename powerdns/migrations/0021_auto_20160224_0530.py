# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0020_remove_recordrequest_target_ordername'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainMetadataTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('kind', models.CharField(max_length=15, verbose_name='kind')),
                ('content', models.TextField(null=True, blank=True, verbose_name='content')),
                ('domain_template', models.ForeignKey(to='powerdns.DomainTemplate', verbose_name='Domain template')),
            ],
        ),
        migrations.AddField(
            model_name='domainmetadata',
            name='template',
            field=models.ForeignKey(blank=True, null=True, verbose_name='Template', to='powerdns.DomainMetadataTemplate'),
        ),
    ]
