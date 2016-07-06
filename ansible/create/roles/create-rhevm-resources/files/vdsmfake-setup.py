#! /usr/bin/env python

from math import ceil
from xml.etree import ElementTree
import requests
import ast
import log as logger
import sys

vdsmfake = ast.literal_eval(sys.argv[1])

####################################################################################################
#                                                                                                  #
#                               Methods used for resource creation                                 #
#                                                                                                  #
####################################################################################################


def create_etc_hosts_file(host_names):
    """Creates the hosts file that should be used on the appliance.
    Writes loopback address then the hostname to a file named 'hosts' in the same
    directory as this file"""
    with open('hosts', 'w') as hosts:
        for host in host_names:
            hosts.write('127.0.0.1 {}\n'.format(host))


def get_hosts():
    """Returns a list containing the names of all hosts on the appliance"""
    host_names = []
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/hosts/"
    header = {'Accept': 'application/xml'}
    response = requests.get(
        url=url,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header
    )
    xml_tree = ElementTree.fromstring(response.content)
    host_list = xml_tree.findall('host')
    for host in host_list:
        host_names.append(host.find('name').text)
    return host_names


def create_host(name, address, password, cluster_name):
    """Creates a host on cluster <cluster>. Expects string values"""
    cluster_id = get_cluster_id(cluster_name)
    xml_data = ("<host><name>{}</name><address>{}</address>"
                "<root_password>{}</root_password><cluster id='{}' "
                "href='/api/clusters/{}'/></host>"
                .format(name, address, password, cluster_id, cluster_id))
    appliance = vdsmfake['appliance']['ip_address']
    url = "https://" + appliance + "/api/hosts/"
    header = {"content-type": "application/xml", "Accept": "application/xml"}
    response = requests.post(
        url=url,
        data=xml_data,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False)
    if response.status_code != 201:
        logger.error('create_host failed: response: {}'.format(response.content))


def create_hosts(host_names):
    """Creates a host for each name within host_names. Expects a list of tuples with format(hostname,
    host_address, host_password, host_cluster)"""
    hosts = get_hosts()
    for name, address, password, cluster in host_names:
        if name in hosts:
            continue
        create_host(name, address, password, cluster)


def get_virtual_machines():
    """Returns a list containing the names of all VMs on the appliance"""
    vm_names = []
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/vms/"
    header = {'Accept': 'application/xml'}
    response = requests.get(
        url=url,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header
    )
    xml_tree = ElementTree.fromstring(response.content)
    vm_list = xml_tree.findall('vm')
    for vm in vm_list:
        vm_names.append(vm.find('name').text)
    return vm_names


def get_vm_id(vm_name):
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/vms/"
    header = {'Accept': 'application/xml'}
    response = requests.get(
        url=url,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False
    )
    tree = ElementTree.fromstring(response.content)
    for element in tree.getchildren():
        if element.find('name').text == vm_name:
            return element.attrib['id']


def create_virtual_machine_NIC(vm_name, network_name):
    vm_id = get_vm_id(vm_name)
    xml_data = "<nic><name>nic1</name><network><name>{}</name></network></nic>".format(network_name)
    appliance = vdsmfake['appliance']['ip_address']
    url = "https://" + appliance + "/api/vms/{}/nics".format(vm_id)
    header = {"content-type": "application/xml", "Accept": "application/xml"}
    response = requests.post(
        url=url,
        data=xml_data,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False)
    if response.status_code != 201:
        logger.error('create_virtual_machine_NIC failed: response: {}'.format(response.content))


def create_virtual_machine_disk(vm_name, disk_size, storage_name):
    vm_id = get_vm_id(vm_name)
    storage_id = get_storage_id(storage_name)
    xml_data = ("<disk><storage_domains><storage_domain id='{}'/></storage_domains><size>{}</size>"
                "<type>system</type><interface>virtio</interface><format>cow</format>"
                "<bootable>true</bootable></disk>".format(storage_id, disk_size))
    appliance = vdsmfake['appliance']['ip_address']
    url = "https://" + appliance + "/api/vms/{}/disks".format(vm_id)
    header = {"content-type": "application/xml", "Accept": "application/xml"}
    response = requests.post(
        url=url,
        data=xml_data,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False)
    if response.status_code != 201:
        logger.error('create_virtual_machine_disk failed: response: {}'.format(response.content))


