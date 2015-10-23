# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import powerdns.utils
from django.conf import settings
import powerdns.models.requests
import powerdns.models.powerdns
import dj.choices.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0010_auto_20150921_0613'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', dj.choices.fields.ChoiceField(choices=powerdns.models.requests.RequestStates, default=1)),
                ('name', models.CharField(validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')], unique=True, verbose_name='name', max_length=255)),
                ('master', models.CharField(blank=True, null=True, verbose_name='master', max_length=128)),
                ('type', models.CharField(choices=[('MASTER', 'MASTER'), ('NATIVE', 'NATIVE'), ('SLAVE', 'SLAVE')], blank=True, null=True, verbose_name='type', max_length=6)),
                ('account', models.CharField(blank=True, null=True, verbose_name='account', max_length=40)),
                ('remarks', models.TextField(blank=True, verbose_name='Additional remarks')),
                ('record_auto_ptr', dj.choices.fields.ChoiceField(choices=powerdns.utils.AutoPtrOptions, default=2, help_text='Should A records have auto PTR by default')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RecordRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', dj.choices.fields.ChoiceField(choices=powerdns.models.requests.RequestStates, default=1)),
                ('name', models.CharField(null=True, verbose_name='name', max_length=255, blank=True, validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$')], help_text="Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!")),
                ('type', models.CharField(choices=[('A', 'A'), ('AAAA', 'AAAA'), ('AFSDB', 'AFSDB'), ('CERT', 'CERT'), ('CNAME', 'CNAME'), ('DNSKEY', 'DNSKEY'), ('DS', 'DS'), ('HINFO', 'HINFO'), ('KEY', 'KEY'), ('LOC', 'LOC'), ('MX', 'MX'), ('NAPTR', 'NAPTR'), ('NS', 'NS'), ('NSEC', 'NSEC'), ('PTR', 'PTR'), ('RP', 'RP'), ('RRSIG', 'RRSIG'), ('SOA', 'SOA'), ('SPF', 'SPF'), ('SRV', 'SRV'), ('SSHFP', 'SSHFP'), ('TXT', 'TXT')], null=True, verbose_name='type', max_length=6, blank=True, help_text='Record qtype')),
                ('content', models.CharField(blank=True, null=True, verbose_name='content', max_length=255, help_text="The 'right hand side' of a DNS record. For an A record, this is the IP address")),
                ('ttl', models.PositiveIntegerField(default=3600, blank=True, null=True, verbose_name='TTL', help_text='TTL in seconds')),
                ('prio', models.PositiveIntegerField(blank=True, null=True, verbose_name='priority', help_text='For MX records, this should be the priority of the mail exchanger specified')),
                ('ordername', models.CharField(blank=True, null=True, verbose_name='DNSSEC Order', max_length=255)),
                ('auth', models.NullBooleanField(default=True, verbose_name='authoritative', help_text='Should be set for data for which is itself authoritative, which includes the SOA record and our own NS records but not set for NS records which are used for delegation or any delegation related glue (A, AAAA) records')),
                ('disabled', models.BooleanField(default=False, verbose_name='Disabled', help_text='This record should not be used for actual DNS queries. Note - this field works for pdns >= 3.4.0')),
                ('remarks', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^(\\*\\.)?([_A-Za-z0-9-]+\\.)*([A-Za-z0-9])+$'), powerdns.models.powerdns.SubDomainValidator()], unique=True, verbose_name='name', max_length=255),
        ),
        migrations.AlterField(
            model_name='domain',
            name='record_auto_ptr',
            field=dj.choices.fields.ChoiceField(choices=powerdns.utils.AutoPtrOptions, default=2, help_text='Should A records have auto PTR by default'),
        ),
        migrations.AlterField(
            model_name='record',
            name='disabled',
            field=models.BooleanField(default=False, verbose_name='Disabled', help_text='This record should not be used for actual DNS queries. Note - this field works for pdns >= 3.4.0'),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='domain',
            field=models.ForeignKey(to='powerdns.Domain', help_text='The domain for which a record is to be added', related_name='record_requests'),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='owner',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='record',
            field=models.ForeignKey(null=True, to='powerdns.Record', help_text='The record for which a change is being requested', related_name='requests'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='domain',
            field=models.ForeignKey(null=True, to='powerdns.Domain', help_text='The domain for which a change is requested', related_name='requests'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='owner',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='parent_domain',
            field=models.ForeignKey(null=True, to='powerdns.Domain', help_text='The parent domain for which a new subdomain is to be created', related_name='child_requests'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='reverse_template',
            field=models.ForeignKey(null=True, verbose_name='Reverse template', to='powerdns.DomainTemplate', blank=True, help_text='A template that should be used for reverse domains when PTR templates are automatically created for A records in this template.', related_name='reverse_template_for_requests'),
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='template',
            field=models.ForeignKey(null=True, verbose_name='Template', to='powerdns.DomainTemplate', blank=True, related_name='template_for_requests'),
        ),
    ]
