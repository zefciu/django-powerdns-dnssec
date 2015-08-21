"""Utilities for powerdns models"""

from pkg_resources import working_set, Requirement

from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dj.choices import Choices


VERSION = working_set.find(Requirement.parse('django-powerdns-dnssec')).version

try:
    from jira import JIRA
    JIRA_SERVER = JIRA(
        settings.JIRA_URL,
        basic_auth=(settings.JIRA_USERNAME, settings.JIRA_PASSWORD),
        get_server_info=False,
    )
except (ImportError, AttributeError):
    JIRA_SERVER = None


JIRA_MISCONFIGURATION_MSG = """To enable JIRA support you need to install jira
package and provide JIRA_URL"""
import rules


@rules.predicate
def is_owner(user, object_):
    return not object_ or object_.owner == user


class TimeTrackable(models.Model):
    created = models.DateTimeField(
        verbose_name=_("date created"), auto_now=False, auto_now_add=True,
        editable=False,
    )
    modified = models.DateTimeField(
        verbose_name=_('last modified'), auto_now=True, editable=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_values = {
            k: v for k, v in self.__dict__.items() if not k.startswith('_')
        }

    class Meta:
        abstract = True


class Owned(models.Model):
    """Model that has an owner. This owner is set as default to the creator
    of this model, but can be overridden."""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    class Meta:
        abstract = True

    def email_owner(self, creator):
        """If the owner is different from the creator - notify the owner."""
        if (
            creator != self.owner and
            settings.ENABLE_OWNER_NOTIFICATIONS and
            hasattr(self.owner, 'email')
        ):
            subject_template, content_template = settings.OWNER_NOTIFICATIONS[
                type(self)._meta.object_name
            ]
            kwargs = {}
            for key, user in [
                ('owner', self.owner),
                ('creator', creator),
            ]:
                kwargs[key + '-email'] = user.email
                kwargs[key + '-name'] = '{} {}'.format(
                    user.first_name,
                    user.last_name
                )
            kwargs['object'] = str(self)

            subject = subject_template.format(**kwargs)
            content = content_template.format(**kwargs)
            send_mail(
                subject,
                content,
                settings.FROM_EMAIL,
                [self.owner.email],
            )


class UserBasedValidator():
    """Generic validator which logic depends on the current user"""

    def set_context(self, field):
        self.user = field.parent.context['request'].user


class PermissionValidator(UserBasedValidator):
    """A validator that only allows objects that user has permission for"""

    def __init__(self, permission, *args, **kwargs):
        self.permission = permission
        super().__init__(*args, **kwargs)

    def __call__(self, object_):
        if not self.user.has_perm(self.permission, object_):
            raise ValidationError("You don't have permission to use this")
        return object_


def to_reverse(ip):
    """
    Given an ip address it will return a tuple of (domain, number)
    suitable for PTR record
    """
    *domain_parts, number = ip.split('.')
    domain = '{}.in-addr.arpa'.format('.'.join(reversed(domain_parts)))
    return (domain, number)


class AutoPtrOptions(Choices):
    _ = Choices.Choice
    NEVER = _("Never")
    ALWAYS = _("Always")
    ONLY_IF_DOMAIN = _("Only if domain exists")


DOMAIN_TYPE = (
    ('MASTER', 'MASTER'),
    ('NATIVE', 'NATIVE'),
    ('SLAVE', 'SLAVE'),
)


def format_recursive(template, arguments):
    """
    Performs str.format on the template in a recursive fashion iterating over
    lists and dictionary values

    >>> template = {
    ... 'a': 'Value {a}',
    ... 'b': {
    ...     'a': 'Value {a}',
    ...     'b': 'Value {b}',
    ... },
    ... 'c': ['Value {a}', 'Value {b}'],
    ... 'd': 10,
    ... }
    >>> arguments = {
    ... 'a': 'A',
    ... 'b': 'B',
    ... }
    >>> result = format_recursive(template, arguments)
    >>> result['a']
    'Value A'
    >>> result['b']['b']
    'Value B'
    >>> result['c'][0]
    'Value A'
    >>> result['d']
    10
    """
    if isinstance(template, str):
        return template.format(**arguments)
    elif isinstance(template, dict):
        return {
            k: format_recursive(v, arguments)
            for (k, v) in template.items()
        }
    elif isinstance(template, list):
        return [format_recursive(v, arguments) for v in template]
    else:
        return template


def log_save_to_jira(sender, instance, created, **kwargs):
    if not settings.ENABLE_JIRA_LOGGING:
        return
    if not JIRA:
        raise ImproperlyConfigured(JIRA_MISCONFIGURATION_MSG)
    changes_list = ([
        '||Field||Value||' if created else '||Field||Previous||Current||'
    ])
    if created:
        for (k, v) in instance.__dict__.items():
            if k.startswith('_'):
                continue
            changes_list.append('|{}|{}|'.format(k, v))
    else:
        for (k, v) in instance._initial_values.items():
            if v != getattr(instance, k):
                changes_list.append(
                    '|{}|{}|{}|'.format(k, v, getattr(instance, k))
                )
    template_args = {
        'changes': '\n'.join(changes_list),
        'name': instance.name,
    }
    template_name = 'created' if created else 'modified'
    template = settings.JIRA_TEMPLATES[sender._meta.object_name][template_name]
    JIRA_SERVER.create_issue(fields=format_recursive(template, template_args))


def log_delete_to_jira(sender, instance, **kwargs):
    if not settings.ENABLE_JIRA_LOGGING:
        return
    if not JIRA:
        raise ImproperlyConfigured(JIRA_MISCONFIGURATION_MSG)
    template_args = {
        'name': instance.name,
    }
    template = settings.JIRA_TEMPLATES[sender._meta.object_name]['deleted']
    JIRA_SERVER.create_issue(fields=format_recursive(template, template_args))
