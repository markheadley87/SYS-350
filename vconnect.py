# Requirement 1

import getpass
from pyVim.connect import SmartConnect
from pyVmomi import vim 
import ssl
import json

s=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
s.verify_model=ssl.CERT_NONE

def read_json_config(file_path): # Creates a method to read through a file
    config = {}
    with open(file_path, 'r') as file: # Opens the file (that we called earlier) in read mode, 
        config = json.load(file) # Loads the json file called below
    return config['vcenter'][0] # Returns the first item in the array
    
config = read_json_config("vcenter-conf.json") # Runs the function with the vcenter-conf.json file
vcenter_host = config['vcenterhost'] # Creates an object from the function
vcenter_user = config['vcenteradmin'] # Creates another object from the function

print("======================")
print("List VCenter host and login account:")
print(vcenter_host) # Prints results of the file retrieval
print(vcenter_user) # Prints results of file retrieval 
print("======================")
print("Login to VCenter here:")

# Requirement 2
passw = getpass.getpass() # Collect password securely
si=SmartConnect(host=vcenter_host, user=vcenter_user, pwd=passw, sslContext=s) # Connect using password, username, and vcenter host
aboutInfo=si.content.about # Create a variable to call information about the VCenter server
session_manager = si.content.sessionManager # Create variable to call information about the session manager
current_session = session_manager.currentSession # Create a variable to call information about the current session

# Print outputs
print("Connected as: ", current_session.userName)
print("Source IP Address is: ", current_session.ipAddress)
print("VCenter Server: ", vcenter_host)
print("VCenter Version: ", aboutInfo.fullName)

# Requirement 3
def get_vm_by_name(content, vm_name = None): # Creates a function to get VM by name
    vm_list = [] # Creates an array to store VM data
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True) # Passes VCenter container data to a variable we can call
    for vm in container.view: # Creates a loop to iterate through all the VMs in the container
        if vm_name is None or vm_name.lower() in vm.name.lower(): # Checks if an input is given, then converts the input (if there is one) into lowercase then checks if that VM exists
            vm_list.append(vm) # Adds the to the end of the array
    container.Destroy # Cleans up the container we opened
    return vm_list # Stores the data into the array

vms = get_vm_by_name(si.content, vm_name=None) # Creates a default variable to search for VMs, this allows no input to be given later, and it will bring up all VM data
print("======================")
print("Enter a VM name: ")
vm_to_search = input("Search for a VM name: ") # Takes user input to search for a VM
found_vms = get_vm_by_name(si.content, vm_name=vm_to_search) # Searches through VCenters MOB content page for the VM from the loop before
if found_vms: # If statement to check if the VM name was found in the array
    for vm in found_vms: # Runs as a result of the VM Name being found, this also runs with "None" to list all VMs
        print("VM Found!: ", vm.name)
else: # Runs if VM name is not found
    print("VM Name does not exist...")


# Requirement 4
def get_info(vm): # Create a function to get VM data
    summary = vm.summary # Creates an easy to call variable for VM summary data
    name = summary.config.name # Collects VM name
    power_state = summary.runtime.powerState # Collects if the VM is on or off
    num_cpus = summary.config.numCpu # Num CPUs allocated
    memory = summary.config.memorySizeMB # Memory allocated
    ip = summary.guest.ipAddress # IP address of the VM

    return { # Returns all the data to be called upon later
        "name": name,
        "power_state": power_state,
        "num_cpus": num_cpus,
        "memory": memory,
        "ip": ip,

    }

# Print data for searched VM
for vm in found_vms: # For loop to use the name in requirement 3 to gather data about the VM
    info = get_info(vm) # Creating a variable to call the get_info function for the data, while passing the VM name from requirement 3
    print(f"VM Name: {info['name']}") # Prints VM data
    print(f"VM Power: {info['power_state']}")
    print(f"CPUS: {info['num_cpus']}")
    print(f"Memory: {info['memory']}")
    print(f"IP: {info['ip']}")
