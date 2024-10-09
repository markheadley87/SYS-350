from time import sleep
import vconnect
from pyVim.connect import Disconnect
from pyVmomi import vim

def menu():
    print("[1] VCenter Info")
    print("[2] Session Details")
    print("[3] VM Details")
    print("[4] Perform VM Actions")
    print("[0] Exit")

def vmmenu():
    print("[1] Power on VM")
    print("[2] Power off VM")
    print("[3] Take a Snapshot")
    print("[4] Delete a VM")
    print("[5] Reconfigure a VM")
    print("[6] Rename a VM")
    print("[0] Back")

def main():
    # This ensures the vCenter connection is established first using vconnect
    vconnect.config = vconnect.read_json_config("vcenter-conf.json")
    vconnect.vcenter_host = vconnect.config['vcenterhost']
    vconnect.vcenter_user = vconnect.config['vcenteradmin']

    passw = vconnect.getpass.getpass()  # Collect password securely
    vconnect.si = vconnect.SmartConnect(host=vconnect.vcenter_host, user=vconnect.vcenter_user, pwd=passw, sslContext=vconnect.s)

    menu()
    option = int(input("Enter your selection: "))

    while option != 0:
        match option:
            case 1:
                # Display vCenter Info
                print("VCenter Info: ")
                about_info = vconnect.si.content.about
                print(f"VCenter Server: {about_info.fullName}")
                print(f"VCenter Version: {about_info.version}")
                print(f"Build Number: {about_info.build}")
                print(f"OS Type: {about_info.osType}")
            
            case 2:
                # Display Session Details
                print("Session Details:")
                session_manager = vconnect.si.content.sessionManager
                current_session = session_manager.currentSession
                print(f"Connected as: {current_session.userName}")
                print(f"Source IP Address: {current_session.ipAddress}")

            case 3:
                # List VM Details
                print("VM Details:")
                vm_to_search = input("Enter VM name to search (or leave blank to list all VMs): ")
                found_vms = vconnect.get_vm_by_name(vconnect.si.content, vm_name=vm_to_search)
                if found_vms:
                    for vm in found_vms:
                        info = vconnect.get_info(vm)
                        print(f"VM Name: {info['name']}")
                        print(f"Power State: {info['power_state']}")
                        print(f"CPUs: {info['num_cpus']}")
                        print(f"Memory: {info['memory']} MB")
                        print(f"IP Address: {info['ip']}")
                else:
                    print("No VMs found matching the criteria.")

            case 4:
                # Perform VM Actions (Enter VM Action menu)
                vmmenu()
                vm_action = int(input("Enter VM action: "))
                if vm_action == 0:
                    menu()  # Return to main menu
                else:
                    # Implement VM action functions (e.g., power on/off VM, take snapshot, etc.)
                    vm_to_search = input("Enter VM name to perform action on: ")
                    found_vms = vconnect.get_vm_by_name(vconnect.si.content, vm_name=vm_to_search)
                    if found_vms:
                        vm = found_vms[0]  # Assuming only one VM found, adjust as necessary
                        match vm_action:
                            case 1:
                                # Power on VM
                                if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:
                                    vm.PowerOn()
                                    print(f"Powering on VM: {vm.name}")
                                else:
                                    print("VM is already powered on.")
                            
                            case 2:
                                # Power off VM
                                if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
                                    vm.PowerOff()
                                    print(f"Powering off VM: {vm.name}")
                                else:
                                    print("VM is already powered off.")
                            
                            case 3:
                                # Snapshot VM
                                snapshot_name = input("What name would you like to name the snapshot?: ")
                                desc = input("Input a description: ")
                                memory_check = input("Would you like to snapshot memory?: (True/False)")
                                silent_snap = input("Would you like to silently snapshot?: (True/False)")
                                vm.CreateSnapshot(snapshot_name, desc, bool(memory_check), bool(silent_snap))
                            
                            case 4: 
                                # Delete VM
                                vm.Delete()
                            
                            case 5:
                                # Reconfigure a VM
                                def reconfigure_vm(vm, new_cpu_count=None, new_memory_size=None):
                                    spec = vim.vm.ConfigSpec()  # Create a new config spec for VM reconfiguration
                                    spec.numCPUs = int(input("How many CPUs do you want to give the VM? "))
                                    spec.memoryMB = int(input("What amount of memory would you like to change to?: (MB)"))
                                    if new_cpu_count is not None:
                                        spec.numCPUs = new_cpu_count  # Set the new number of CPUs
                                    if new_memory_size is not None:
                                        spec.memoryMB = new_memory_size  # Set the new memory size in MB
                                    # Reconfiguring the VM with the new spec
                                    print(f"Reconfiguring VM: {vm.name}")
                                    vm.ReconfigVM_Task(spec = spec)
                                reconfigure_vm(vm)
                                
                            
                            case 6:
                                # Rename a VM
                                name = input("What would you like to rename the VM to?: ")
                                vm.Rename(name)

                    else:
                            print("VM action canceled.")

        option = int(input("Enter your selection: "))  # Prompt for input again after each action

if __name__ == "__main__": # Chat GPT 
    try:
        main()
    finally:
        # Always disconnect from vCenter when done
        if 'si' in locals() and vconnect.si:
            Disconnect(vconnect.si)
