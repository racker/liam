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
