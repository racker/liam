from __future__ import print_function
import unittest

from liam.arn import ArnParser
from liam.exception import InvalidArn


class TestArnParsing(unittest.TestCase):

    def test_normal_arn(self):
        arn = 'arn:aws:sns:us-east-1:123456789012:my_corporate_topic:02034b43-fefa-4e07-a5eb-3be56f8c54ce'
        arn_parser = ArnParser(arn)
        self.assertEquals(arn_parser.scheme, 'arn')
        self.assertEquals(arn_parser.partition, 'aws')
        self.assertEquals(arn_parser.service, 'sns')
        self.assertEquals(arn_parser.region, 'us-east-1')
        self.assertEquals(arn_parser.account, '123456789012')
        self.assertEquals(arn_parser.resource, 'my_corporate_topic:02034b43-fefa-4e07-a5eb-3be56f8c54ce')
        self.assertEquals(arn_parser.boto_service_name, 'sns')

    def test_normal_arnt(self):
        arn = 'arnt:aws:cloudwatch:us-east-1:123456789012:metric:AWS/SNS:test'
        arn_parser = ArnParser(arn)
        self.assertEquals(arn_parser.scheme, 'arnt')
        self.assertEquals(arn_parser.partition, 'aws')
        self.assertEquals(arn_parser.service, 'cloudwatch')
        self.assertEquals(arn_parser.region, 'us-east-1')
        self.assertEquals(arn_parser.account, '123456789012')
        self.assertEquals(arn_parser.resource, 'metric:AWS/SNS:test')
        self.assertEquals(arn_parser.boto_service_name, 'cloudwatch')

    def test_global_service(self):
        arn = 'arn:aws:iam::123456789012:user/Test'
        arn_parser = ArnParser(arn)
        self.assertEquals(arn_parser.scheme, 'arn')
        self.assertEquals(arn_parser.partition, 'aws')
        self.assertEquals(arn_parser.service, 'iam')
        self.assertEquals(arn_parser.region, '')
        self.assertEquals(arn_parser.account, '123456789012')
        self.assertEquals(arn_parser.resource, 'user/Test')
        self.assertEquals(arn_parser.boto_service_name, 'iam')

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

    def test_elb(self):
        arn = 'arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/test_lb'
        arn_parser = ArnParser(arn)
        self.assertEquals(arn_parser.scheme, 'arn')
        self.assertEquals(arn_parser.partition, 'aws')
        self.assertEquals(arn_parser.service, 'elasticloadbalancing')
        self.assertEquals(arn_parser.region, 'us-east-1')
        self.assertEquals(arn_parser.account, '123456789012')
        self.assertEquals(arn_parser.resource, 'loadbalancer/test_lb')
        self.assertEquals(arn_parser.boto_service_name, 'elb')

    def test_elbv2(self):
        arn = 'arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188'
        arn_parser = ArnParser(arn)
        self.assertEquals(arn_parser.scheme, 'arn')
        self.assertEquals(arn_parser.partition, 'aws')
        self.assertEquals(arn_parser.service, 'elasticloadbalancing')
        self.assertEquals(arn_parser.region, 'us-east-1')
        self.assertEquals(arn_parser.account, '123456789012')
        self.assertEquals(arn_parser.resource, 'loadbalancer/app/my-load-balancer/50dc6c495c0c9188')
        self.assertEquals(arn_parser.boto_service_name, 'elbv2')