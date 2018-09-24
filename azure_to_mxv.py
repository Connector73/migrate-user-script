import json
import csv
import secrets
import string

from subprocess import check_output, call

fieldnames = ("Azure AD Group","First Name","Last Name","Extension","Voice DID","Fax DID","Caller ID","ID for MS Exchange","Home Phone","Cell Phone",
                "Fax Number", "E-mail","Alternate E-mail","User Name","Password","PIN","Pseudonym","User Profile","ID","Admin Profile","Paging Profile",
                "Recording Profile", "Home MX","Current MX", "Default Role","Assigned Device(s)","CallGroup","AA")

password_length = 8
pin_length = 6

def generate_password (N):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(N))

def generate_pin (N):
    return ''.join(secrets.choice(string.digits) for _ in range(N))

def main():
    # ID and extension format, increments by one for every new user
    id_number = 100
    extension_number = 100

    # Login
    call(['az', 'login'])

    # Get Azure user list
    user_list_json = json.loads(check_output(['az', 'ad', 'user', 'list']).decode('utf-8'))

    # CSV output
    with open("csv_output.csv","w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()

        for user in user_list_json:
            extension_number += 1
            id_number += 1

            user_group_list = check_output(['az', 'ad', 'user', 'get-member-groups', '--upn-or-object-id', user['userPrincipalName'], '--query', '[].displayName']).decode('utf-8')
            
            # Formatting names
            user_name = user['givenName']
            user_surname = user['surname']

            if user_name is None and user_surname is None:
                if user['displayName'] is not None:
                    user_name, *middle_name, user_surname = user['displayName'].split()

            # Write to CSV file
            writer.writerow({"Azure AD Group" : user_group_list,
                                "First Name" : user_name,
                                "Last Name" : user_surname,
                                "Home Phone" : user['telephoneNumber'],
                                "Cell Phone" : user['mobile'],
                                "E-mail" : user['userPrincipalName'],
                                "User Name" : user['userPrincipalName'].split("@")[0],
                                "Password" : generate_password(password_length),
                                "PIN" : generate_pin(pin_length),
                                "Extension" : extension_number,
                                "ID" : id_number
                                })


if __name__ == '__main__':
    main()
