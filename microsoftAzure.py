from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network.v2020_06_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2020_06_01.models import SecurityRule
import azure.mgmt.compute
import base64
 
resource_client = get_client_from_cli_profile(ResourceManagementClient)

RESOURCE_GROUP_NAME = "Labo1_CLD"
print(RESOURCE_GROUP_NAME)
LOCATION = "westeurope"

# Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
    {
        "location": LOCATION
    }
)

# Obtain the management object for virtual machines
compute_client = get_client_from_cli_profile(ComputeManagementClient)

#provision a virtual network

VNET_NAME = "lab1-vnet"
SUBNET_NAME = "lab1-subnet"
IP_CONFIG_NAME = "lab1-ip-config"

# Obtain the management object for networks
network_client = get_client_from_cli_profile(NetworkManagementClient)

# Provision the virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {
            "address_prefixes": ["10.0.0.0/16"]
        }
    }
)

vnet_result = poller.result()

print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

#Provision the subnet and wait for completion
poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
    VNET_NAME, SUBNET_NAME,
    { "address_prefix": "10.0.0.0/24" }
)
subnet_result = poller.result()

print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")


#Provision an IP address and wait for completion

IP_NAME_DB = "db-ip"
NIC_DB_NAME = "db-nic"
IP_NAME_BACKEND = "back-ip"
NIC_BACK_NAME = "back-nic"
IP_NAME_FRONTEND = "front-ip"
NIC_FRONT_NAME = "front-nic"

poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME_DB,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

ip_address_db_result = poller.result()

poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME_BACKEND,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

ip_address_back_result = poller.result()

poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
    IP_NAME_FRONTEND,
    {
        "location": LOCATION,
        "sku": { "name": "Standard" },
        "public_ip_allocation_method": "Static",
        "public_ip_address_version" : "IPV4"
    }
)

ip_address_front_result = poller.result()

print(f"Provisioned public IP address {ip_address_db_result.name} with address {ip_address_db_result.ip_address}")
print(f"Provisioned public IP address {ip_address_back_result.name} with address {ip_address_back_result.ip_address}")
print(f"Provisioned public IP address {ip_address_front_result.name} with address {ip_address_front_result.ip_address}")

#provision the security groups
#database
DB_nsg = NetworkSecurityGroup()
DB_nsg.location = LOCATION
DB_nsg.security_rules = [SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='Allow ssh access', source_port_range='*', destination_port_range='22', priority=1000, name='ssh'),
						SecurityRule(protocol='Tcp', source_address_prefix='10.0.0.0/24', destination_address_prefix='*', access='Allow', direction='Inbound', description='Allow database access from backend private network', source_port_range='*', destination_port_range='3306', priority=1010, name='DB_access')]
#backend
back_nsg = NetworkSecurityGroup()
back_nsg.location = LOCATION
back_nsg.security_rules = [SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='Allow ssh access', source_port_range='*', destination_port_range='22', priority=1000, name='ssh'),
							SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='', source_port_range='*', destination_port_range='5222', priority=1010, name='ejabberd_standard'),
							SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='', source_port_range='*', destination_port_range='5223', priority=1020, name='ejabberd_jabber'),
							SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='', source_port_range='*', destination_port_range='5269', priority=1030, name='ejabberd_server'),
							SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='', source_port_range='*', destination_port_range='5280', priority=1040, name='websocket_access'),
							SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='', source_port_range='*', destination_port_range='4369', priority=1050, name='ejabberd_empd')] 

#frontend
front_nsg = NetworkSecurityGroup()
front_nsg.location = LOCATION
front_nsg.security_rules = [SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='Allow ssh access', source_port_range='*', destination_port_range='22', priority=1000, name='ssh'),
							SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='', source_port_range='*', destination_port_range='80', priority=1010, name='http_access'),
							SecurityRule(protocol='Tcp', source_address_prefix='*', destination_address_prefix='*', access='Allow', direction='Inbound', description='', source_port_range='*', destination_port_range='443', priority=1020, name='https_access')]


DB_nsg_obj = network_client.network_security_groups.begin_create_or_update(RESOURCE_GROUP_NAME, "db-nsg", DB_nsg).result()
back_nsg_obj = network_client.network_security_groups.begin_create_or_update(RESOURCE_GROUP_NAME, "back-nsg", back_nsg).result()
front_nsg_obj = network_client.network_security_groups.begin_create_or_update(RESOURCE_GROUP_NAME, "front-nsg", front_nsg).result()


print(f"Provisioned network security group with name {DB_nsg_obj.name}")
print(f"Provisioned network security group with name {back_nsg_obj.name}")
print(f"Provisioned network security group with name {front_nsg_obj.name}")



#Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_DB_NAME, 
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_db_result.id }
        }],
        'network_security_group': {
            'id': DB_nsg_obj.id
        }
    }
)

nic_db_result = poller.result()
print(f"Provisioned nic with name {NIC_DB_NAME}")

poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_BACK_NAME, 
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_back_result.id }
        }],
        'network_security_group': {
            'id': back_nsg_obj.id
        }
    }
)

nic_back_result = poller.result()
print(f"Provisioned nic with name {NIC_BACK_NAME}")

poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
    NIC_FRONT_NAME, 
    {
        "location": LOCATION,
        "ip_configurations": [ {
            "name": IP_CONFIG_NAME,
            "subnet": { "id": subnet_result.id },
            "public_ip_address": {"id": ip_address_front_result.id }
        }],
        'network_security_group': {
            'id': front_nsg_obj.id
        }
    }
)

nic_front_result = poller.result()
print(f"Provisioned nic with name {NIC_FRONT_NAME}")


DB_PARAMETERS={
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "variables": {},
	"location": "westeurope",
	"type": "Microsoft.Compute/virtualMachines",
    "apiVersion": "2019-07-01",
    "name": "db-image-20201001160640",
	"storage_image_reference" :{
    "id" : "/subscriptions/5181e089-3771-4b0d-9e07-9c3a90b2b013/resourceGroups/labo1/providers/Microsoft.Compute/images/db-image-20201001160640"
  },
    "storageProfile": {
        "osDisk": {
			"createOption": "fromImage",
            "managedDisk": {
                "storageAccountType": "Standard_LRS"
            }
			
        },
        "imageReference": {
            "id": "/subscriptions/5181e089-3771-4b0d-9e07-9c3a90b2b013/resourceGroups/labo1/providers/Microsoft.Compute/images/db-image-20201001160640"
        }
    },
	"osProfile": {
                    "computerName": "database",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": True,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDHSlGDhOkyHsvf76GAaF+Mn0yF\r\nf1rb1Rcz1zVixVIUSbkKhqSzMlgKx5jbFIWCFzbeqFnjTi03Dn68h3Ds5CYOHoW5\r\nC4VbEwczWjt8qP0BbBGrDdouQHiL8kdzc6TYjlDUhR4PaIWt2HDaBhQh4u3WhKIp\r\nHp8aPvm52EQhBjfMOWwfu4I+QMSt8pqnwSVn1cUzFIwDhyG5rrkXevnZzeCzxhek\r\nQ+meMvCuw6xOM5CYkF8q6SaK9fMQXLGeftDtnQoY2qphvci+bhVDGIF1aHh0EHvb\r\ndsg604lrA2RW9Y6ywr+htaDF1KEtrb2cUKdw24HQK8Ew35uL8MuzV0zt+mWbqSDp\r\n9bIN0CuaBREvJedhKSez6I8KKSyBV8IzixIp4knLIEnlWJjVBiKQ3YeG4/1t/CQi\r\nr12gEWvii3OAArm2vAQb7+Jl9QO7WVQ3sle6+D5IUBBszYn5fPwYpnOYOxNnXPdN\r\nLnIr3vKzDNhgZaNJnbuhDOXArdTXlFEFjxjdgqU= generated-by-azure\r\n"
                                }
                            ]
                        }
                    }
                },
	"network_profile": {
		"network_interfaces": [{
			"id": nic_db_result.id,
        }]
    },
	"hardware_profile": {
		"vm_size": "Standard_B1s"
	},
    "hyperVGeneration": "V1"
            
}

#script to modify host ip in the ejabberd.yml file and to register a user to the app with the credentials admin:admin
back_custom_data = base64.b64encode(b"#!/bin/bash\nsudo sed -i '0,/^hosts:/{s/hosts:.*/hosts: [\"" + ip_address_back_result.ip_address.encode('utf-8') + b"\"]/}' /etc/ejabberd/ejabberd.yml && sudo ejabberdctl restart && sleep 5 && sudo ejabberdctl register admin " + ip_address_back_result.ip_address.encode('utf-8') + b" admin\n").decode('latin-1')