def create_virtual_machine_from_template(name, cluster, template, memory_size):
    """Creates a virtual machine from the specified template. Expects strings for all arguments,
    with memory_size in bits"""
    xml_data = ("<vm><name>{}</name>"
    "<cluster><name>{}</name></cluster>"
    "<template><name>{}</name></template>"
    "<memory>{}</memory>"
    "<memory_policy><guaranteed>{}</guaranteed></memory_policy>"
    "<os type='other_linux'>"
    "<boot dev='hd'/></os>"
    "<type>server</type></vm>".format(name, cluster, template, memory_size, memory_size))

    appliance = vdsmfake['appliance']['ip_address']
    url = "https://" + appliance + "/api/vms"
    header = {"content-type": "application/xml", "Accept": "application/xml"}
    response = requests.post(
        url=url,
        data=xml_data,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False)
    if response.status_code != 201:
        logger.error('create_virtual_machine_from_template failed: response: {}'
            .format(response.content))


def create_virtual_machines_from_template(VMs_to_create):
    """Creates one Virtual machine for each name in VMs_to_create, from the specified
    template. Expects a list of tuples, with order (name, cluster, template, memory_size)"""
    vms = get_virtual_machines()
    for name, cluster, template, memory_size in VMs_to_create:
        if name in vms:
            continue
        create_virtual_machine_from_template(name, cluster, template, memory_size)


def create_fake_virtual_machines(VMs_to_create):
    """Creates one Virtual machine on the appliance for each VM in VMs_to_create, from the specified
    template. Expects a list of tuples, with order:
    (name, cluster, template,  memory_size, disk_size, storage_name, network)"""
    vms = get_virtual_machines()
    for name, cluster, template, memory_size, disk_size, storage_name, network in VMs_to_create:
        if name in vms:
            continue
        create_virtual_machine_from_template(name, cluster, template, memory_size)
        create_virtual_machine_NIC(name, network)
        create_virtual_machine_disk(name, disk_size, storage_name)


def get_storages():
    """Returns a list containing the names of all data-stores on the appliance"""
    storage_names = []
    header = {'Accept': 'application/xml'}
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/storagedomains/"
    response = requests.get(
        url=url,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header
    )
    xml_tree = ElementTree.fromstring(response.content)
    storage_list = xml_tree.findall('storage_domain')
    for storage in storage_list:
        storage_names.append(storage.find('name').text)
    return storage_names


def get_storage_id(storage_name):
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/storagedomains/"
    header = {'Accept': 'application/xml'}
    response = requests.get(
        url=url,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False
    )
    tree = ElementTree.fromstring(response.content)
    for element in tree.getchildren():
        if element.find('name').text == storage_name:
            return element.attrib['id']


def create_storage(storage_type, fs_type, name, address, path, hostname):
    xml_data = ("<storage_domain><name>{}</name><type>{}</type><storage><type>{}</type>"
                "<address>{}</address><path>{}</path></storage><host><name>{}</name></host>"
                "</storage_domain>".format(name, storage_type, fs_type, address, path, hostname))
    appliance = vdsmfake['appliance']['ip_address']
    url = "https://" + appliance + "/api/storagedomains"
    header = {"content-type": "application/xml", "Accept": "application/xml"}
    response = requests.post(
        url=url,
        data=xml_data,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False)
    if response.status_code != 201:
        logger.error('create_storage failed: response: {}'.format(response.content))


def create_storages(storage_names):
    """Creates a new data-store on the appliance for each name in storage_names. Expects a list of
    tuples with format(storage_type, fs_type, name, address, path, hostname)"""
    storages = get_storages()
    for storage_type, fs_type, name, address, path, hostname in storage_names:
        if name in storages:
            continue
        create_storage(storage_type, fs_type, name, address, path, hostname)


