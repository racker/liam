from string import Formatter
from boto3.exceptions import ResourceLoadException


def _parse_components(arn):
    return arn.split(':', 5)


class ARN(object):

    def __init__(self, arn):
        self.arn = arn
        self.components = _parse_components(self.arn)

    @property
    def partition(self):
        return self.components[1]

    @property
    def service(self):
        return self.components[2]

    @property
    def region(self):
        return self.components[3]

    @property
    def account(self):
        return self.components[4]

    @property
    def resource(self):
        return self.components[5]


class Arn(object):
    def __init__(self, session, boto_resource, account_id=None):
        self.session = session
        self.boto_resource = boto_resource
        self.account_id = account_id

    @property
    def arn(self):
        return self.get_arn()

    def _get_partition(self):
        return self.boto_resource.meta.client.meta.partition

    def _get_service(self):
        return self.boto_resource.meta.service_name

    def _get_region(self):
        # this might require some additional logic to deal with global regions
        return self.boto_resource.meta.client.meta.region_name

    def _get_account(self):
        # TODO: inject this into our session directly so we dont need to call
        if not self.account_id:
            self.accoun_id = self.session.client(
                'sts').get_caller_identity()['Account']
        return self.account_id

    def _get_generic(self, key):
        return getattr(self.boto_resource, key)

    def _format_arn(self, format_string):
        required_keys = [
                k[1]
                for k in Formatter().parse(format_string)
                if k[1]
            ]
        mapping = {}
        for key in required_keys:
            if key == 'partition':
                mapping['partition'] = self._get_partition()
            elif key == 'service':
                mapping['service'] = self._get_service()
            elif key == 'region':
                mapping['region'] = self._get_region()
            elif key == 'account-id':
                mapping['account-id'] = self._get_account()
            else:
                mapping[key] = self._get_generic(key)
        return format_string.format(**mapping)

    def _get_data_path(self, data_path):
        if self.boto_resource.meta.data is None:
            if hasattr(self.boto_resource, 'load'):
                self.boto_resource.load()
            else:
                raise ResourceLoadException(
                    '{0} has no load method'.format(
                        self.boto_resource.__class__.__name__))

        data = self.boto_resource.meta.data
        for key in data_path:
            data = data[key]  # TODO: Error handling
        return data

    def _get_arn_config(self):
        loader = self.session._loader
        api_version = None  # This forces the latest version
        service_name = self.boto_resource.meta.service_name
        resource_name = self.boto_resource.meta.resource_model.name
        arn_model = loader.load_service_model(service_name,
                                              'arns-1',
                                              api_version)
        resources = arn_model.get('resources', {}).get(resource_name, {})
        config = resources.get('arn', {})
        return config

    def get_arn(self):
        arn_config = self._get_arn_config()
        data_path = arn_config.get('dataPath', False)
        format_string = arn_config.get('formatString', False)

        if data_path:
            # If the Arn already exists as part of the response lets use that
            arn = self._get_data_path(data_path)
        elif format_string:
            # When if doubt Try to format it out
            arn = self._format_arn(format_string)
        else:
            # Don't go chasing waterfarns
            raise NotImplementedError()
        return arn