BACK_PARAMETERS={
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "variables": {},
	"location": "westeurope",
	"type": "Microsoft.Compute/virtualMachines",
    "apiVersion": "2019-07-01",
    "name": "back-image-20201001175822",
	"storage_image_reference" :{
    "id" : "/subscriptions/5181e089-3771-4b0d-9e07-9c3a90b2b013/resourceGroups/labo1/providers/Microsoft.Compute/images/back-image-20201001175822"
  },
    "storageProfile": {
        "osDisk": {
			"createOption": "fromImage",
            "managedDisk": {
                "storageAccountType": "Standard_LRS"
            }
			
        },
        "imageReference": {
            "id": "/subscriptions/5181e089-3771-4b0d-9e07-9c3a90b2b013/resourceGroups/labo1/providers/Microsoft.Compute/images/back-image-20201001175822"
        }
    },
	"osProfile": {
                    "computerName": "backend",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": True,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDKCy9uEYwhmrHTO0zMs3l522iC\r\niOkUzQIK/fvE3Kx6MsgcwI9Dvg8/TxjCjYz2Bx9pIXvy2iLkPWajiCuikVsKUHKq\r\npPcjyqnwLT1va/oIhUG3HUxR6dhqeT2cZ+R065lsmUWeHOCO8CmG5u7en/FSW3LY\r\nhpQumIi+HMVPke5ZmsoeArOsSpYpLM/BSea4A4EfOM2351hfzgJWUKWvBLSYBppT\r\ntoA0qWUbI4MIQushNnX05tQgBXg8Y7q621wQm5tVvpURPjIcfjg27Q9LN0X2UYdZ\r\nh6pyqFnBzlFvq00plqZ8pr/DB+w7tW4CUGVpsgwSStqPoC3N7n6eI86ffrrpY/KO\r\nMq5DKRSVakSGARER2il2oEaj045viTcrzmkp8cnSh+JmKMctHYnoWSMlcyI1a7F4\r\nCtv3Xpp047UKbwv9U983ycfp6Ww7bYu9lZ1GmaQ4P6LQBv89R+Na5dFAcibp3eND\r\n2Z/g4Z0WCczxB3bmZZ5g4a7hCMG5vA0s4pnKlvM= generated-by-azure\r\n"
                                }
                            ]
                        }
                    },
				"customData": back_custom_data
                },
	"network_profile": {
		"network_interfaces": [{
			"id": nic_back_result.id,
        }]
    },
	"hardware_profile": {
		"vm_size": "Standard_B1s"
	},
    "hyperVGeneration": "V1"
            
}

#script to change the ip of the backend server in the index.html file of the apche2 server
front_custom_data = base64.b64encode(b"#!/bin/bash\nsudo sed -i 's/127.0.0.1/" + ip_address_back_result.ip_address.encode('utf-8') + b"/g' /var/www/html/index.html\n").decode('latin-1')

FRONT_PARAMETERS={
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "variables": {},
	"location": "westeurope",
	"type": "Microsoft.Compute/virtualMachines",
    "apiVersion": "2019-07-01",
    "name": "front-image-20201001183657",
	"storage_image_reference" :{
    "id" : "/subscriptions/5181e089-3771-4b0d-9e07-9c3a90b2b013/resourceGroups/labo1/providers/Microsoft.Compute/images/front-image-20201001183657"
  },
    "storageProfile": {
        "osDisk": {
			"createOption": "fromImage",
            "managedDisk": {
                "storageAccountType": "Standard_LRS"
            }
			
        },
        "imageReference": {
            "id": "/subscriptions/5181e089-3771-4b0d-9e07-9c3a90b2b013/resourceGroups/labo1/providers/Microsoft.Compute/images/front-image-20201001183657"
        }
    },
	"osProfile": {
                    "computerName": "frontend",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": True,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCRNNBGwIB6nRwmEi3xIWUGO6d1\r\nL6D7HWALfFT104oqFq4EaCNdMuIyZvC0j8/ItSH8fDmPgpkSR0NE/r4CERkUJPnx\r\nGbF+FXTLhBTAQlJnw4OYMOI5/B3wErM8lrJh9MeHvkUPvtsuzJJjSlnmW/63GW72\r\netzSqiiPkNrqu9gNEFoBFkq7pTT511Q/KkYs3rAovsF791UNJXj/iXKqW6LFDGrD\r\n09AyEy2rT+9kKVg7RJEvkmKgPxBRDc+JMJgFywbSqRryP+Bh1sNXwizoUCCgS0mH\r\n9DsfgjIS0tIS10c7MFhWheRtUe/OvFj2wxNJdlxD2gs2CGx+O4TO2Pejt8YiNRw2\r\ns1bKsK7Mp1G7zKedLyEKcnizWfetzygmt26yNLOqoXIzPxHGtWnAA1xXtsEaBS1g\r\n0osVf622owbPBnznCWH0+A+D9F3N50GYbV/VqFB1lmBIBlmY263AUdlZ77ToBKft\r\nK6tkUHn4ecukD2HkQ9ni2IvFIzf4+zuBBKmIKT8= generated-by-azure\r\n"
                                }
                            ]
                        }
                    },
				"customData": front_custom_data
                },
	"network_profile": {
		"network_interfaces": [{
			"id": nic_front_result.id,
        }]
    },
	"hardware_profile": {
		"vm_size": "Standard_B1s"
	},
    "hyperVGeneration": "V1"
            
}

print("Provisioning database virtual machine...")
poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, 'db', DB_PARAMETERS)
print("Done")

print("Provisioning backend virtual machine...")
compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, 'back', BACK_PARAMETERS).result()
print("Done")

print("Provisioning frontend virtual machine...")
compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, 'front', FRONT_PARAMETERS).result()
print("Done")

while(True):
	print("Press q to clean the environment")
	x = input()
	if(x == 'q'):
		resource_client.resource_groups.delete(RESOURCE_GROUP_NAME)
		break;
		