JIRA integration
-------------------------

If you want to trace changes done to domains and records with JIRA, you need
additional configuration.

Install ``django-powerdns-dnssec`` with ``jira`` extra::

    # pip install django-powerdns-dnssec[jira]

The necessary configuration is:

``ENABLE_JIRA_LOGGING``
    set to True
``JIRA_URL``
    URL of your JIRA instance
``JIRA_USERNAME``, ``JIRA_PASSWORD``
    credentials
``JIRA_TEMPLATES``
    a mapping describing how your JIRA tickets should look like. They should be
    in a form:::

    JIRA_TEMPLATES = {
        'Domain': {
            'created': template,
            'modified': template,
            'deleted': template,
        },
        'Record': {
            'created': template,
            'modified': template,
            'deleted': template,
        },
    }

The templates should be mappings accepted by JIRA API. They can use the
following fields:

``name``
    The name of domain/record
``changes``
    The table containing changes or initial values

An example template can look like this::

    {
        'project': {'key': 'DNS'},
        'issuetype': {'name': 'Change'},
        'summary': 'Domain {name} created',
        'description': '{changes}',
    }
