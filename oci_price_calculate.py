"""
This module will
"""

import csv
import requests
import json
import pprint
import sys
import argparse
from urllib.request import urlopen
from colorama import Fore, Style
from create_shape_price_mapping import *
from create_terrafrom_plan_json import *
from python_terraform import *


def create_list_for_instances(instance_list, updated_price):

    """
    This function will create a list for all VM shapes in the Terraform plan and will add cost for CPU, memory,
    virtual machine and number of CPU and memory to the list 
    """

    instances_process_list=[]
    print(f"{Fore.GREEN}Calculate cost per instance...{Style.RESET_ALL} ")
    for instance in instance_list:
        instance_dict= {}
        shape = instance['shape']
        
        virtual_machine_count = 1
        virtual_machine_cost =  updated_price[shape].get('virtual machine USD')

        if virtual_machine_cost == None:
            virtual_machine_cost = 0

        CPU_cost = updated_price[shape].get('CPU USD')
        
        if CPU_cost == None:
            CPU_cost = 0
        
        memory_cost = updated_price[shape].get('memory USD')
        
        if memory_cost == None:
            memory_cost = 0
       
        CPU_count = instance['config'][0].get('ocpus')

        if CPU_count == None:
            CPU_count = 0

        memory_count = instance['config'][0].get('memory_in_gbs')
        
        if memory_count == None:
             memory_count = 0
        
        instance_dict= { 'name' : instance['name'], 
                        'shape' : instance['shape'], 
                        'virtual_machine_count' : virtual_machine_count,
                        'virtual_machine_cost' : virtual_machine_cost,
                        'CPU_cost' : CPU_cost,
                        'memory_cost' : memory_cost,
                        'CPU_count': CPU_count,
                        'memory_count': memory_count,
                        'total_memory_cost' : memory_count * memory_cost,
                        'total_CPU_cost' : CPU_count * CPU_cost,
                        'total_vm_cost' : virtual_machine_count * virtual_machine_cost }
        
        instances_process_list.append(instance_dict)
    return instances_process_list
        
    
def calculate_cost(vm_process_list):
    pp = pprint.PrettyPrinter(depth=6)
    total_cost_vm_list =[]
    print(f"{Fore.GREEN}Ouptut Cost...{Style.RESET_ALL} ")

    print(f"-------------------------------------------------------------------------------------------")
    for vm in vm_process_list:
        shape = vm['shape']
        cpu_cost = vm['CPU_cost']
        cpu_count = vm['CPU_count']
        memory_cost = vm['memory_cost']
        memory_count = vm['memory_count']
        virtual_vm_cost = vm['total_vm_cost']
        cpu_total = cpu_cost * cpu_count
        memory_total = memory_cost * memory_count
        total_cost = virtual_vm_cost + cpu_total + memory_total
       
        print(f"{Fore.GREEN}Instance: {vm['name']}{Style.RESET_ALL}" ) 
        print (f"shape: {vm['shape']}" )
        print(f"virtual machine cost: {str(virtual_vm_cost)}" )
        print(f"CPU Count: {str(cpu_count)} CPU cost:  {str(cpu_cost)} CPU total cost: {str(cpu_total)}  " )
        print(f"Memory Count: {str(memory_count)} Memory cost:  {str(memory_cost)} Memory total cost: {str(memory_total)}  " )
        print(f"Total cost for Instance:  {total_cost:.4f}  " )
        print(f"")
        total_cost_vm_list.append(total_cost)
    
    total_instance_cost = sum(total_cost_vm_list)
    print(f"{Fore.GREEN}Total cost for instances in Terraform stack is: {total_instance_cost:.4f} per hour {Style.RESET_ALL} ")


def cli():
    # Create the parser
    my_parser = argparse.ArgumentParser(description='calculate OCI pricing for instances in a Terraform Stack',
                                        prog='oci_price_calculate',
                                        usage='%(prog)s [options] path',
                                        epilog='Enjoy the program from OCI Teach Marketing! :)')

    # Add the arguments
    my_parser.add_argument('Path',
                       metavar='path',
                       type=str,
                       help='the path to the Terraform Stack')
    args = my_parser.parse_args()
    
    input_path = args.Path

    if not os.path.isdir(input_path):
        print('The path specified does not exist')
        sys.exit()
    
    return args.Path



def main():
    """
    file1: local csv file in same directory for mapping OCI shape to OCI partnumbers
    uri: URL for OCI pricing list
    path: path to directory of Terrafrom stack
    """

    file1 = "./shape.csv"
    uri = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/"
    # path = sys.argv[1]
    path =  cli()

    
    
    # create JSON output for Terraform plan and returns list of  "oci_core_instance"
    run_terraform_plan(path)
    resource_changes_list = convert_terraform_plan_to_dict()
   
    
    # list of  "oci_core_instance" resources
    instance_list = find_instances(resource_changes_list)

   
    # create OCI shape to Part number Dictionary and File
    price_dict = get_oci_price_list(uri)
    vm_price = read_parts_list(file1)
    
    updated_price = append_vm_price(vm_price, price_dict)
    
    # create OCI shape to Part number write to file
    write_vm_price_to_file(updated_price)

    vm_process_list = create_list_for_instances(instance_list, updated_price)
    calculate_cost(vm_process_list)




if __name__ == "__main__":
    main()
