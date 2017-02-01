from __future__ import print_function
import unittest

from liam.arn import ArnParser
from liam.exception import InvalidArn


class TestArnParsing(unittest.TestCase):

    def test_normal_arn(self):
        arn = 'arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/test_lb'
        arn_parser = ArnParser(arn)
        self.assertEquals(arn_parser.scheme, 'arn')
        self.assertEquals(arn_parser.partition, 'aws')
        self.assertEquals(arn_parser.service, 'elasticloadbalancing')
        self.assertEquals(arn_parser.region, 'us-east-1')
        self.assertEquals(arn_parser.account, '123456789012')
        self.assertEquals(arn_parser.resource, 'loadbalancer/test_lb')

    def test_normal_arnt(self):
        arn = 'arnt:aws:cloudwatch:us-east-1:123456789012:metric:AWS/SNS:test'
        arn_parser = ArnParser(arn)
        self.assertEquals(arn_parser.scheme, 'arnt')
        self.assertEquals(arn_parser.partition, 'aws')
        self.assertEquals(arn_parser.service, 'cloudwatch')
        self.assertEquals(arn_parser.region, 'us-east-1')
        self.assertEquals(arn_parser.account, '123456789012')
        self.assertEquals(arn_parser.resource, 'metric:AWS/SNS:test')

    def test_global_service(self):
        arn = 'arn:aws:iam::123456789012:user/Test'
        arn_parser = ArnParser(arn)
        self.assertEquals(arn_parser.scheme, 'arn')
        self.assertEquals(arn_parser.partition, 'aws')
        self.assertEquals(arn_parser.service, 'iam')
        self.assertEquals(arn_parser.region, '')
        self.assertEquals(arn_parser.account, '123456789012')
        self.assertEquals(arn_parser.resource, 'user/Test')

    def test_blank_string(self):
        arn = ''
        with self.assertRaisesRegexp(InvalidArn, "Provided arn is incomplete"):
            ArnParser(arn)

    def test_bogus_arn(self):
        arn = 'test:arn'
        with self.assertRaisesRegexp(InvalidArn, "Provided arn is incomplete"):
            ArnParser(arn)

    def test_non_string(self):
        arn = {}
        with self.assertRaisesRegexp(InvalidArn, "Provided arn not a string"):
            ArnParser(arn)

    def test_none(self):
        arn = None
        with self.assertRaisesRegexp(InvalidArn, "Provided arn not a string"):
            ArnParser(arn)
