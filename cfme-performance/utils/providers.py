"""REST API interactions to the appliance for provider and VM configuration/testing."""
from mgmtsystem.virtualcenter import VMWareSystem
from mgmtsystem.rhevm import RHEVMSystem
from utils.conf import cfme_performance
from utils.log import logger
import copy
import json
import requests
import time


def get_all_provider_ids():
    """Returns an integer list of provider ID's via the REST API"""
    logger.debug('Retrieving the list of provider ids')

    provider_ids = []
    provider_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] + "/api/providers",
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )

    provider_json = provider_response.json()
    provider_urls = provider_json['resources']
    for url in provider_urls:
        last_slash = url['href'].rfind('/')
        provider_ids.append(int(url['href'][last_slash + 1:]))

    return provider_ids


def get_all_vm_ids():
    """Returns an integer list of vm ID's via the REST API"""
    logger.debug('Retrieving the list of vm ids')

    vm_ids = []
    vm_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] + "/api/vms",
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )

    vm_json = vm_response.json()
    vm_urls = vm_json['resources']
    for url in vm_urls:
        last_slash = url['href'].rfind('/')
        vm_ids.append(int(url['href'][last_slash + 1:]))

    return vm_ids


def get_all_host_ids():
    """Returns an integer list of host ID's via the Rest API"""
    logger.debug('Retrieving the list of host ids')

    host_ids = []
    host_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] + "/api/hosts",
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )

    host_json = host_response.json()
    host_urls = host_json['resources']
    for url in host_urls:
        last_slash = url['href'].rfind('/')
        host_ids.append(int(url['href'][last_slash + 1:]))
    return host_ids


def get_all_template_ids():
    """Returns an integer list of template ID's via the Rest API"""
    logger.debug('Retrieving the list of template ids')

    template_ids = []
    template_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] + "/api/templates",
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )

    template_json = template_response.json()
    template_urls = template_json['resources']
    for url in template_urls:
        last_slash = url['href'].rfind('/')
        template_ids.append(int(url['href'][last_slash + 1:]))
    return template_ids


def get_provider_details(provider_id):
    """Returns the name, and type associated with the provider_id"""
    logger.debug('Retrieving the provider details for ID: {}'.format(provider_id))

    details = {}
    response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] +
            "/api/providers/" + str(provider_id),
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )
    details_json = response.json()

    details['id'] = details_json['id']
    details['name'] = str(details_json['name'])
    details['type'] = str(details_json['type'])

    return details


def get_vm_details(vm_id):
    """Returns the name, type, vendor, host_id, and power_state associated with the vm_id"""
    logger.vdebug('Retrieving the VM details for ID: {}'.format(vm_id))

    details = {}
    response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] +
            "/api/vms/" + str(vm_id),
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )
    details_json = response.json()

    details['id'] = details_json['id']
    if 'ems_id' in details_json:
        details['ems_id'] = details_json['ems_id']
    details['name'] = str(details_json['name'])
    details['type'] = str(details_json['type'])
    details['vendor'] = str(details_json['vendor'])
    if 'host_id' in details_json:
        details['host_id'] = str(details_json['host_id'])
    details['power_state'] = str(details_json['power_state'])
    return details


def get_template_details(template_id):
    """Returns the name, type, and guid associated with the template_id"""
    logger.debug('Retrieving the template details for ID: {}'.format(template_id))

    template_details = {}
    template_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] +
            "/api/templates/" + str(template_id),
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )
    template_json = template_response.json()

    template_details['name'] = str(template_json['name'])
    template_details['type'] = str(template_json['type'])
    template_details['guid'] = str(template_json['guid'])
    return template_details


def get_all_template_details():
    """Returns a dictionary mapping template ids to their name, type, and guid"""
    all_details = {}
    for id in get_all_template_ids():
        all_details[id] = {}
        all_details[id] = get_template_details(id)
    return all_details


def get_provider_id(provider_name):
    """"Return the ID associated with the specified provider name"""
    logger.debug('Retrieving the ID for provider: {}'.format(provider_name))
    for provider_id in get_all_provider_ids():
        details = get_provider_details(provider_id)
        if details['name'] == provider_name:
            return provider_id
    return


def get_vm_id(vm_name):
    """"Return the ID associated with the specified VM name"""
    logger.debug('Retrieving the ID for VM: {}'.format(vm_name))
    for vm_id in get_all_vm_ids():
        details = get_vm_details(vm_id)
        if details['name'] == vm_name:
            return vm_id
    return


