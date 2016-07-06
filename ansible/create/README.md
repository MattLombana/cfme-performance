# Create

Playbooks used to create Virtual Machines and VM Simulators used for CFME Testing. All playbooks are run on the local host, bypassing Ansible's ssh features. hosts.local can be specified, but is not required.

**Table of Contents**
========
- [Playbooks](#playbooks)
<<<<<<< 2a89532642499d1c9153f9b94c68a18147f4c731
  - [create-cfme-appliance.yml](#create-cfme-applianceyml)
=======
  - [create-workload-VM.yml](#create-workload-VMyml)
  - [create-test-VM.yml](#create-test-VMyml)
  - [create-simulator.yml](#create-simulatoryml)
>>>>>>> Add initial playbooks, README, and base files for future playbooks

# Playbooks

## create-cfme-appliance.yml

```
[root@perf ansible]# ansible-playbook create/create-cfme-appliance.yml
```
Provisions VMs based on configurable settings in all.local.yml. After prvisioning these VMs are ready to have a configure playbook run against them.
