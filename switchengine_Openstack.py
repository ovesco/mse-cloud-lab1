import openstack

KEYPAIR_NAME = "silvestri_keypair"
FLAVOR_NAME = "m1.small"
NETWORK_NAME = "private"

def create_server(conn, image_name, server_name):
    print("Create Server:")

    image = conn.compute.find_image(image_name)
    flavor = conn.compute.find_flavor(FLAVOR_NAME)
    network = conn.network.find_network(NETWORK_NAME)
    keypair = create_keypair(conn)

    server = conn.compute.create_server(
        name=server_name, image_id=image.id, flavor_id=flavor.id,
        networks=[{"uuid": network.id}], key_name=keypair.name)

    server = conn.compute.wait_for_server(server)

conn.compute.start_server(conn.compute.find_server("maria2")['id'])
create_server(conn, 'ejabberd_ok', 'eja_script')
create_server(conn, 'front_ok', 'front_script')

conn.compute.add_floating_ip_to_server(conn.compute.find_server("eja_script")['id'], "86.119.40.117")
conn.compute.add_floating_ip_to_server(conn.compute.find_server("front_script")['id'], "86.119.36.94")
conn.compute.remove_security_group_from_server(conn.compute.find_server("eja_script")['id'], conn.network.find_security_group("bf51955c-7f11-45cd-92a0-47e7eaac35c1"))
conn.compute.add_security_group_to_server(conn.compute.find_server("eja_script")['id'], conn.network.find_security_group("4935f7a3-6453-467f-b59b-437cd4b73696"))
conn.compute.add_security_group_to_server(conn.compute.find_server("eja_script")['id'], conn.network.find_security_group("1a05662d-cbc1-42fe-ad90-df7e76927de4"))
conn.compute.remove_security_group_from_server(conn.compute.find_server("front_script")['id'], conn.network.find_security_group("bf51955c-7f11-45cd-92a0-47e7eaac35c1"))
conn.compute.add_security_group_to_server(conn.compute.find_server("front_script")['id'], conn.network.find_security_group("4935f7a3-6453-467f-b59b-437cd4b73696"))
conn.compute.add_security_group_to_server(conn.compute.find_server("front_script")['id'], conn.network.find_security_group("75cb2d72-2112-408d-adfa-033c2de15bc2"))