def get_vm_ids(vm_names):
    """Returns a dictionary mapping each VM name to it's id"""
    name_list = vm_names[:]
    logger.debug('Retrieving the IDs for {} VM(s)'.format(len(name_list)))
    id_map = {}
    for vm_id in get_all_vm_ids():
        if len(name_list) == 0:
            break
        vm_name = get_vm_details(vm_id)['name']
        if vm_name in name_list:
            id_map[vm_name] = vm_id
            name_list.remove(vm_name)
    return id_map


def get_template_guids(template_dict):
    """Returns a list of tuples. The inner tuples are formated so that each guid is in index 0, and its
    provider's name is in index 1. Expects a dictionary mapping a provider to its templates"""
    result_list = []
    all_template_details = get_all_template_details()
    for provider in template_dict:
        provider_type = cfme_performance['providers'][provider]['type']
        for template_name in template_dict[provider]:
            inner_tuple = ()
            for id in all_template_details:
                if ((all_template_details[id]['name'] == template_name) and
                        (all_template_details[id]['type'] == provider_type + '::Template')):
                    inner_tuple += (all_template_details[id]['guid'],)
                    inner_tuple += (cfme_performance['providers'][provider]['name'],)
                    result_list.append(inner_tuple)
    return result_list


def add_provider(provider):
    """Adds a provider via the REST API."""
    logger.vdebug('Adding Provider: {}, Type: {}'.format(provider['name'], provider['type']))

    data_dict = {
        "action": "create",
        "resources": [{
            "name": provider['name'],
            "type": provider['type'],
            "credentials": [{
                "userid": provider['credentials']['username'],
                "password": provider['credentials']['password']
            }]
        }]
    }

    if 'ip_address' in provider:
        data_dict['resources'][0]['hostname'] = provider['ip_address']

    if (provider['type'] == 'ManageIQ::Providers::Amazon::CloudManager' or
    provider['type'] == 'ManageIQ::Providers::Google::CloudManager'):
        data_dict['resources'][0]['provider_region'] = provider['provider_region']

    if 'metrics_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['metrics_credentials']['username'],
            "password": provider['metrics_credentials']['password'],
            "auth_type": "metrics"
        })
    elif 'password_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['password_credentials']['username'],
            "password": provider['password_credentials']['password'],
            "auth_type": "password"
        })
    elif 'bearer_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['bearer_credentials']['username'],
            "password": provider['bearer_credentials']['password'],
            "auth_type": "bearer"
        })
    elif 'amqp_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['amqp_credentials']['username'],
            "password": provider['amqp_credentials']['password'],
            "auth_type": "amqp"
        })
    elif 'ssh_keypair_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['ssh_keypair_credentials']['username'],
            "password": provider['ssh_keypair_credentials']['password'],
            "auth_type": "ssh_keypair"
        })

    json_data = json.dumps(data_dict)
    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/providers",
                             data=json_data,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('Added Provider: {}, Response: {}'.format(provider['name'], response))


def add_providers(providers):
    """Adds a provider with one request per provider via the REST API."""
    starttime = time.time()
    for provider in providers:
        add_provider(cfme_performance['providers'][provider])
    logger.info('Added Providers in: {}s'.format(round(time.time() - starttime, 2)))


def add_host_credentials(provider):
    """"Adds host credentials to a provider via the REST API"""
    data_dict = {
        "action": "edit",
        "resource": {
            "credentials": {
                "userid": provider['host_credentials']['username'],
                "password": provider['host_credentials']['password']
            }
        }
    }

    json_data = json.dumps(data_dict)
    appliance = cfme_performance['appliance']['ip_address']
    for host in get_all_host_ids():
        response = requests.post("https://" + appliance + "/api/hosts/" + str(host),
                                 data=json_data,
                                 auth=(cfme_performance['appliance']['rest_api']['username'],
                                       cfme_performance['appliance']['rest_api']['password']),
                                 verify=False,
                                 headers={"content-type": "application/json"},
                                 allow_redirects=False)

        if response.status_code != 200:
            logger.debug(response.text)

    logger.debug('Added host credentials, Response: {}'.format(response))


