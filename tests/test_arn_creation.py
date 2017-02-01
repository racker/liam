import unittest

from botocore.stub import Stubber, ANY
import moto

from liam import arn
from liam.utils import setup_boto3_session


class TestArnCreation(unittest.TestCase):

    @moto.mock_sts
    def setUp(self):
        self.creds = {
            'aws_access_key_id': 'test_key_id',
            'aws_secret_access_key': 'test_secret_key'
        }
        self.region_name = 'us-east-1'
        self.session = setup_boto3_session(self.creds, region_name=self.region_name)

    @moto.mock_elb
    @moto.mock_sts
    def test_elb(self):
        name = 'test_lb'
        expected_arn = 'arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/test_lb'
        session = setup_boto3_session(self.creds, region_name=self.region_name)
        c = session.client('elb')
        c.create_load_balancer(
            LoadBalancerName=name,
            Listeners=[
               {
                   'Protocol': 'tcp',
                   'LoadBalancerPort': 123,
                   'InstancePort': 123,
               },
            ],
        )

        r = session.resource('elb', region_name='us-east-1')
        elbs = []
        for item in r.load_balancers.all():
            elbs.append(item)

        self.assertEquals(1, len(elbs))
        for elb in elbs:
            generated_arn = arn.Arn(session, elb).arn
            self.assertEquals(expected_arn, generated_arn)

    @moto.mock_sts
    def test_elbv2(self):
        expected_arn = 'arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188'
        response = {
            'LoadBalancers': [
                {
                    'LoadBalancerArn': expected_arn,
                },
            ],
        }
        expected_params = {u'LoadBalancerArns': ANY}

        r = self.session.resource('elbv2', region_name='us-east-1')
        stubber = Stubber(r.meta.client)
        stubber.add_response('describe_load_balancers', response, {})
        stubber.add_response('describe_load_balancers', response,
                             expected_params)
        stubber.activate()
        for elb in r.load_balancers.all():
            generated_arn = arn.Arn(self.session, elb).arn
            self.assertEquals(expected_arn, generated_arn)

    def test_sns(self):
        pass