def get_clusters():
    """Returns a list containing the names of all clusters on the appliance"""
    cluster_names = []
    header = {'Accept': 'application/xml'}
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/clusters/"
    response = requests.get(
        url=url,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header
    )
    xml_tree = ElementTree.fromstring(response.content)
    cluster_list = xml_tree.findall('cluster')
    for cluster in cluster_list:
        cluster_names.append(cluster.find('name').text)
    return cluster_names


def create_cluster(name, cpu, datacenter):
    """ Method to create clusters. Expects a list of tuples with the form:
    (cluster_name, cluster_cpu_type, Data_center) """
    dc_id = get_datacenter_id(datacenter)
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/clusters"
    header = {"content-type": "application/xml", "Accept": "application/xml"}
    xml_data = ('<cluster><name>{}</name><cpu id="{}"/><data_center id="{}"/>'
        '</cluster>'.format(name, cpu, dc_id))
    response = requests.post(
        url=url,
        data=xml_data,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False
    )
    if response.status_code != 201:
        logger.error('could not create cluster, response: {}'.format(response.content))


def create_clusters(cluster_tuples):
    """Creates a new cluster on the appliance for each name in cluster_names"""
    for name, cpu, datacenter in cluster_tuples:
        create_cluster(name, cpu, datacenter)


def get_cluster_id(cluster_name):
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/clusters/"
    header = {'Accept': 'application/xml'}
    response = requests.get(
        url=url,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False
    )
    tree = ElementTree.fromstring(response.content)
    for element in tree.getchildren():
        if element.find('name').text == cluster_name:
            return element.attrib['id']


def turn_on_vms(name_list):
    """Method to turn on all vms. Expects a list of Vm names"""
    for vm in name_list:
        vm_id = get_vm_id(vm)
        url = "https://{}/api/vms/{}/start".format(vdsmfake['appliance']['ip_address'], vm_id)
        header = {"content-type": "application/xml", "Accept": "application/xml"}
        xml_data = '<action><vm><os><boot dev="hd"/></os></vm></action>'
        response = requests.post(
            url=url,
            data=xml_data,
            auth=(vdsmfake['appliance']['rest_api']['username'],
                  vdsmfake['appliance']['rest_api']['password']),
            verify=False,
            headers=header,
            allow_redirects=False
        )
        if response.status_code != 201:
            logger.error('could not turn on vm: {}, response: {}'.format(vm, response.content))


def get_datacenter_id(datacenter_name):
    """ Method which returns the id of the specified data_center"""
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/datacenters/"
    header = {'Accept': 'application/xml'}
    response = requests.get(
        url=url,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False
    )
    tree = ElementTree.fromstring(response.content)
    for element in tree.getchildren():
        if element.find('name').text == datacenter_name:
            return element.attrib['id']


def create_network(name, datacenter):
    """ Method to create a network object"""
    dc_id = get_datacenter_id(datacenter)
    url = "https://" + vdsmfake['appliance']['ip_address'] + "/api/networks"
    header = {"content-type": "application/xml", "Accept": "application/xml"}
    xml_data = ('<network><name>{}</name><data_center id="{}"/></network>'.format(name, dc_id))
    response = requests.post(
        url=url,
        data=xml_data,
        auth=(vdsmfake['appliance']['rest_api']['username'],
              vdsmfake['appliance']['rest_api']['password']),
        verify=False,
        headers=header,
        allow_redirects=False
    )
    if response.status_code != 201:
        logger.error('could not create network, response: {}'.format(response.content))


def create_networks(network_tuples):
    """ Method to create networks, Expects a list of tuples with the form:
    (network_name, Data_center)"""
    for name, datacenter in network_tuples:
        create_network(name, datacenter)


####################################################################################################
#                                                                                                  #
#                                 Methods which create resources                                   #
#                                                                                                  #
####################################################################################################


def clusters():
    num_clusters = vdsmfake['fake_resources']['clusters']['number'] - 1
    cpu = vdsmfake['fake_resources']['clusters']['cpu']
    datacenter = vdsmfake['fake_resources']['clusters']['datacenter']
    clusters = []
    for i in range(num_clusters):
        cluster_name = 'Default{}'.format(i + 2)
        temp_tuple = (cluster_name, cpu, datacenter)
        clusters.append(temp_tuple)
    create_clusters(clusters)


