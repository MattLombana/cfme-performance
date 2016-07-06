#! /usr/bin/env python

from ovirtsdk.api import API
from ovirtsdk.xml import params
import ast
import sys
import time

appliance = ast.literal_eval(sys.argv[1])
rhevm_hostname = sys.argv[2]
user = sys.argv[3]
passw = sys.argv[4]

MB = 1024 * 1024
GB = 1024 * MB

ca = '/tmp/rhevm_appliance_certs/{}'.format(rhevm_hostname)
rhevm_url = 'https://{}'.format(rhevm_hostname)

api = API(url=rhevm_url, username=user, password=passw, ca_file=ca)

vm_name = appliance['vm_name']
template_object = api.templates.get(name=appliance['template'])
template_disks = params.Disks(clone=appliance['clone_template'])
cluster_object = api.clusters.get(name=appliance['cluster'])
host_object = api.hosts.get(appliance['host'])
migrate = appliance['migrate']
appliance_nics = appliance['NICS'][:]
appliance_memory = appliance['memory_size']
appliance_type = appliance['vm_type']
num_cores = appliance['cores']
num_cpus = appliance['cpus']
placement_object = params.VmPlacementPolicy(host=host_object, affinity=migrate)
cpu_topology = params.CpuTopology(cores=num_cores, threads=num_cpus)
cpu_object = params.CPU(topology=cpu_topology)

vm_params = params.VM(
    name=vm_name,
    template=template_object,
    disks=template_disks,
    cluster=cluster_object,
    host=host_object,
    cpu=cpu_object,
    memory=appliance['memory_size'] * GB,
    placement_policy=placement_object)

cfme_appliance = api.vms.add(vm_params)
time.sleep(60)

for disk in appliance['disks']:
    disk_size = appliance['disks'][disk]['size'] * GB
    interface_type = appliance['disks'][disk]['interface']
    disk_format = appliance['disks'][disk]['format']
    allocation = appliance['disks'][disk]['allocation']
    location = appliance['disks'][disk]['location']
    store = api.storagedomains.get(name=location)
    domain = params.StorageDomains(storage_domain=[store])
    disk_param = params.Disk(
        description=disk,
        storage_domains=domain,
        size=disk_size,
        interface=interface_type,
        format=disk_format,
        type_=allocation)
    new_disk = cfme_appliance.disks.add(disk=disk_param)
time.sleep(10)

if len(appliance_nics) > 0:
    current_nics = cfme_appliance.get_nics().list()
    current_networks = []
    for nic in current_nics:
            network_id = nic.get_network().id
            current_networks.append(api.networks.get(id=network_id).name)

    new_set = set(appliance_nics)
    current_set = set(current_networks)
    appliance_nics = list(new_set - current_set)

for i in range(len(appliance_nics)):
    network_name = params.Network(name=appliance_nics[i])
    nic_name = params.NIC(name='card{}'.format(i), network=network_name)
    cfme_appliance.nics.add(nic=nic_name)
time.sleep(10)

dev = params.Boot(dev='network')
cfme_appliance.os.boot.append(dev)
cfme_appliance.update()

cfme_appliance.start()

api.disconnect()
