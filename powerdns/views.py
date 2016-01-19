"""Views and viewsets for DNSaaS API"""

from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from powerdns.models import (
    CryptoKey,
    DeleteRequest,
    Domain,
    DomainMetadata,
    DomainTemplate,
    DomainRequest,
    Record,
    RecordTemplate,
    RecordRequest,
    SuperMaster,
)
from rest_framework.filters import DjangoFilterBackend, SearchFilter
from rest_framework.viewsets import ModelViewSet

from powerdns.serializers import (
    CryptoKeySerializer,
    DomainMetadataSerializer,
    DomainSerializer,
    DomainTemplateSerializer,
    RecordSerializer,
    RecordTemplateSerializer,
    SuperMasterSerializer,
)
from powerdns.utils import VERSION


class FiltersMixin(object):

    filter_backends = (DjangoFilterBackend,)


class OwnerViewSet(FiltersMixin, ModelViewSet):
    """Base view for objects with owner"""

    def perform_create(self, serializer, *args, **kwargs):
        if serializer.validated_data.get('owner') is None:
            serializer.save(owner=self.request.user)
        else:
            object_ = serializer.save()
            object_.email_owner(self.request.user)


class DomainViewSet(OwnerViewSet):

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    filter_fields = ('name', 'type')


class RecordViewSet(OwnerViewSet):

    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filter_fields = ('name', 'type', 'content', 'domain')
    search_fields = ('name', 'type', 'content')


class CryptoKeyViewSet(FiltersMixin, ModelViewSet):

    queryset = CryptoKey.objects.all()
    serializer_class = CryptoKeySerializer
    filter_fields = ('domain',)


class DomainMetadataViewSet(FiltersMixin, ModelViewSet):

    queryset = DomainMetadata.objects.all()
    serializer_class = DomainMetadataSerializer
    filter_fields = ('domain',)


class SuperMasterViewSet(FiltersMixin, ModelViewSet):

    queryset = SuperMaster.objects.all()
    serializer_class = SuperMasterSerializer
    filter_fields = ('ip', 'nameserver')


class DomainTemplateViewSet(FiltersMixin, ModelViewSet):

    queryset = DomainTemplate.objects.all()
    serializer_class = DomainTemplateSerializer
    filter_fields = ('name',)


class RecordTemplateViewSet(FiltersMixin, ModelViewSet):

    queryset = RecordTemplate.objects.all()
    serializer_class = RecordTemplateSerializer
    filter_fields = ('domain_template', 'name', 'content')


class HomeView(TemplateView):

    """Homepage. This page should point user to API or admin site. This package
    will provide some minimal homepage template. The administrators of
    DNSaaS solutions are encouraged however to create their own ones."""

    template_name = "powerdns/home.html"

    def get_context_data(self, **kwargs):

        return {
            'version': VERSION,
        }


def accept_request_factory(request_model, model_name=None):
    def result(request, pk):
        request = request_model.objects.get(pk=pk)
        domain = request.accept()
        if model_name:
            return redirect(
                reverse(
                    'admin:powerdns_{}_change'.format(model_name),
                    args=(domain.pk,)
                )
            )
        else:
            return redirect(reverse('admin:index'))
    return result

accept_domain_request = accept_request_factory(DomainRequest, 'domain')
accept_record_request = accept_request_factory(RecordRequest, 'record')
accept_delete_request = accept_request_factory(DeleteRequest)
