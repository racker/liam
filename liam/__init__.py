from __future__ import print_function
import logging

from botocore.exceptions import ClientError

from liam import utils

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)
logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)


class Scanner(object):

    def __init__(self, aws_creds, session=None, account_id=None, services=None,
                 regions=None, collections=None):
        self.session = session or utils.setup_boto3_session(aws_creds)
        self.account_id = account_id or self.get_account_id()
        self.services = services or self.get_available_resources()
        self.regions = regions
        self.collections = collections
        self.found_resources = []
        self.found_arns = []

    def _get_resources(self):
        resources = self.session.get_available_resources()
        return resources

    def _init_boto_resource(self, service_name, region_name):
        return self.session.resource(service_name, region_name)

    def _get_scan_regions(self, service_name):
        if self.regions:
            return self.regions
        regions = self.get_available_regions(service_name=service_name)

        # Removing local regions as it is out of liam's purview
        regions.remove("local")

        return regions

    def _get_scan_collections(self, resource):
        if self.collections:
            return self.collections
        return utils.get_available_collections(resource)

    def scan(self, return_arns=False):
        self.found_resources = []
        for service_name in self.services:
            for region_name in self._get_scan_regions(service_name):
                resource = self._init_boto_resource(service_name, region_name)
                for collection_name in self._get_scan_collections(resource):
                    LOG.debug(
                        "Scan of {service_name}:{region_name}:{collection_name}".format(  # noqa
                            service_name=service_name,
                            region_name=region_name,
                            collection_name=collection_name
                        )
                    )
                    collection_iterator = utils.get_collection_iterator(
                        collection_name,
                        resource,
                        service_name,
                        self.account_id
                    )
                    try:
                        for item in collection_iterator:
                            self.found_resources.append(item)
                            LOG.debug("Found {}".format(str(item)))
                    except ClientError as exc:
                        if 'is not supported in this region' in exc.message:
                            LOG.warning(
                                "{}:{} not supported in {}. Skipping".format(
                                    service_name, collection_name, region_name)
                            )
                        else:
                            raise
        if return_arns:
            return utils.generate_arns(self.session, self.found_resources,
                                       self.account_id)
        return self.found_resources

    def get_account_id(self):
        return self.session.client('sts').get_caller_identity().get('Account')

    def get_available_services(self):
        return self.session.get_available_services()

    def get_available_regions(self, service_name, **kwargs):
        return self.session.get_available_regions(service_name, **kwargs)

    def get_available_resources(self):
        return self.session.get_available_resources()