def scan_provider_vm(vm_id):
    """Performs Smart State Analysis on the specified VM via the REST API"""
    logger.vdebug('Scanning VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "scan"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.vdebug('Queued Scan VM: {}, Response: {}'.format(vm_id, response))


def scan_provider_vms(vm_ids):
    """Performs Smart State Analysis on the specified VMs with one request per VM
    via the REST API"""
    starttime = time.time()
    for vm in vm_ids:
        scan_provider_vm(vm)
    logger.vdebug('Queued Scan {} VM(s) in: {}s'.format(len(vm_ids),
        round(time.time() - starttime, 2)))


def scan_provider_vms_bulk(vm_ids):
    """Performs Smart State Analysis on the specified VMs with one request via the REST API"""
    starttime = time.time()

    appliance = cfme_performance['appliance']['ip_address']
    resources = []
    for vm_id in vm_ids:
        resources.append({
            "href": "https://" + appliance + "/api/vms/" + str(vm_id)
        })

    data_dict = {
        "action": "scan",
        "resources": resources
    }
    data_json = json.dumps(data_dict)
    response = requests.post("https://" + appliance + "/api/vms/",
                             data=data_json,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.vdebug('Queued Scan {} VM(s) in: {}s'.format(len(vm_ids),
        round(time.time() - starttime, 2)))


def refresh_provider(provider_id):
    """Refresh the specified provider via the REST API"""
    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/providers/" + str(provider_id),
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Queued Refresh Provider: {}, Response: {}'.format(provider_id, response))


def refresh_providers(provider_ids):
    """Refresh the specified providers with one request per provider via the REST API"""
    starttime = time.time()
    for provider in provider_ids:
        refresh_provider(provider)
    logger.debug('Queued Refresh {} Provider(s) in: {}s'.format(len(provider_ids),
        round(time.time() - starttime, 2)))


def refresh_providers_bulk(provider_ids):
    """Refresh the specified providers with one request via the REST API"""
    starttime = time.time()

    appliance = cfme_performance['appliance']['ip_address']
    resources = []
    for provider_id in provider_ids:
        resources.append({
            "href": "https://" + appliance + "/api/providers/" + str(provider_id)
        })

    data_dict = {
        "action": "refresh",
        "resources": resources
    }
    data_json = json.dumps(data_dict)
    response = requests.post("https://" + appliance + "/api/providers/",
                             data=data_json,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Queued Refresh {} Provider(s) in: {}s'.format(len(provider_ids),
        round(time.time() - starttime, 2)))


def refresh_provider_vm(vm_id):
    """Refresh the specified VM via the REST API"""
    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Queued Refresh VM: {}, Response: {}'.format(vm_id, response))


def refresh_provider_vms(vm_ids):
    """Refresh the specified VMs with one request per VM via the REST API"""
    starttime = time.time()
    for vm in vm_ids:
        refresh_provider_vm(vm)
    logger.debug('Queued Refresh {} VM(s) in: {}s'.format(len(vm_ids),
        round(time.time() - starttime, 2)))


def refresh_provider_vms_bulk(vm_ids):
    """Refresh the specified VMs with one request via the REST API"""
    starttime = time.time()

    appliance = cfme_performance['appliance']['ip_address']
    resources = []
    for vm_id in vm_ids:
        resources.append({
            "href": "https://" + appliance + "/api/vms/" + str(vm_id)
        })

    data_dict = {
        "action": "refresh",
        "resources": resources
    }
    data_json = json.dumps(data_dict)
    response = requests.post("https://" + appliance + "/api/vms/",
                             data=data_json,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Queued Refresh {} VM(s) in: {}s'.format(len(vm_ids),
        round(time.time() - starttime, 2)))


def provision_vm(vm_name, template_guid, vlan):
    """Create a provision request for a VM"""
    starttime = time.time()
    data_dict = {
        'action': 'create',
        'resources': [{
            'template_fields': {
                'guid': template_guid
            },
            'vm_fields': {
                'number_of_sockets': 1,
                'cores_per_socket': 1,
                'vm_name': vm_name,
                'vm_memory': '1024',
                'vlan': vlan,
                'vm_auto_start': True,
                'provision_type': 'native_clone'
            },
            'requester': {
                'user_name': 'admin',
                'owner_first_name': 'FirstName',
                'owner_last_name': 'LastName',
                'owner_email': 'alex@perf.com',
                'auto_approve': True
            },
            'additional_values': {
                'request_id': '1001'
            },

            'ems_custom_attributes': {},
            'miq_custom_attributes': {}
        }]
    }

    data_json = json.dumps(data_dict)
    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/provision_requests/",
                             data=data_json,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)
    logger.debug('Queued Provision VM {} in: {}s'.format(vm_name,
        round(time.time() - starttime, 2)))


