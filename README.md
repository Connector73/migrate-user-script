# migrate-user-script
Script to migrate user data between AzureAD - MXvirtual - Provisioning server

# Requirements
* Python 3.6<br>
* Azure CLI (2.0.46 or up)

# Usage
## From Azure AD to MXvirtual
Description: Get user information from Azure AD and export to .csv file.<br>
Script: `azure_to_mxv.py`<br>
Output: .csv file ready to import to Mxvirtual<br>
Usage: `python azure_to_mxv.py`<br>

At start script will open browser with login screen to Azure portal. Login with user that has access to read user information in active directory.<br>
**Important:** Script automatically generates Passwords and PINs for mx users. Extension and ID numbers are assigned starting from 100. Use tools like Excel to change Password, PIN, Extension or ID number if needed afterwards.

## From MXvirtual to Azure AD
Description: Read from mxvirtual exported .csv file and create users in Azure AD<br>
Script: `mxv_to_azure.py`<br>
Output: Created users list.<br>
Usage: `python mxv_to_azure.py --mxv-file FILE`<br>
Arguments:
* Required
    * `--mxv-file` : Path to user list file exported from MXvirtual
* Optional
    * `-h` : Display help message
    
At start script will open browser with login screen to Azure portal. Login with user that has access to add users in active directory.<br>
**Important**: **Username** in Azure AD is taken from e-mail column in csv file. Domain name in e-mail must be registered and verified in Azure AD. Else creation of user will fail.<br>

## From MXvirtual to Provisioning server
Description: Read from mxvirtual exported .csv file and create users in Provisioning server<br>
Script: `mxv_to_provisioning.py`<br>
Output: Userlist with passwords for C73 app.<br>
Usage: `python mxv_to_provisioning.py --mxv-file FILE --group GROUP --admin-host example.com --tenant XXX-XXX-XXX --admin-name NAME --admin-pass PASS --no-ssl`<br>
Arguments:
* Required
    * `--mxv-file` : Path to user list file exported from MXvirtual
    * `--group` : Group name for provisioning. Refer to Provisioning server readme. [update link](https://github.com/Connector73/provisioning/blob/master/README.md)
    * `--admin-host` : Provisioning server administrator API host address. Example - admin.example.com, localhost:8000 etc.
* Optional
    * `--tenant` : Tenant ID of Azure AD. Reuired for Azure AD  user authentication.
    * `--admin-name` : Admin username for provisioning if configured
    * `--admin-pass` : Admin password for provisioning if configured
    * `--no-ssl` : If provided, connection is on unsecured HTTP. Default connection is HTTPS.
    * `-h` : Display help message

Variables:<br>
`admin_endpoint` if path to admin host URI is different, specify it here. Example: If `--admin-host` is `example.com`, but provisioning admin server serves on `example.com/admin`, then `admin_endpoint` will be `/admin`.<br><br>
**Important:** If mxvirtual csv file does not contain PAssword and PIN columns, then script will generate Passwords and PINs for mx users. Please add Password and PIN columns manually if dont want to generate new ones.

## From Provisioning server to MXvirtual
Description: Read data from provisioning server and output .csv file ready to import to MXvirtual.<br>
Script: `provisioning_mxv.py`<br>
Output: .csv file to be imported to MXvirtual.<br>
Usage: `python provisioning_mxv.py --admin-host <example.com> --admin-name NAME --admin-pass PASS --no-ssl`<br>
Arguments:
* Required
    * `--admin-host` : Provisioning server administrator API host address. Example - admin.example.com, localhost:8000 etc.
* Optional
    * `--admin-name` : Admin username for provisioning if configured
    * `--admin-pass` : Admin password for provisioning if configured
    * `--no-ssl` : If provided, connection is on unsecured HTTP. Default connection is HTTPS.
    * `-h` : Display help message

Variables:<br>
`admin_endpoint` if path to admin host URI is different, specify it here. Example: If `--admin-host` is `example.com`, but provisioning admin server serves on `example.com/admin`, then `admin_endpoint` will be `/admin`.<br><br>
**Important:** If Extension and ID are blank in provisioning server, you have to manually fill them afterwards. If not importing users to MXvirtual may be incorrect.
