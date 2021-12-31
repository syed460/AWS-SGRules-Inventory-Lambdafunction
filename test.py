#!/bin/python3

import json, csv
import boto3
from pprint import pprint
from datetime import datetime, timedelta
import subprocess, os

#def lambda_handler(event, context):
print("---------------Script Starts-------------")
print("")

#------------------Environmental Variable (4)-------------

Bucket_region = os.getenv("Bucket_region")
Bucket_Name = os.getenv("Bucket_Name")
#filename= os.getenv("filename")
filename= "test_filename"
prefix_in_bucket=os.getenv("prefix_in_bucket") 

#----------------------------------------
#defining file name
def date_on_filename(filename, file_extension):  
    date = str(datetime.now().date())
    return filename + "-" + date + "." + file_extension

report_filename = date_on_filename(filename, "csv")
print(f"output file name: {report_filename}")

#local file path
filepath= "/tmp/" + report_filename
print(f"Output File Patch {filepath}")
print("")

#Collecting Account Number
sts_cli=boto3.client(service_name='sts', region_name="us-east-1")
responce_1=sts_cli.get_caller_identity()
account_number=responce_1.get("Account")
#--------------------------------------------

#--------------Manually update the dic.keys() to header_list if mismatch

header_list=['Account', 'Region', 'VPC-ID', 'VPC-Name', 'SG-ID', 'SG-Name', 'SG-Description', 'FromPort', 'ToPort', \
    'Protocol','IpRanges','Rule-Description','Rule Type']
 
print(f"Header for CSV file = {header_list}")
print(" ")
# to add 50 Tag headers
'''
for v in range(1,51):
    header_list.append(f'Tag{v}')
'''
#-----------collect all region list into Regions
print("collecting all the regions name")

ec2_cli = boto3.client(service_name='ec2', region_name="us-east-1")    
responce=ec2_cli.describe_regions()
#pprint(responce['Regions'])

Regions=[]
for each in responce['Regions']:
    #print(each['RegionName'])
    Regions.append(each['RegionName'])    
print(f"Total {len(Regions)} regions")
print("")

# Regions=['us-east-1']
x=1 

#===================
#----------creating file with headder

print("Oppening the csv file to append each server details")
with open(filepath,'w') as csv_file:
#with open("outpu.csv",'w') as csv_file:
    Writer=csv.writer(csv_file)
    Writer.writerow(header_list)
    
    print("Now going through each regions to check requred details")
    
    for region in Regions:
        print(f'============ Region: {region}')
        print("")
        #print(type(region))
        ec2_cli=boto3.client(service_name='ec2', region_name=region)
        #describe_security_group_rules()
        #describe_security_groups()
        all_SG=ec2_cli.describe_security_groups()
        #pprint()
        for SG in all_SG['SecurityGroups']:
            dic = {'Account':account_number,'Region':region,'VPC-ID':'NA','VPC-Name':'NA','SG-ID':'NA','SG-Name':'NA',
            'SG-Description':'NA',
            'FromPort':'NA','ToPort':'NA','Protocol':'NA','IpRanges':'NA','Rule-Description':'NA','Rule Type':'NA'}
            #pprint(SG)
            
            dic['SG-Name']=SG['GroupName']
            dic['SG-ID'] = SG['GroupId']
            dic['SG-Description'] = SG['Description']
            dic['VPC-ID'] = SG['VpcId']
            #print the outbound rules

            for r in SG['IpPermissionsEgress']:
                dic['Rule Type']= 'Inbound'
                #print(r)
                if r.get('FromPort') != None:
                    dic['FromPort'] = r['FromPort']
                dic['Protocol'] = r['IpProtocol']
                if r.get('ToPort') != None:
                    dic['ToPort'] = r['ToPort']
                for each in r['IpRanges']:
                    #print(each)
                    dic['IpRanges']=each['CidrIp']
                    if each.get('Description') != None:
                        dic['Rule-Description']=each['Description']
                #now print the full value
                #print(dic.keys())
                #print(dic.values())
                print(" ")
                Writer.writerow(dic.values())
                print(f"------Rule {x} details been taken\n")
                x=x+1

            for ingress_rule in SG['IpPermissions']:
                dic['Rule Type']= 'Outbound'
                #print(ingress_rule)
                
                #clearing the variables
                dic['FromPort']='NA'
                dic['Protocol']='NA'
                dic['ToPort']='NA'
                dic['IpRanges']='NA'
                dic['Rule-Description']='NA'

                if ingress_rule.get('FromPort') != None:
                    dic['FromPort'] = ingress_rule['FromPort']
                dic['Protocol'] = ingress_rule['IpProtocol']
                if ingress_rule.get('ToPort') != None:
                    dic['ToPort'] = ingress_rule['ToPort']
                for each in ingress_rule['IpRanges']:
                    #print(each)
                    dic['IpRanges']=each['CidrIp']
                    if each.get('Description') != None:
                        dic['Rule-Description']=each['Description']
                #now print the full value
                #print(dic.keys())
                #print(dic.values())
                print(" ")
                Writer.writerow(dic.values())
                print(f"------Rule {x} details been taken\n")
                x=x+1                