def vm_exists(vm_id):
    """Returns true if and only if CFME recognizes the vm"""
    return vm_id in get_all_vm_ids()


def get_remaining_vms():
    remaining_vms = []
    for vm_id in get_all_vm_ids():
        details = get_vm_details(vm_id)
        if details['name'][:4] == '2016' and 'retirement_state' not in details:
            remaining_vms.append(details['name'])
    return remaining_vms


def retire_vm(vm_id):
    """Retire the specified VM via the REST API, Returns true if successful"""
    logger.debug('Retiring guest VM with ID: {}'.format(vm_id))
    if (not vm_exists(vm_id)):
        logger.warning('Attempted to Retire vm {}, which doesn\'t exist'.format(vm_id))
        return False

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "retire"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)
        return False

    logger.debug('Retired guest VM: {}, Response: {}'.format(vm_id, response))
    return True


def retire_provisioned_vm(vm_tuple):
    """Retires the Vm specified in the vm_tuple. Expects a the tuple to contain
    a VM name in index 0, and its provider in index 1. Returns True if successful"""
    starttime = time.time()
    vm_name, provider_name = vm_tuple
    logger.debug('Cleaning up: {}'.format(vm_name))
    vm_id = get_vm_id(vm_name)
    result = retire_vm(vm_id)
    if result:
        logger.debug('Queued retire for VM in {}s'.format(round(time.time() - starttime, 2)))
        return result
    else:
        logger.error('Could not delete VM: {}'.format(vm_name))
        return result


def retire_provisioned_vms(provision_order):
    """Attempts to retire all VMs in provision_order. Expects provision order to be a list
    of tuples VM name is in index 0, and its provider's name in index 1"""
    starttime = time.time()
    startsize = len(provision_order)

    for vm_tuple in provision_order[:]:
        if retire_provisioned_vm(vm_tuple):
            provision_order.remove(vm_tuple)

    logger.debug('Retired {} VMs in: {}s'.format(startsize - len(provision_order),
        round(time.time() - starttime, 2)))


def get_vm_provider(vm_name):
    """Returns the provider name of the Vm"""
    vm_id = get_vm_id(vm_name)
    vm_details = get_vm_details(vm_id)
    vm_type = vm_details['type']
    last_colon = vm_type.rfind('::')
    expected_provider_type = vm_type[:last_colon]
    for provider in get_all_provider_ids():
        details = get_provider_details(provider)
        if details['type'] == expected_provider_type:
            return details


def get_mgmt_provider_class(provider):
    if provider.type == 'ManageIQ::Providers::Vmware::InfraManager':
        return VMWareSystem(provider.ip_address,
                            provider.credentials.username,
                            provider.credentials.password)
    elif provider.type == 'ManageIQ::Providers::Redhat::InfraManager':
        return RHEVMSystem(provider.ip_address,
                           provider.credentials.username,
                           provider.credentials.password)


def delete_provisioned_vm(vm_tuple):
    """Deletes the Vm specified in the vm_tuple. Expects a the tuple to contain
    a VM name in index 0, and its provider in index 1. Returns True if successful"""
    vm_name, provider_name = vm_tuple
    logger.debug('Cleaning up: {}'.format(vm_name))
    provider_details = (cfme_performance['providers'][provider_name])
    provider = get_mgmt_provider_class(provider_details)
    try:
        provider.delete_vm(vm_name)
        return True
    except Exception as e:
        # VM potentially was not yet provisioned
        logger.error('Could not delete VM: {} Exception: {}'.format(vm_name, e))
        return False


def delete_provisioned_vms(provision_order):
    """Attempts to delete all VMs in provision_order. Expects provision order to be a list
    of tuples VM name is in index 0, and its provider's name in index 1"""
    starttime = time.time()
    startsize = len(provision_order)

    for vm_tuple in provision_order[:]:
        if delete_provisioned_vm(vm_tuple):
            provision_order.remove(vm_tuple)

    logger.debug('Deleted {} VMs in: {}s'.format(startsize - len(provision_order),
        round(time.time() - starttime, 2)))


