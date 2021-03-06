"""Runs Idle Workload by resetting appliance and idling with no providers."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_workload_idle_default
from utils.appliance import wait_for_miq_server_workers_started
from utils.conf import cfme_performance
from utils.grafana import get_default_dashboard_url
from utils.log import logger
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.smem_memory_monitor import add_workload_quantifiers
from utils.ssh import SSHClient
import time
import pytest


@pytest.mark.usefixtures('generate_version_files')
def test_idle_default(request):
    """Runs an appliance at idle for specific amount of time. Memory Monitor creates graphs and
    summary at the end of the scenario."""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()

    clean_appliance(ssh_client)

    quantifiers = {}
    scenario_data = {'appliance_ip': cfme_performance['appliance']['ip_address'],
        'appliance_name': cfme_performance['appliance']['appliance_name'],
        'test_dir': 'workload-idle',
        'test_name': 'Idle with Default Roles',
        'appliance_roles': get_server_roles_workload_idle_default(separator=', '),
        'scenario': {'name': 'default'}}
    monitor_thread = SmemMemoryMonitor(SSHClient(), scenario_data)

    def cleanup_workload(from_ts, quantifiers, scenario_data):
        starttime = time.time()
        to_ts = int(starttime * 1000)
        g_url = get_default_dashboard_url(from_ts, to_ts)
        logger.debug('Started cleaning up monitoring thread.')
        monitor_thread.grafana_url = g_url
        monitor_thread.signal = False
        monitor_thread.join()
        add_workload_quantifiers(quantifiers, scenario_data)
        timediff = time.time() - starttime
        logger.info('Finished cleaning up monitoring thread in {}'.format(timediff))
    request.addfinalizer(lambda: cleanup_workload(from_ts, quantifiers, scenario_data))

    monitor_thread.start()

    wait_for_miq_server_workers_started(poll_interval=2)
    # No need to set server roles as we are using the default set of roles

    s_time = cfme_performance['workloads']['test_idle_default']['total_time']
    logger.info('Idling appliance for {}s'.format(s_time))
    time.sleep(s_time)

    quantifiers['Elapsed_Time'] = s_time
    logger.info('Test Ending...')
