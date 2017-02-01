from __future__ import print_function
import liam

CREDS = {
    'aws_access_key_id': "FILL_ME_IN",
    'aws_secret_access_key': "FILL_ME_IN"
}


def example_1():
    # run a scan of ec2 subnets in us-east regions, returning arns
    scanner = liam.Scanner(
        CREDS,
        services=['ec2'],
        regions=['us-east-1', 'us-east-2'],
        collections=['subnets']
    )
    results = scanner.scan(return_arns=True)
    print(results)


def example_2():
    # run a full scan of everything
    scanner = liam.Scanner(CREDS)
    results = scanner.scan()
    print(results)


def main():
    example_1()


if __name__ == '__main__':
    main()
