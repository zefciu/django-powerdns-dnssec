# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import powerdns.models.powerdns
from django.conf import settings
import powerdns.utils
import powerdns.models.requests
import dj.choices.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0010_auto_20150921_0613'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('state', dj.choices.fields.ChoiceField(choices=powerdns.models.requests.RequestStates, default=1)),
                ('name', models.CharField(max_length=255, verbose_name='name', validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')])),
                ('master', models.CharField(max_length=128, verbose_name='master', null=True, blank=True)),
                ('type', models.CharField(choices=[('MASTER', 'MASTER'), ('NATIVE', 'NATIVE'), ('SLAVE', 'SLAVE')], max_length=6, verbose_name='type', null=True, blank=True)),
                ('account', models.CharField(max_length=40, verbose_name='account', null=True, blank=True)),
                ('remarks', models.TextField(verbose_name='Additional remarks', blank=True)),
                ('record_auto_ptr', dj.choices.fields.ChoiceField(help_text='Should A records have auto PTR by default', choices=powerdns.utils.AutoPtrOptions, default=2)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecordRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('state', dj.choices.fields.ChoiceField(choices=powerdns.models.requests.RequestStates, default=1)),
                ('name', models.CharField(help_text="Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!", verbose_name='name', null=True, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')], max_length=255, blank=True)),
                ('type', models.CharField(help_text='Record qtype', max_length=6, verbose_name='type', null=True, choices=[('A', 'A'), ('AAAA', 'AAAA'), ('AFSDB', 'AFSDB'), ('CERT', 'CERT'), ('CNAME', 'CNAME'), ('DNSKEY', 'DNSKEY'), ('DS', 'DS'), ('HINFO', 'HINFO'), ('KEY', 'KEY'), ('LOC', 'LOC'), ('MX', 'MX'), ('NAPTR', 'NAPTR'), ('NS', 'NS'), ('NSEC', 'NSEC'), ('PTR', 'PTR'), ('RP', 'RP'), ('RRSIG', 'RRSIG'), ('SOA', 'SOA'), ('SPF', 'SPF'), ('SRV', 'SRV'), ('SSHFP', 'SSHFP'), ('TXT', 'TXT')], blank=True)),
                ('content', models.CharField(help_text="The 'right hand side' of a DNS record. For an A record, this is the IP address", max_length=255, verbose_name='content', null=True, blank=True)),
                ('ttl', models.PositiveIntegerField(help_text='TTL in seconds', verbose_name='TTL', null=True, blank=True, default=3600)),
                ('prio', models.PositiveIntegerField(help_text='For MX records, this should be the priority of the mail exchanger specified', verbose_name='priority', null=True, blank=True)),
                ('ordername', models.CharField(max_length=255, verbose_name='DNSSEC Order', null=True, blank=True)),
                ('auth', models.NullBooleanField(help_text='Should be set for data for which is itself authoritative, which includes the SOA record and our own NS records but not set for NS records which are used for delegation or any delegation related glue (A, AAAA) records', verbose_name='authoritative', default=True)),
                ('disabled', models.BooleanField(help_text='This record should not be used for actual DNS queries. Note - this field works for pdns >= 3.4.0', verbose_name='Disabled', default=False)),
                ('remarks', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(max_length=255, verbose_name='name', unique=True, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()]),
        ),
        migrations.AlterField(
            model_name='domain',
            name='record_auto_ptr',
            field=dj.choices.fields.ChoiceField(help_text='Should A records have auto PTR by default', choices=powerdns.utils.AutoPtrOptions, default=2),
        ),
        migrations.AlterField(
            model_name='record',
            name='disabled',
            field=models.BooleanField(help_text='This record should not be used for actual DNS queries. Note - this field works for pdns >= 3.4.0', verbose_name='Disabled', default=False),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='domain',
            field=models.ForeignKey(help_text='The domain for which a record is to be added', related_name='record_requests', to='powerdns.Domain'),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='record',
            field=models.ForeignKey(help_text='The record for which a change is being requested', related_name='requests', null=True, to='powerdns.Record'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='domain',
            field=models.ForeignKey(help_text='The domain for which a change is requested', related_name='requests', null=True, blank=True, to='powerdns.Domain'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='parent_domain',
            field=models.ForeignKey(help_text='The parent domain for which a new subdomain is to be created', related_name='child_requests', null=True, blank=True, to='powerdns.Domain'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='reverse_template',
            field=models.ForeignKey(help_text='A template that should be used for reverse domains when PTR templates are automatically created for A records in this template.', related_name='reverse_template_for_requests', verbose_name='Reverse template', null=True, to='powerdns.DomainTemplate', blank=True),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='template',
            field=models.ForeignKey(related_name='template_for_requests', verbose_name='Template', null=True, to='powerdns.DomainTemplate', blank=True),
        ),
    ]