def shutdown_vm_guest(vm_id):
    """Shut down the specified VM  via the REST API"""
    logger.vdebug('Shutting down guest VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "shutdown_guest"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Shutdown guest VM: {}, Response: {}'.format(vm_id, response))


def reboot_vm_guest(vm_id):
    """Reboot the specified VM  via the REST API"""
    logger.vdebug('Rebooting guest VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "reboot_guest"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Rebooted guest VM: {}, Response: {}'.format(vm_id, response))


def start_vm(vm_id):
    """Start the specified VM  via the REST API"""
    logger.vdebug('Starting VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "start"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Started VM: {}, Response: {}'.format(vm_id, response))


def stop_vm(vm_id):
    """Stop the specified VM  via the REST API"""
    logger.vdebug('Stopping VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "stop"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Stopped VM: {}, Response: {}'.format(vm_id, response))


def suspend_vm(vm_id):
    """Suspend the specified VM  via the REST API"""
    logger.vdebug('Suspending VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "suspend"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Suspended VM: {}, Response: {}'.format(vm_id, response))


def map_vms_to_ids(provider_names_to_vm_names):
    """Takes a dictionary of providers with a list of vms and generates a list of vm_ids for each
    vm in the data structure.  We need this because more than one provider can lead to a """
    starttime = time.time()
    expected_num_ids = sum(len(x) for x in provider_names_to_vm_names.itervalues())
    expected_num_providers = len(provider_names_to_vm_names.keys())
    # Intended ouput here (List of vm ids):
    vm_ids = []
    # Intermediate data structure holding provider_id to list of vm names
    provider_ids_to_vm_names = {}

    # First get all providers details
    all_providers_details = []
    for pro_id in get_all_provider_ids():
        details = get_provider_details(pro_id)
        all_providers_details.append(details)

    providers_to_vms_copy = dict(provider_names_to_vm_names)
    # Next map provider_name to the provider_id
    for provider_name in provider_names_to_vm_names:
        for provider_detail in all_providers_details:
            if provider_name == provider_detail['name']:
                # Copy VMs from that provider to the Intermediate data structure
                provider_ids_to_vm_names[provider_detail['id']] = list(
                    provider_names_to_vm_names[provider_name])
                del providers_to_vms_copy[provider_name]
                break

    if len(providers_to_vms_copy) > 0:
        # Error, we did not find all providers, likely there is an issue with the scenario data
        # inside of cfme_performance.yml or cfme_performance.local.yml
        logger.error('Provider(s) + vm(s) not found in CFME Inventory: {}'.format(
            providers_to_vms_copy))

    provider_ids_to_vm_names_copy = copy.deepcopy(provider_ids_to_vm_names)
    # Now map each vm_name+ems_id to the actual vm_id and append to our list
    for vm_id in get_all_vm_ids():
        vm_details = get_vm_details(vm_id)
        for provider_id in provider_ids_to_vm_names:
            if ('ems_id' in vm_details and provider_id == vm_details['ems_id']):
                # Match provider_id, now check vm_name
                for vm_name in provider_ids_to_vm_names[provider_id]:
                    if vm_name == vm_details['name']:
                        logger.debug('Matching {} to vm id: {}'.format(vm_name, vm_id))
                        vm_ids.append(vm_id)
                        del (provider_ids_to_vm_names_copy[provider_id]
                            [provider_ids_to_vm_names_copy[provider_id].index(vm_name)])
                        break
        if (sum(len(x) for x in provider_ids_to_vm_names_copy.itervalues()) == 0):
            break

    # Now check for left over vms that we did not match:
    leftover_num_ids = sum(len(x) for x in provider_ids_to_vm_names_copy.itervalues())
    if leftover_num_ids > 0:
        logger.error('(Provider_id(s)) + VM(s) not found in CFME inventory: {}'.format(
            provider_ids_to_vm_names_copy))
    logger.debug('Mapped {}/{} vm ids/names over {}/{} provider ids/names in {}s'.format(
        len(vm_ids), expected_num_ids, len(provider_ids_to_vm_names.keys()), expected_num_providers,
        round(time.time() - starttime, 2)))
    return vm_ids


def reset_vm(vm_id):
    """Reset the specified VM via the REST API"""
    logger.vdebug('Reseting VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "reset"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Reset VM: {}, Response: {}'.format(vm_id, response))
