from utils.conf import cfme_performance
from utils.log import logger
import json
import requests


def add_provider(provider):
    """Adds Provider via the Rest API."""
    logger.debug('Adding Provider: {}, Type: {}'.format(provider['name'],
                                                        provider['type']))

    if (provider['type'] == 'ManageIQ::Providers::Redhat::InfraManager'):
        json_data = json.dumps({
            "action": "create",
            "resources": [{
                "name": provider['name'],
                "type": provider['type'],
                "hostname": provider['ip_address'],
                "credentials": [{
                    "userid": provider['credentials']['username'],
                    "password": provider['credentials']['password']
                },
                  {
                    "userid": provider['metrics_credentials']['username'],
                    "password": provider['metrics_credentials']['password'],
                    "auth_type": "metrics"
                }]
            }]
        })
    else:
        json_data = json.dumps({
            "action": "create",
            "resources": [{
                "name": provider['name'],
                "type": provider['type'],
                "hostname": provider['ip_address'],
                "credentials": {
                    "userid": provider['credentials']['username'],
                    "password": provider['credentials']['password']
                    }
                }]
            })

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/providers",
                             data=json_data,
                             auth=(cfme_performance['appliance']['rest_api']['\
username'], cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('The response for adding Provider: {}, Type: {}, is: {}\
    '.format(provider['name'], provider['type'], response))


def add_providers(providers):
    for provider in providers:
        add_provider(cfme_performance['providers'][provider])


def refresh_provider(provider):
    logger.debug('Refreshing Provider: {}'.format(provider['name']))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/providers/105",
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['\
username'], cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('The response for refreshing Provider: {}, Type: {}, is: {}\
    '.format(provider['name'], provider['type'], response))


def refresh_provider_host(provider):
    logger.debug('TODO: Initiate Provider Host Refresh')


def refresh_provider_vm(provider):
    logger.debug('Refreshing Provider VM: {}'.format(provider['name']))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms",
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['\
username'], cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('The response for refreshing Provider VM: {}, Type: {}, is: {}\
    '.format(provider['name'], provider['type'], response))
