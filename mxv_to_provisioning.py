import csv
import json
import argparse
import secrets
import string
import http.client
import base64

mxv_csv_file = "/path/to/csv_output.csv"
c73_user_list = "/path/to/save/c73_user_list.csv"

fieldnames = ("First Name","Last Name","Extension","Voice DID","Fax DID","Caller ID","ID for MS Exchange","Home Phone","Cell Phone","Fax Number",
                "E-mail","Alternate E-mail","User Name","Password","PIN","Pseudonym","User Profile","ID","Admin Profile","Paging Profile","Recording Profile","Home MX",
                "Current MX", "Default Role","Assigned Device(s)","CallGroup","AA")

admin_endpoint = ""

def get_pin(user):
    if 'PIN' not in user or user['PIN'] == '':
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    else:
        return user['PIN']


def get_password(user):
    if 'Password' not in user or user['Password'] == '':
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    else:
        return user['Password']


def get_outgoing_number(user):
    if user['Voice DID'] != '':
        return user['Voice DID']
    if user['Caller ID'] != '':
        return user['Caller ID']
    if user['Home Phone'] != '':
        return user['Home Phone']
    if user['Cell Phone'] != '':
        return user['Cell Phone']
    return None


def c73_password():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))


def body_json(user, group, tenantId):
    mx = {
        "account_name" : user['User Name'],
        "account_pin" : get_pin(user),
        "account_pwd" : get_password(user),
        "first_name" : user['First Name'],
        "last_name" : user['Last Name'],
        "mobile_number" : user['Cell Phone'],
        "outgoing_number" : get_outgoing_number(user),
        "extension" : user['Extension'],
        "id" : user['ID']
        }
    services = {"MX" : mx}

    body = {
        "group" : group,
        "tenant" : tenantId,
        "password" : c73_password(),
        "name" : user['First Name'] + ' ' + user['Last Name'],
        "services" : services
        }

    return body


def conn_to_admin(ahost,no_ssl):
    if no_ssl:
        return http.client.HTTPConnection(ahost,timeout=5)
    else:
        return http.client.HTTPSConnection(ahost,timeout=5)

def main(group, ahost, tenantId=None, admin_name=None, admin_pass=None, no_ssl=False):
    admin_conn = conn_to_admin(ahost,no_ssl)

    with open(mxv_csv_file, 'r') as csvfile:
        with open(c73_user_list, 'w') as c73_csv:
            writer = csv.DictWriter(c73_csv, fieldnames=('C73 Username','C73 Password'), dialect='excel')
            writer.writeheader()

            read_fields = csv.reader(csvfile)
            actual_fieldnames = next(read_fields, None)
            reader = csv.DictReader(csvfile,actual_fieldnames)
            
            headers = {"Content-type": "application/json"}
            if admin_name is not None and admin_pass is not None:
                userAndPass = base64.b64encode(str.encode(admin_name) + b":" + str.encode(admin_pass)).decode("ascii")
                headers["Authorization"] = "Basic %s" %  userAndPass

            for row in reader:
                body = body_json(row, group, tenantId)
                
                try:
                    admin_conn.request("PUT", admin_endpoint + "/users/" + row['E-mail'], body=json.dumps(body), headers=headers)
                except Exception as e:
                    print("Connection error")
                    print(e)
                    exit(1)
                
                response = admin_conn.getresponse()
                if response.status == 204:
                    print('Successfully addded user:', row['E-mail'])
                else:
                    print(response.status, response.reason)
                admin_conn.close()

                writer.writerow({"C73 Username" : row['E-mail'],
                                "C73 Password" : body['password'],
                                })
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tenant', dest='tenant', help='Tenant ID of Azure AD', metavar='XXX-XXX-XXX')
    parser.add_argument('--admin-name', dest='admin_name', help='Admin username for provisioning if configured', metavar='NAME')
    parser.add_argument('--admin-pass', dest='admin_pass', help='Admin password for provisioning if configured', metavar='PASS')
    parser.add_argument('--no-ssl', dest='no_ssl', action='store_true', help='If provided, connection is on unsecured HTTP. Default is False')
    requiredArg = parser.add_argument_group('required arguments')
    requiredArg.add_argument('--group', dest='group', help='Group name for provision', metavar='GROUP', required=True)
    requiredArg.add_argument('--admin-host', dest='admin_host', help='Provisioning server administrator API host address', metavar='<example.com>', required=True)
    
    args = parser.parse_args()
    main(args.group, args.admin_host, args.tenant, args.admin_name, args.admin_pass, args.no_ssl)
