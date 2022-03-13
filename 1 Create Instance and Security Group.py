import time
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2", region_name="ap-southeast-2")
response = ec2.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

#create security group

try:
    response = ec2.create_security_group(GroupName='23019722-sg',
                                         Description='security group for development environment',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)

#create key pair

key_pair = ec2.create_key_pair(KeyName="23019722-key")

#create instance
reservation = ec2.run_instances(
        ImageId="ami-d38a4ab1",
        SecurityGroups=['23019722-sg'],
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="23019722-key"
    )

instance = reservation["Instances"][0]
id = instance["InstanceId"]
print(id)

#get public IP address
#console is a bit slow to show, so wait for 20 sec here.
time.sleep(20)
EC2_RESOURCE = boto3.resource('ec2')
instances = EC2_RESOURCE.instances.all()
for instance in instances:
    if instance.id == id:
        print(instance.public_ip_address)

#get public IP address, method 2
time.sleep(50)
reservations = ec2.describe_instances(InstanceIds=[id]).get("Reservations")
for reservation in reservations:
    for instance in reservation['Instances']:
        print(instance.get("PublicIpAddress"))