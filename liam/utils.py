import os

import boto3
import botocore.session

from liam.arn import Arn


def get_available_collections(resource):
    collections = [
        collection.name
        for collection
        in resource.meta.resource_model.collections
    ]
    return collections


def get_available_regions(service_name, partition_name='aws',
                          allow_non_regional=False):
    regions = setup_boto3_session({}).get_available_regions(
        service_name,
        partition_name=partition_name,
        allow_non_regional=allow_non_regional
    )
    # In the case of global services we want the region to be an empty string
    if not regions:
        regions = ['']
    return regions


def get_available_resources():
    return setup_boto3_session({}).get_available_resources()


def setup_boto3_session(creds, region_name=None):
    """Gets a boto session with the liam resources inserted"""
    boto_core_session = botocore.session.get_session()
    loader = boto_core_session.get_component('data_loader')

    # Because we are overwriting some botocore paginators we need our files to
    # load first. Append will work fine once changes are merged upstream
    loader.search_paths.insert(
        0, os.path.join(os.path.dirname(__file__), 'data')
    )
    session = boto3.Session(botocore_session=boto_core_session,
                            region_name=region_name, **creds)
    return session


def get_cm_iterator(collection_name, boto_resource, service_name, account_id,
                    filter_by_owner=True):
    # TODO: This is ugly and just fixes edge cases for now. This needs cleaning
    collection_manager = init_collection_manager(
        boto_resource, collection_name)
    if not filter_by_owner:
        return collection_manager.all()

    if service_name == 'ec2' and collection_name == 'images':
        iterator = collection_manager.filter(Owners=['self'])
    elif service_name == 'ec2' and collection_name == 'snapshots':
        iterator = collection_manager.filter(
            OwnerIds=[account_id])
    else:
        iterator = collection_manager.all()
    return iterator


def generate_arn(session, boto_resource, account_id):
    arn = Arn(session, boto_resource, account_id=account_id)
    generated_arn = arn.get_arn()
    return generated_arn


def generate_arns(session, boto_objects, account_id):
    arns = []
    for obj in boto_objects:
        arns.append(generate_arn(session, obj, account_id))
    return arns


def init_collection_manager(boto_resource, collection_name):
    return getattr(boto_resource, collection_name)
