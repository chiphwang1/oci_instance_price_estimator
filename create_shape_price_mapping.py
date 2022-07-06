"""
This module will read a locl file "shape.csv" for mapping of OCI shape to OCI part numbers.
It will retrives OCI pricing list for part and map price to OCI shapes and output a file and dictionary with the mapping
"""

import csv
import requests
import json
from urllib.request import urlopen
from colorama import Fore, Style


def get_oci_price_list(uri):
    
    """
    API call to retreive pricing list form OCI. data_json is the dictionary with the price list 
    that is returned. price_data.json is the output written to file
    uri = url for downloading OCI proce list
    """
    print(f"{Fore.GREEN}Retrieving OCI Price List for Parts...{Style.RESET_ALL} ")
    response = urlopen(uri)
    price_json = json.loads(response.read())
    with open('price_data.json', 'w') as outfile:
        json.dump(price_json, outfile)
    
    return price_json


def read_parts_list(map_csv_file):
    
    """
    Read CSV for mapping OCI shapes to OCI part numbers and returns a dictionary
    map_csv_file = csv file for  OCI shapes to OCI part numbers mapping
    """    
    print(f"{Fore.GREEN}Retrieving local shape to parts file...{Style.RESET_ALL} ")
    vm_price_dict = {}
    with open(map_csv_file, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            vm_price_dict[row['shape']] = dict(row)
    
    return vm_price_dict

def append_vm_price(vm_price,price_dict):
    
    """
    Takes dictionary for OCI shapes to OCI part and appends pricing for memory, CPU and virtual for all currencies
    based on matching part number and adds to the dictionary and returns the dictionary
    vm_price = dictionary with OCI shapes to OCI part mapping
    price_dict = dictionary with OCI pricing
    """  
    print(f"{Fore.GREEN}Create mapping of shape to Parts...{Style.RESET_ALL} ")
    for k,v in vm_price.items():
        for part in price_dict['items']:
            if  part['partNumber'] == v['CPU part number']:
                for currency in part['currencyCodeLocalizations']:
                    vm_price[k]["CPU " + currency['currencyCode']] = currency['prices'][0]['value']

            if  part['partNumber'] == v['memory part number']:
                for currency in part['currencyCodeLocalizations']:
                    vm_price[k]["memory " + currency['currencyCode']] = currency['prices'][0]['value']
            
            if  part['partNumber'] == v['virtual machine part number']:
                for currency in part['currencyCodeLocalizations']:
                    vm_price[k]["virual machine " + currency['currencyCode']] = currency['prices'][0]['value']

    return vm_price



def write_vm_price_to_file(vm_price):
    
    """
    Writes updated OCI shapes file with mapping of part number to prices 
    vm_price = dictionary with prices to shape and parts mapping
    """  

    vm_list = []
    csv_columns = []
    for k,v in vm_price.items():
        vm_list.append(v)
        csv_columns.append(k)
   

    try:
        with open('vm_price.csv','w', encoding='utf8', newline='') as output_file:
            fc = csv.DictWriter(output_file, fieldnames=vm_list[0].keys(),)
            fc.writeheader()
            fc.writerows(vm_list)
          
    except IOError:
        print("I/O error")


def main():
    file1 = "./shape.csv"
    uri = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/"
    
    price_dict = get_oci_price_list(uri)
    vm_price = read_parts_list(file1)
    updated_price = append_vm_price(vm_price, price_dict)
    write_vm_price_to_file(updated_price)





if __name__ == "__main__":
    main()