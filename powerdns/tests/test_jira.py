import json
import unittest

import responses

from django.conf import settings
from powerdns.models.powerdns import Domain, Record


class JiraCreateMock(responses.RequestsMock):
    """Prepare to receive create_issue request"""

    def __enter__(self):
        rsps = super().__enter__()
        rsps.add(
            url='http://jira.ourcompany.com/rest/api/2/issue',
            method='POST',
            status=201,
            content_type='application/json',
            body=(
                '{"id":"1","key":"DNS-1","self":'
                '"https://jira-sandbox.allegrogroup.com/'
                'rest/api/2/issue/1"}'
            ),
        )
        rsps.add(
            url='http://jira.ourcompany.com/rest/api/2/issue/DNS-1',
            method='GET',
            status=200,
            content_type='application/json',
            body=(
                '{"fields": {"id":"1","key":"DNS-1","self":'
                '"http://jira.ourcompany.com/'
                'rest/api/2/issue/1"}}'
            ),
        )
        return rsps


class TestJira(unittest.TestCase):

    def setUp(self):
        settings.ENABLE_JIRA_LOGGING = True

    def tearDown(self):
        settings.ENABLE_JIRA_LOGGING = False

    def assert_issue_created(
        self,
        rsps,
        summary_contains='',
        description_contains=''
    ):
        data = json.loads(rsps.calls[0].request.body)
        self.assertIn(description_contains, data['fields']['description'])
        self.assertIn(summary_contains, data['fields']['summary'])

    def test_create_domain(self):
        """Creating a domain causes change creation"""
        with JiraCreateMock() as rsps:
            self.domain = Domain.objects.create(name='example.com')
            self.assert_issue_created(
                rsps,
                description_contains='name|example.com'
            )
        with JiraCreateMock():
            self.domain.delete()

    def test_change_domain(self):
        """Editing a domain causes change creation"""
        with JiraCreateMock():
            self.domain = Domain.objects.create(name='example.com')

        with JiraCreateMock() as rsps:
            self.domain.name = 'example.net'
            self.domain.save()
            self.assert_issue_created(
                rsps,
                description_contains='name|example.com|example.net',
            )
        with JiraCreateMock():
            self.domain.delete()

    def test_delete_domain(self):
        """Deleting a domain causes change creation"""
        with JiraCreateMock():
            self.domain = Domain.objects.create(name='example.com')
        with JiraCreateMock() as rsps:
            self.domain.delete()
            self.assert_issue_created(
                rsps,
                summary_contains='example.com',
            )

    def test_create_record(self):
        """Creating a domain causes change creation"""
        with JiraCreateMock():
            self.domain = Domain.objects.create(name='example.com')

        with JiraCreateMock() as rsps:
            self.record = Record.objects.create(
                domain=self.domain,
                type='CNAME',
                name='site.example.com',
                content='www.example.com',
            )
            self.assert_issue_created(
                rsps,
                description_contains='name|site.example.com'
            )
        with JiraCreateMock():
            self.record.delete()
        with JiraCreateMock():
            self.domain.delete()

    def test_change_record(self):
        """Creating a domain causes change creation"""
        with JiraCreateMock():
            self.domain = Domain.objects.create(name='example.com')

        with JiraCreateMock():
            self.record = Record.objects.create(
                domain=self.domain,
                type='CNAME',
                name='site.example.com',
                content='www.example.com',
            )
        with JiraCreateMock() as rsps:
            self.record.name = 'blog.example.com'
            self.record.save()
            self.assert_issue_created(
                rsps,
                description_contains='name|site.example.com|blog.example.com'
            )
        with JiraCreateMock():
            self.record.delete()
        with JiraCreateMock():
            self.domain.delete()

    def test_delete_record(self):
        """Deleting a record causes change creation"""
        with JiraCreateMock():
            self.domain = Domain.objects.create(name='example.com')

        with JiraCreateMock():
            self.record = Record.objects.create(
                domain=self.domain,
                type='CNAME',
                name='site.example.com',
                content='www.example.com',
            )
        with JiraCreateMock() as rsps:
            self.record.delete()
            self.assert_issue_created(
                rsps,
                description_contains='site.example.com'
            )
        with JiraCreateMock():
            self.domain.delete()
