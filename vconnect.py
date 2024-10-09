import getpass
from pyVim.connect import SmartConnect
from pyVmomi import vim
import ssl
import json

s = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
s.verify_mode = ssl.CERT_NONE

def read_json_config(file_path):
    config = {}
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config['vcenter'][0]

def get_vm_by_name(content, vm_name=None):
    vm_list = []
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
    for vm in container.view:
        if vm_name is None or vm_name.lower() in vm.name.lower():
            vm_list.append(vm)
    container.Destroy()
    return vm_list

def get_info(vm):
    summary = vm.summary
    name = summary.config.name
    power_state = summary.runtime.powerState
    num_cpus = summary.config.numCpu
    memory = summary.config.memorySizeMB
    ip = summary.guest.ipAddress

    return {
        "name": name,
        "power_state": power_state,
        "num_cpus": num_cpus,
        "memory": memory,
        "ip": ip,
    }

if __name__ == "__main__":
    config = read_json_config("vcenter-conf.json")
    vcenter_host = config['vcenterhost']
    vcenter_user = config['vcenteradmin']

    print("======================")
    print("List VCenter host and login account:")
    print(vcenter_host)
    print(vcenter_user)
    print("======================")
    print("Login to VCenter here:")

    passw = getpass.getpass()
    si = SmartConnect(host=vcenter_host, user=vcenter_user, pwd=passw, sslContext=s)
    aboutInfo = si.content.about
    session_manager = si.content.sessionManager
    current_session = session_manager.currentSession

    print("Connected as: ", current_session.userName)
    print("Source IP Address is: ", current_session.ipAddress)
    print("VCenter Server: ", vcenter_host)
    print("VCenter Version: ", aboutInfo.fullName)

    vms = get_vm_by_name(si.content)
    print("======================")
    print("Enter a VM name: ")

    vm_to_search = input("Search for a VM name: ")
    found_vms = get_vm_by_name(si.content, vm_name=vm_to_search)

    if found_vms:
        for vm in found_vms:
            print("VM Found!: ", vm.name)
    else:
        print("VM Name does not exist...")

    for vm in found_vms:
        info = get_info(vm)
        print(f"VM Name: {info['name']}")
        print(f"VM Power: {info['power_state']}")
        print(f"CPUS: {info['num_cpus']}")
        print(f"Memory: {info['memory']}")
        print(f"IP: {info['ip']}")
