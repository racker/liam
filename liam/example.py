import liam

creds = {
    'aws_access_key_id': "FILL_ME_IN",
    'aws_secret_access_key': "FILL_ME_IN"
}


def main():
    scanner = liam.Scanner(creds)
    results = scanner.full_scan()
    print results


if __name__ == '__main__':
    main()
