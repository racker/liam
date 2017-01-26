from __future__ import print_function
import os


import boto3
from botocore.exceptions import ClientError
import botocore.session


def setup_boto3_session(creds):
    """Gets a boto session with the liam resources inserted"""
    boto_core_session = botocore.session.get_session()
    loader = boto_core_session.get_component('data_loader')

    # Because we are overwriting some botocore paginators we need our files to
    # load first. Append will work fine once changes are merged upstream
    loader.search_paths.insert(
        0, os.path.join(os.path.dirname(__file__), 'data')
    )
    session = boto3.Session(botocore_session=boto_core_session, **creds)
    return session


class Scanner(object):

    def __init__(self, creds, session=None):
        if not session:
            self.session = setup_boto3_session(creds)
            self.account_id = self.get_account_id()

    def full_scan(self):
        resources = self.session.get_available_resources()
        found = {}
        for resource_name in resources:
            found[resource_name] = {}
            for region_name in self.session.get_available_regions(
                    resource_name):

                resource = Resource(
                    service_name=resource_name,
                    region_name=region_name,
                    account_id=self.account_id,
                    session=self.session
                )
                found_items = resource.scan()
                found[resource_name][region_name] = found_items
            print(found)
        return found

    def get_account_id(self):
        return self.session.client('sts').get_caller_identity().get('Account')

    def get_available_services(self):
        return self.session.get_available_services()

    def get_available_regions(self, service_name, **kwargs):
        return self.session.get_available_regions(service_name, **kwargs)

    def get_available_resources(self):
        return self.session.get_available_resources()


class Resource(object):
    def __init__(self, service_name, region_name, account_id, session):
        self.service_name = service_name
        self.region_name = region_name
        self.account_id = account_id
        self.session = session
        self.boto_resource = self._init_boto_resource()

    def _init_boto_resource(self):
        return self.session.resource(self.service_name, self.region_name)

    def get_available_collections(self):
        return self.boto_resource.meta.resource_model.collections

    def scan(self):
        found = []
        for boto_collection in self.get_available_collections():
            col_obj = Collection(
                service_name=self.service_name,
                region_name=self.region_name,
                account_id=self.account_id,
                collection_name=boto_collection.name,
                session=self.session
            )
            found_items = col_obj.scan()
            found.extend(found_items)
        return found


class Collection(object):
    def __init__(self, service_name, region_name, account_id, collection_name,
                 session):

        self.service_name = service_name
        self.region_name = region_name
        self.collection_name = collection_name
        self.account_id = account_id
        self.session = session
        self.boto_resource = self._init_boto_resource()
        self.collection_manager = self._init_collection_manager()

    def _init_collection_manager(self):
        return getattr(self.boto_resource, self.collection_name)

    def _init_boto_resource(self):
        return self.session.resource(self.service_name, self.region_name)

    def get_iterator(self, filter_by_owner=True):
        if not filter_by_owner:
            return self.collection_manager.all()

        if self.service_name == 'ec2' and self.collection_name == 'images':
            iterator = self.collection_manager.filter(Owners=['self'])
        elif (self.service_name == 'ec2' and
              self.collection_name == 'snapshots'):
            iterator = self.collection_manager.filter(
                OwnerIds=[self.account_id])
        else:
            iterator = self.collection_manager.all()
        return iterator

    def scan(self):
        print("Gathering {}/{}/{}".format(self.service_name, self.region_name,
                                          self.collection_name))

        found_resources = []
        try:
            for item in self.get_iterator(self.collection_manager):
                found_resources.append(item)
        except ClientError as exc:
            if 'is not supported in this region' in exc.message:
                pass
            else:
                raise
        if found_resources:
            print(found_resources)
        return found_resources
