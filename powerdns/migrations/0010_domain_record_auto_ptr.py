# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dj.choices.fields
import powerdns.utils


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0009_auto_20150915_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='record_auto_ptr',
            field=dj.choices.fields.ChoiceField(default=2, choices=powerdns.utils.AutoPtrOptions),
        ),
    ]
