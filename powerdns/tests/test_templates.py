"""Tests for the template system"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.test import TestCase

from powerdns.models.powerdns import Domain, Record, DomainMetadata
from powerdns.tests.utils import (
    DomainTemplateFactory,
    RecordTemplateFactory,
    DomainMetadataTemplateFactory,
    assert_does_exist,
    assert_not_exists,
)
from powerdns.utils import AutoPtrOptions


class TestTemplates(TestCase):
    """Test cases for a simple template"""

    def setUp(self):
        self.reverse_template = DomainTemplateFactory(name='reverse')
        self.domain_template1 = DomainTemplateFactory(name='template1')
        self.t1_soa_record = RecordTemplateFactory(
            type='SOA',
            name='{domain-name}',
            content=(
                'ns1.{domain-name} hostmaster.{domain-name} '
                '0 43200 600 1209600 600'
            ),
            domain_template=self.domain_template1,
        )
        self.t1_ns_record = RecordTemplateFactory(
            type='NS',
            name='{domain-name}',
            content=(
                'ns1.{domain-name}'
            ),
            domain_template=self.domain_template1,
        )
        self.t1_a_record = RecordTemplateFactory(
            type='A',
            name='www.{domain-name}',
            content=(
                '192.168.1.3'
            ),
            domain_template=self.domain_template1,
            auto_ptr=AutoPtrOptions.ALWAYS,
        )
        self.t1_metadata = DomainMetadataTemplateFactory(
            kind='TSIG-ALLOW-AXFR',
            content='tsig-1',
            domain_template=self.domain_template1,
        )
        self.domain_template2 = DomainTemplateFactory(name='template2')
        RecordTemplateFactory(
            type='SOA',
            name='{domain-name}',
            content=(
                'nameserver1.{domain-name} hostmaster.{domain-name} '
                '0 43200 1200 1209600 1200'
            ),
            domain_template=self.domain_template2,
        )
        RecordTemplateFactory(
            type='NS',
            name='{domain-name}',
            content=(
                'nameserver1.{domain-name}'
            ),
            domain_template=self.domain_template2,
        )
        RecordTemplateFactory(
            type='NS',
            name='{domain-name}',
            content=(
                'nameserver2.{domain-name}'
            ),
            domain_template=self.domain_template2,
        )
        DomainMetadataTemplateFactory(
            kind='TSIG-ALLOW-AXFR',
            content='tsig-2',
            domain_template=self.domain_template2,
        )

    def test_record_creation(self):
        """Records are created when template is used to create a domain"""
        domain = Domain(
            name='example.com',
            template=self.domain_template1,
            reverse_template=self.domain_template2,
        )
        domain.save()
        self.assertEqual(domain.record_set.count(), 3)
        self.assertSetEqual(
            set(r.content for r in domain.record_set.all()),
            {
                'ns1.example.com hostmaster.example.com '
                '0 43200 600 1209600 600',
                'ns1.example.com',
                '192.168.1.3'
            }
        )
        assert_does_exist(Record, type='PTR', name='3.1.168.192.in-addr.arpa')
        assert_does_exist(DomainMetadata, domain=domain, content='tsig-1')

    def test_template_change(self):
        """Records are changed when template on existing domain is changed"""
        domain = Domain(
            name='example.com',
            template=self.domain_template1,
            reverse_template=self.domain_template2,
        )
        domain.save()
        domain.template = self.domain_template2
        domain.save()
        self.assertEqual(domain.record_set.count(), 3)
        self.assertSetEqual(
            set(r.content for r in domain.record_set.all()),
            {
                'nameserver1.example.com hostmaster.example.com '
                '0 43200 1200 1209600 1200',
                'nameserver1.example.com',
                'nameserver2.example.com',
            }
        )
        assert_not_exists(DomainMetadata, domain=domain, content='tsig-1')
        assert_does_exist(DomainMetadata, domain=domain, content='tsig-2')

    def test_template_modify(self):
        """Record is changed when its template is modified"""
        domain = Domain(name='example.com', template=self.domain_template1)
        domain.save()
        self.t1_ns_record.content = 'nsrv1.{domain-name}'
        self.t1_ns_record.save()
        record = Record.objects.get(type='NS', domain=domain)
        self.assertEqual(record.content, 'nsrv1.example.com')

    def test_metadata_template_modify(self):
        """Metadata is changed when its template is modified"""
        domain = Domain(name='example.com', template=self.domain_template1)
        domain.save()
        self.t1_metadata.content = 'tsig-x'
        self.t1_metadata.save()
        assert_not_exists(DomainMetadata, domain=domain, content='tsig-1')
        assert_does_exist(DomainMetadata, domain=domain, content='tsig-x')

    def test_template_delete(self):
        """Records are deleted if corresponding template is deleted"""
        # This is managed by django's default ForeignKey.on_delete
        # so doesn't need implementation, but let's test it anyways:
        domain = Domain(
            name='example.com',
            template=self.domain_template1,
            reverse_template=self.domain_template2,
        )
        domain.save()
        assert_does_exist(
            Record,
            domain=domain,
            content='192.168.1.3'
        )
        assert_does_exist(
            Record,
            name='3.1.168.192.in-addr.arpa',
            type='PTR'
        )
        self.t1_a_record.delete()
        self.assertEqual(domain.record_set.count(), 2)
        assert_not_exists(
            Record,
            domain=domain,
            content='192.168.1.3'
        )
        assert_not_exists(
            Record,
            name='3.1.168.192.in-addr.arpa',
            type='PTR'
        )

    def test_template_add(self):
        """Records are added if the domain template gets a new record
        template"""
        domain = Domain(name='example.com', template=self.domain_template1)
        domain.save()
        self.t1_ns2_record = RecordTemplateFactory(
            type='NS',
            name='{domain-name}',
            content=(
                'ns2.{domain-name}'
            ),
            domain_template=self.domain_template1,
        )
        self.assertEqual(domain.record_set.count(), 4)
        assert_does_exist(Record, domain=domain, content='ns2.example.com')
