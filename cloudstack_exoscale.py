import exoscale

exo = exoscale.Exoscale()
zone_gva = exo.compute.get_zone('ch-gva-2')


tmpl = list(exo.compute.list_instance_templates(zone_gva, 'Linux Ubuntu 18.04 LTS 64-bit'))[0]
sshkey = exo.compute.get_ssh_key('cloudsys')

# Create security groups
security_group_base = exo.compute.create_security_group('base')
security_group_web = exo.compute.create_security_group('web')
security_group_ejabberd = exo.compute.create_security_group('ejabberd')
security_group_mariadb = exo.compute.create_security_group('mariadb')

base_rules = [
  exoscale.api.compute.SecurityGroupRule.ingress(
    description='ssh',
    network_cidr='0.0.0.0/0',
    port='22',
    protocol='tcp'
  )
]

ejabberd_rules = [
  exoscale.api.compute.SecurityGroupRule.ingress(
    description='ejabberd_standard',
    network_cidr='0.0.0.0/0',
    port='5222',
    protocol='tcp'
  ),
  exoscale.api.compute.SecurityGroupRule.ingress(
    description='ejabberd_jabber',
    network_cidr='0.0.0.0/0',
    port='5223',
    protocol='tcp'
  ),
  exoscale.api.compute.SecurityGroupRule.ingress(
    description='ejabberd_server',
    network_cidr='0.0.0.0/0',
    port='5269',
    protocol='tcp'
  ),
    exoscale.api.compute.SecurityGroupRule.ingress(
    description='ejabberd_websocket',
    network_cidr='0.0.0.0/0',
    port='5280',
    protocol='tcp'
  ),
]

web_rules = [
  exoscale.api.compute.SecurityGroupRule.ingress(
    description='HTTP',
    network_cidr='0.0.0.0/0',
    port='80',
    protocol='tcp'
  ),
  exoscale.api.compute.SecurityGroupRule.ingress(
    description='HTTPS',
    network_cidr='0.0.0.0/0',
    port='443',
    protocol='tcp'
  )
]

mariadb_rules = [
  exoscale.api.compute.SecurityGroupRule.ingress(
    description='mariadb_standard',
    network_cidr='0.0.0.0/0',
    port='3306',
    protocol='tcp'
  )
]

print('Creating base firewall')
for rule in base_rules:
  security_group_base.add_rule(rule)

print('Creating mariadb firewall')
for rule in mariadb_rules:
  security_group_mariadb.add_rule(rule)

print('Creating ejabberd firewall')
for rule in ejabberd_rules:
  security_group_ejabberd.add_rule(rule)

print('Creating web frontend firewall')
for rule in web_rules:
  security_group_web.add_rule(rule)

# Create instances
print('Creating mariadb instance...')
mariadb_instance = exo.compute.create_instance(
  name='mariadb-auto',
  ssh_key=sshkey,
  zone=zone_gva,
  type=exo.compute.get_instance_type('small'),
  template=tmpl,
  volume_size=10,
  security_groups=[security_group_base, security_group_mariadb],
  user_data="""
#cloud-config
runcmd:
  - apt-get --yes update
  - apt-get --yes install mysql-server
  - 'sudo sed -i "s/.*bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf'
  - sudo service mysql stop
  - sudo service mysql start
  - sudo mysqladmin password "yoloswag22"
  - echo "GRANT ALL ON ejabberd.* TO 'ejabberd'@'%' IDENTIFIED BY 'yoloswag22';" | sudo mysql
  - echo "FLUSH PRIVILEGES;" | sudo mysql
  - echo "CREATE DATABASE ejabberd;" | mysql -u ejabberd --password=yoloswag22
  - wget https://raw.githubusercontent.com/processone/ejabberd/master/sql/mysql.sql
  - mysql -D ejabberd -u ejabberd --password=yoloswag22 < mysql.sql
  """
)
print('Done, mariadb IP: %s' % (mariadb_instance.ipv4_address))

print('Creating ejabberd instance...')
ejabberd_instance = exo.compute.create_instance(
  name='ejabberd-auto',
  zone=zone_gva,
  ssh_key=sshkey,
  type=exo.compute.get_instance_type('small'),
  template=tmpl,
  volume_size=10,
  security_groups=[security_group_base, security_group_ejabberd],
  user_data="""
#cloud-config
runcmd:
  - sudo apt-get --yes update
  - sudo apt install --yes ejabberd erlang-p1-mysql mysql-client
  - echo "WRITING CONFIG"
  - 'sudo sed -i -i "s/auth_method: internal/auth_method: sql/" /etc/ejabberd/ejabberd.yml'
  - "sudo sed -i \\"0,/^hosts:/{s/hosts:.*/hosts: ['$(hostname -I | awk '{print $1}')']/}\\" /etc/ejabberd/ejabberd.yml"
  - "sudo sed -i '/^  - \\"localhost\\"/d' /etc/ejabberd/ejabberd.yml"
  - "sudo sed -i '$a sql_type: \\"mysql\\"\n' /etc/ejabberd/ejabberd.yml"
  - "sudo sed -i '$a sql_server: \\"%s\\"' /etc/ejabberd/ejabberd.yml"
  - "sudo sed -i '$a sql_database: \\"ejabberd\\"\n' /etc/ejabberd/ejabberd.yml"
  - "sudo sed -i '$a sql_username: \\"ejabberd\\"\n' /etc/ejabberd/ejabberd.yml"
  - "sudo sed -i '$a sql_password: \\"yoloswag22\\"\n' /etc/ejabberd/ejabberd.yml"
  - "sudo sed -i '$a default_db: \\"sql\\"\n' /etc/ejabberd/ejabberd.yml"
  - echo "RESTARTING..."
  - sudo ejabberdctl stop
  - sudo ejabberdctl stop
  - sudo ejabberdctl start
  - echo "REGISTERING USER..."
  - sudo ejabberdctl register admin1 localhost yoloswag22
  - echo "DONE"
  """ % (mariadb_instance.ipv4_address)
)
print('Done, ejabberd IP: %s' % (ejabberd_instance.ipv4_address))

print('Creating frontend instance...')
frontend_instance = exo.compute.create_instance(
  name='frontend-auto',
  zone=zone_gva,
  ssh_key=sshkey,
  type=exo.compute.get_instance_type('tiny'),
  template=tmpl,
  volume_size=10,
  security_groups=[security_group_base, security_group_web],
  user_data="""
#cloud-config
runcmd:
  - apt-get --yes update
  - sudo apt install --yes apache2
  - wget https://gist.githubusercontent.com/ovesco/f9c4474cceb6e5c358c3580f8b39fee7/raw/a845b89abc491e4f9439c285cc5b19a963066b06/index.html
  - sudo rm /var/www/html/index.html
  - sudo cp index.html /var/www/html/index.html
  - sudo sed -i "s/IP_ADDRESS/%s/g" /var/www/html/index.html
""" % (ejabberd_instance.ipv4_address)
)
print('Done, frontend IP: %s' % (frontend_instance.ipv4_address))
print('You can now access {ip} and connect with admin1@{ejj} and password yoloswag22'.format(ip=frontend_instance.ipv4_address, ejj=ejabberd_instance.ipv4_address))