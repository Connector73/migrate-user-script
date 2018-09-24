import json
import csv
import argparse
import http.client
import base64

fieldnames = ("TenantID","First Name","Last Name","Extension","Voice DID","Fax DID","Caller ID","ID for MS Exchange","Home Phone","Cell Phone","Fax Number",
                "E-mail","Alternate E-mail","User Name","Password","PIN","Pseudonym","User Profile","ID","Admin Profile","Paging Profile","Recording Profile","Home MX",
                "Current MX", "Default Role","Assigned Device(s)","CallGroup","AA")

admin_endpoint = ""

def conn_to_admin(ahost,no_ssl):
    if no_ssl:
        return http.client.HTTPConnection(ahost,timeout=5)
    else:
        return http.client.HTTPSConnection(ahost,timeout=5)


def main(ahost, admin_name=None, admin_pass=None, no_ssl=False):
    admin_conn = conn_to_admin(ahost,no_ssl)
    
    headers = {"Content-type": "application/json"}
    
    if admin_name is not None and admin_pass is not None:
        userAndPass = base64.b64encode(str.encode(admin_name) + b":" + str.encode(admin_pass)).decode("ascii")
        headers["Authorization"] = "Basic %s" %  userAndPass
    
    try:
        admin_conn.request("GET", admin_endpoint + "/users", headers=headers)
    except Exception as e:
        print("Connection error")
        print(e)
        exit(1)
    
    response = admin_conn.getresponse()
    
    if response.status != 200:
        print(response.status, response.reason)
        admin_conn.close()
        exit(2)
        
    user_list = json.loads(response.read())['users']
    
    with open("mxv_user_list.csv","w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()

        for user in user_list:
            try:
                admin_conn.request("GET", admin_endpoint + "/users/" + user, headers=headers)
            except Exception as e:
                print("Connection error")
                print(e)
                admin_conn.close()
                exit(1)

            response = admin_conn.getresponse()
            user_data = json.loads(response.read())
            mx = user_data['services']['MX']
            
            # Write to CSV file
            writer.writerow({"TenantID" : user_data['tenant'] if 'tenant' in user_data else None,
                            "First Name" : mx['first_name'],
                            "Last Name" : mx['last_name'],
                            "Cell Phone" : mx['mobile_number'],
                            "E-mail" : user,
                            "User Name" : mx['account_name'],
                            "Password" : mx['account_pwd'],
                            "PIN" : mx['account_pin'],
                            "Extension" : mx['extension'] if 'extension' in mx else None,
                            "ID" : mx['id'] if 'id' in mx else None
                            })
    
    admin_conn.close()
    exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--admin-name', dest='admin_name', help='Admin username for provisioning if configured', metavar='NAME')
    parser.add_argument('--admin-pass', dest='admin_pass', help='Admin password for provisioning if configured', metavar='PASS')
    parser.add_argument('--no-ssl', dest='no_ssl', action='store_true', help='If provided, connection is on unsecured HTTP. Default is False')
    requiredArg = parser.add_argument_group('required arguments')
    requiredArg.add_argument('--admin-host', dest='admin_host', help='Provisioning server administrator API host address', metavar='<example.com>', required=True)
    
    args = parser.parse_args()
    main(args.admin_host, args.admin_name, args.admin_pass, args.no_ssl)
