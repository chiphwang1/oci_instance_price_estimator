"""
This module will run Terrform plan and get the output in JSON format. 
It will search for all "oci_core_instance" resources and return a list with shape and shape_config
"""

import subprocess
import json
import os
import sys
from colorama import Fore, Style
import argparse
from python_terraform import *


def run_terraform_plan(path):
    """
    run terraform plan and create JSON ouput in current directory
    """
    print(f"{Fore.GREEN}Create Terraform Plan JSON FIle...{Style.RESET_ALL} ")
    current_directory = subprocess.getoutput("pwd")
    terraform_plan_file = current_directory + "/" + "plan_output"
    
    # create working directory for Terrafom Plan
    print(f"{Fore.BLUE}Create Workspace Directory ...{Style.RESET_ALL} ")
    subprocess.getoutput('mkdir ./workspace')

    # copy terrafrom directory over to working directory
    print(f"{Fore.BLUE}Copy Terraform Stack ...{Style.RESET_ALL} ")
    subprocess.getoutput('cp -rf {}/* ./workspace'.format(path))

    # remove TF statefiles from ./workspace
    print(f"{Fore.BLUE}Remove TF state files ...{Style.RESET_ALL} ")
    subprocess.getoutput('rm -rf ./workspace/*tfstate*')

    # run terraform init on ./workspace
    print(f"{Fore.BLUE}Run Terraform init ...{Style.RESET_ALL} ")
    terraform_plan = subprocess.getoutput("terraform -chdir=./workspace init")

    # check if required variables are set in Terraform if not exit
    print(f"{Fore.BLUE}Check if required variables are set ...{Style.RESET_ALL} ")
    exit_script = False
    tf = Terraform(working_dir='./workspace')
    output = tf.plan(no_color=IsFlagged, refresh=False)
    for line in output:
        if type(line) == str:
            if 'Error:' in line:
                print(line)
                exit_script = True
    if exit_script == True:
        print(f"{Fore.GREEN}Required Variables Not set Please set Variables to Continue...{Style.RESET_ALL} ")
        sys.exit()


    # run Terraform Plan
    print(f"{Fore.BLUE}Create Terraform Plan JSON output ...{Style.RESET_ALL} ")
    terraform_plan = subprocess.getoutput("terraform -chdir=./workspace plan -out=plan_output")
    if 'Error' in terraform_plan:
        print(terraform_plan)
        sys.exit()
    
    
    # convert Tearrform plan output to JSON and save to local directory
    subprocess.getoutput("terraform -chdir=./workspace show -json plan_output > ./plan.json")
    
    # remove ./workspace directory
    subprocess.getoutput('rm -rf ./workspace')

def convert_terraform_plan_to_dict():
    """
    convert plan.json to dictionary
    and get resource_changes list from JSON outout
    resource_changes list is list of changes to be applied in Terraform
    """
    print(f"{Fore.GREEN}Convert Terraform Plan JSON output to dictionary...{Style.RESET_ALL} ")
    # Opening JSON file
    with open('./plan.json') as json_file:
        data = json.load(json_file)
        # Print the type of data variable
        return data['resource_changes']

def find_instances(resource_changes_list):
    """
    search in resource_changes_list for oci_core_instances
    """
    print(f"{Fore.GREEN}Find all OCI instances...{Style.RESET_ALL} ")
    instance_list = []
    for resource in resource_changes_list:
        instance_dict = {}
        if resource['type'] == 'oci_core_instance':
            instance_dict['name'] = resource['name']           
            instance_dict['shape'] = resource['change']['after']['shape']
            instance_dict['config'] = resource['change']['after']['shape_config']
            instance_list.append(instance_dict)
    return(instance_list)
        



def main():
    """
    namespace: namespace where AutonmousDB resource is created
    secret_name: define in values.yaml wallet.walletName
    path: path to write wallet files
    """
    path = sys.argv[1]
    run_terraform_plan(path)
    resource_changes_list = convert_terraform_plan_to_dict()
    instance_list = find_instances(resource_changes_list)
    
    


    


if __name__ == "__main__":
    main()