import boto3
import botocore
import time
"""
Best practice to define aws credentials :

On Linux/Unix, you need to create a file containing the credentials : ~/.aws/credentials where credentials is the file containing your aws key

You need to add the following config in this credentials file :

[default]
region=us-east-1
aws_access_key_id=******
aws_secret_access_key=*******
aws_session_token=******

You can find theses informations on the account details in Vocareum


Author : Tran Eric
"""


ec2 = boto3.resource('ec2') # High level client
ec2_low_level = boto3.client('ec2') # Low level client

# KeyPair SSH
keyPairName = '' # Need a KeyPair to SSH into the VM

# Images ID
db_image = 'ami-06b4da222f557db65' # Mysql
backend_image = 'ami-0f33764582e66b4cf' # Ejabberd
frontend_image = 'ami-0cbb6e7fb5a5f662d' # ConverseJS

# Create security groups

SG_SSH = ec2.create_security_group(Description='SSH Access', GroupName='SG-SSH')
SG_SSH.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='TCP',
    FromPort=22,
    ToPort=22
)

SG_Mysql = ec2.create_security_group(Description='Mysql Access', GroupName='SG-Mysql')
SG_Mysql.authorize_ingress(
    CidrIp='172.31.0.0/16',
    IpProtocol='TCP',
    FromPort=3306,
    ToPort=3306
)

SG_Ejabberd = ec2.create_security_group(Description='Ejabberd Access', GroupName='SG-Ejabberd')
SG_Ejabberd.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='TCP',
    FromPort=5280,
    ToPort=5280
)

SG_Conversejs = ec2.create_security_group(Description='ConverseJS Access', GroupName='SG-ConverseJS')
SG_Conversejs.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='TCP',
    FromPort=80,
    ToPort=80
)

# Create all instances

# DB instance (Mysql)
instance_db = ec2.create_instances(
    ImageId=db_image,
    MaxCount=1,
    MinCount=1,
    InstanceType='t2.micro',
    KeyName=keyPairName,
    SecurityGroupIds=[
        SG_SSH.id,
        SG_Mysql.id
    ],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags' : [
                {
                    'Key' : 'db',
                    'Value' : ''
                }
            ]
        }
    ]
)

private_ip_db = instance_db[0].private_ip_address #private ip used by the backend to connect to the db

print('Wait Mysql instance to start')
time.sleep(30) # We wait the Mysql instance to start correctly to ensure a correct behavior for the execution of the script

# Create elastic IP
elastic_ip = ec2_low_level.allocate_address(Domain='vpc')
public_ip = elastic_ip['PublicIp']


# Backend instance (Ejabberd)
instance_backend = ec2.create_instances(
    ImageId=backend_image,
    MaxCount=1,
    MinCount=1,
    InstanceType='t2.micro',
    KeyName=keyPairName,
    SecurityGroupIds=[
        SG_SSH.id,
        SG_Ejabberd.id
    ],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags' : [
                {
                    'Key' : 'backend',
                    'Value' : ''
                }
            ]
        }
    ],
    UserData=f"""#!/bin/bash
sudo sed -i 's/sql_server:.*/sql_server: "{private_ip_db}"/g' /etc/ejabberd/ejabberd.yml
sudo sed -i '0,/^hosts:/""" + "{s/hosts:.*/hosts: [" + '"' + public_ip + '"'  + """]/}' /etc/ejabberd/ejabberd.yml
sudo ejabberdctl stop
sudo ejabberdctl start
sudo ejabberdctl register user1 """ + public_ip + " yoloswag22"
)
# Note : the register is executed to close to the restart of the ejabberd service. Need to connect on the instance to create a user
# sudo ejabberdctl register user1 the_public_elastic_ip yoloswag22

print('Wait Ejabberd instance to start')
time.sleep(30) # Need to wait the instance to start correctly before affecting the Elastic IP

# Attach Elastic IP
resp = ec2_low_level.associate_address(
    AllocationId=elastic_ip['AllocationId'],
    InstanceId=instance_backend[0].instance_id)

print(resp)

# Frontend instance (ConverseJS)
instance_frontend = ec2.create_instances(
    ImageId=frontend_image,
    MaxCount=1,
    MinCount=1,
    InstanceType='t2.micro',
    KeyName=keyPairName,
    SecurityGroupIds=[
        SG_SSH.id,
        SG_Conversejs.id
    ],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags' : [
                {
                    'Key' : 'frontend',
                    'Value' : ''
                }
            ]
        }
    ],
    UserData=f"""#!/bin/bash
sudo sed -i 's|http://.*/bosh|http://{public_ip}:5280/bosh|g' /var/www/html/index.html
    """
)