def hosts():
    num_hosts = vdsmfake['fake_resources']['hosts']['number']
    password = vdsmfake['fake_resources']['hosts']['password']
    num_clusters = vdsmfake['fake_resources']['clusters']['number']
    hosts_per_cluster = int(ceil(float(num_hosts) / float(num_clusters)))
    host_names = []
    hosts = []
    for i in range(num_hosts):
        hosts_so_far = len(hosts)
        cluster = 'Default{}'.format(((hosts_so_far / hosts_per_cluster) + 1))
        if cluster == "Default1":
            cluster = "Default"
        host_name = 'fakehost' + str(i + 1).zfill(4)
        temp_tuple = (host_name, host_name, password, cluster)
        host_names.append(host_name)
        hosts.append(temp_tuple)
    create_etc_hosts_file(host_names)
    create_hosts(hosts)


def storage_domains():
    num_hosts = vdsmfake['fake_resources']['hosts']['number']
    address = 'localhost'
    num_storages = vdsmfake['fake_resources']['storage-domains']['number'] - 1
    storage_type = vdsmfake['fake_resources']['storage-domains']['storage_type']
    fs_type = vdsmfake['fake_resources']['storage-domains']['fs_type']
    storage_names = []
    for i in range(num_storages):
        storage_name = 'fakestorage' + str(i + 1).zfill(4)
        hostname = 'fakehost' + str((i % num_hosts) + 1).zfill(4)
        path = '/{}'.format(storage_name)
        temp_tuple = (storage_type, fs_type, storage_name, address, path, hostname)
        storage_names.append(temp_tuple)
    create_storages(storage_names)


def networks():
    num_networks = vdsmfake['fake_resources']['networks']['number'] - 1
    datacenter = vdsmfake['fake_resources']['networks']['datacenter']
    networks = []
    for i in range(num_networks):
        network_name = 'fakenetwork' + str(i + 2).zfill(4)
        temp_tuple = (network_name, datacenter)
        networks.append(temp_tuple)
    create_networks(networks)


def vms():
    num_vms = vdsmfake['fake_resources']['vms']['number']
    network = vdsmfake['fake_resources']['vms']['network']
    template = vdsmfake['fake_resources']['vms']['template']
    memory_size = vdsmfake['fake_resources']['vms']['memory_size']
    disk_size = vdsmfake['fake_resources']['vms']['disk_size']
    num_clusters = vdsmfake['fake_resources']['clusters']['number']
    vms_per_cluster = int(ceil(float(num_vms) / float(num_clusters)))
    vm_names = []
    for i in range(num_vms):
        vms_so_far = len(vm_names)
        cluster = 'Default{}'.format(((vms_so_far / vms_per_cluster) + 1))
        if cluster == "Default1":
            cluster = "Default"
        vm_name = 'fakevm' + str(i + 1).zfill(4)
        storage_name = 'fakestorage001'
        temp_tuple = (vm_name, cluster, template, memory_size, disk_size, storage_name, network)
        vm_names.append(temp_tuple)
    create_fake_virtual_machines(vm_names)


def turn_on_list():
    num_vms = vdsmfake['fake_resources']['vms']['number']
    num_clusters = vdsmfake['fake_resources']['clusters']['number']
    vms_per_cluster = int(ceil(float(num_vms) / float(num_clusters)))
    turn_on_size = int(vms_per_cluster / 2)
    name_list = []
    for i in range(num_clusters):
        start_num = (i * vms_per_cluster) + 1
        end_num = start_num + turn_on_size
        for i in range(start_num, end_num):
            name_list.append('fakevm{}'.format(str(i).zfill(4)))
        turn_on_vms(name_list)


if __name__ == '__main__':
    if 'clusters' in vdsmfake['fake_resources']:
        clusters()

    if 'hosts' in vdsmfake['fake_resources']:
        hosts()

    if 'storage-domains' in vdsmfake['fake_resources']:
        storage_domains()

    if 'networks' in vdsmfake['fake_resources']:
        networks()

    if 'vms' in vdsmfake['fake_resources']:
        vms()
        turn_on_list()
