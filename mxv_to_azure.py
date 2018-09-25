import csv
import json
import string
import secrets
import argparse

from subprocess import check_output, call


fieldnames = ("TenantID","First Name","Last Name","Extension","Voice DID","Fax DID","Caller ID","ID for MS Exchange","Home Phone","Cell Phone","Fax Number",
                "E-mail","Alternate E-mail","User Name","Password","PIN","Pseudonym","User Profile","ID","Admin Profile","Paging Profile","Recording Profile","Home MX",
                "Current MX", "Default Role","Assigned Device(s)","CallGroup","AA")

def azure_password():
    password = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(1))
    password += ''.join(secrets.choice(string.ascii_lowercase) for _ in range(3))
    password += ''.join(secrets.choice(string.digits) for _ in range(4))
    return password

  
def main(mxv_csv):
    # Login
    call(['az', 'login', '--allow-no-subscription'])

    with open(mxv_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile,fieldnames)
        next(reader)

        for row in reader:
            try:
                result = check_output(['az', 'ad', 'user', 'create', '--display-name', ' '.join([row['First Name'],row['Last Name']]),
                                '--password', azure_password(),'--force-change-password-next-login', 'true', '--user-principal-name', row['E-mail']]).decode('utf-8')
                print('Created:', json.loads(result)['userPrincipalName'])
            except Exception as e:
                print(e)

    exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    requiredArg = parser.add_argument_group('required arguments')
    requiredArg.add_argument('--mxv-file', dest='mxvfile', help='MXvirtual exported user list file', metavar='FILE', required=True)
    
    args = parser.parse_args()
    main(args.mxvfile)
