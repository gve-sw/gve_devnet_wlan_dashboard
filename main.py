""" Copyright (c) 2021 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

from flask import Flask, render_template, request
import requests
import meraki
import config
import xlrd
import pandas as pd



api_key = config.api_key

app = Flask(__name__)


dashboard = meraki.DashboardAPI(api_key=api_key, print_console=True,output_log=False)

@app.route('/')
def usage():

    values = []
    labels = []
    total = {"aps":0,"clients":0,"fiveghz":0,"twoghz":0,"laptops":0,"phones":0}
    greatest_clients = 0
    network_greatest_clients = ""
    month_in_seconds = 2.678e+6
    networks = []

    response = dashboard.organizations.getOrganizationNetworks(organizationId=config.meraki_org_id,total_pages="all")

    # retrieving the name and id for each network within the org
    for network in response:
        item = {}
        
        item["id"] = network["id"]
        item["name"] = network["name"]
        
        networks.append(item)
        

    for network in networks:
        count = 0

        # appending network name to label list
        labels.append(network["name"])
        
        devices = dashboard.networks.getNetworkDevices(networkId=network["id"])

        # searching for Meraki MRs
        for device in devices:
            if device["model"].startswith("MR"):
                count = count + 1
                total["aps"] = total["aps"] + 1

        # tracking clients from Meraki stack 

        wireless_clients = 0
        try:
            client_count = dashboard.networks.getNetworkClients(networkId=network["id"],timespan=month_in_seconds,total_pages="all")
        except:
            continue

        for client in client_count:
            if client['ssid'] != None:
                wireless_clients = wireless_clients + 1
                total["clients"] = total["clients"] + 1

            if client['os'] != None:
                if client['os'].startswith('Windows') == True or client['os'].startswith('Mac OS') == True or client['os'].startswith('Chrome OS') == True:
                    total["laptops"] = total["laptops"] + 1
                
                if client['os'].startswith('Android') == True or client['os'].startswith('Apple iPhone') == True:
                    total["phones"] = total["phones"] + 1
                
        values.append(wireless_clients)

        # client count within the last month

        try:
            client_history = dashboard.wireless.getNetworkWirelessClientCountHistory(networkId=network["id"],timespan=month_in_seconds)
        except:
            continue



        for day in client_history:
            if day["clientCount"] != None:
                client_count = len(client_history)

                if client_count > greatest_clients:
                    greatest_clients = client_count
                    network_greatest_clients = network["name"]

        # query datarate 5 GHz band

        data_rate_count_5 = 0
        data_rate_5ghz = dashboard.wireless.getNetworkWirelessDataRateHistory(networkId=network["id"],timespan=month_in_seconds,band="5")
        for day in data_rate_5ghz:
            if day["averageKbps"] != None:
                data_rate_count_5 = data_rate_count_5 + day["averageKbps"]
                total["fiveghz"] = total["fiveghz"] + day["averageKbps"]*1e-6
                total["fiveghz"] = round(total["fiveghz"],2)

        # query datarate 2.4 GHz band

        data_rate_count_2 = 0
        data_rate_2ghz = dashboard.wireless.getNetworkWirelessDataRateHistory(networkId=network["id"],timespan=month_in_seconds,band="2.4")
        for day in data_rate_2ghz:
            if day["averageKbps"] != None:
                data_rate_count_2 = data_rate_count_2 + day["averageKbps"]
                total["twoghz"] = total["twoghz"] + day["averageKbps"]*1e-6
                total["twoghz"] =  round(total["twoghz"],2)
             

        network["ap_count"] = count
        network["client_count"] = wireless_clients

        # calculate data rate percentage distribution between the two bands

        try:
            if data_rate_count_5 > data_rate_count_2:
                percentage_five = ((data_rate_count_2/30) / (data_rate_count_5/30)) * 100
                percentage_two = 100 - percentage_five
            else:
                percentage_two = ((data_rate_count_5/30) / (data_rate_count_2/30)) * 100
                percentage_five = 100 - percentage_two
        except ZeroDivisionError as err:
            if data_rate_count_5 == 0:
                percentage_five = 0
            if data_rate_count_2 == 0:
                percentage_two = 0

        network["five_g"] = str(round(percentage_five,2)) + ' %'
        network["two_g"] = str(round(percentage_two,2)) + ' %'

    if total['phones'] > total['laptops']:
        if total['laptops'] == 0 and total['phones'] != 0:
            total['phones_percentage'] = 100
            total['laptops_percentage'] = 0
        else:
            total['phones_percentage'] = int(total['phones'] / total['laptops'] * 100)
            total['laptops_percentage'] = int(100 - total['phones_percentage'])
    else:
        if total['laptops'] != 0 and total['phones'] == 0:
            total['phones_percentage'] = 0
            total['laptops_percentage'] = 100
        else:
            total['laptops_percentage'] = int(total['laptops'] / total['phones'] * 100)
            total['phones_percentage'] = int(100 - total['laptop_percentage'])


    return render_template('usage.html',
                            networks=networks, 
                            max=greatest_clients, 
                            labels=labels, 
                            values=values,
                            greatest_clients = greatest_clients,
                            network_greatest_clients = network_greatest_clients,
                            total = total)

@app.route('/devices')
def devices():
    month_in_seconds = 2.678e+6
    # file name that will contain the device data for each network
    df = pd.read_excel('file.xlsx')
    labels = []
    networks = []

    used_byod = []
    total_byod = []
    student_population = []

    networks_from_file = df.columns.tolist()

    networks_from_dashboard = dashboard.organizations.getOrganizationNetworks(organizationId=config.meraki_org_id,total_pages='all')

    # will look for client device from excel file and match mac address from meraki network 
    for network_from_file in networks_from_file:
        counter = 0
        wireless_client_counter = 0
        network = {}

        network["network_name"] = network_from_file
        labels.append(network["network_name"])
        devices = df.loc[:,network_from_file].tolist()
        network["byod"] = len(devices)

        for network_from_dashboard in networks_from_dashboard:
            if network["network_name"].lower() == network_from_dashboard["name"].lower():
                print("Network found for " + network["network_name"] + ". Retrieving clients from network")
                clients = dashboard.networks.getNetworkClients(networkId=network_from_dashboard["id"],total_pages=-1,timepan=month_in_seconds)
                for device in devices:
                    for client in clients:
                        if client['ssid'] != None:
                            wireless_client_counter = wireless_client_counter + 1
                            if device == client["mac"]:
                                print("Client match " + device)
                                counter = counter + 1
                                break

        network["count"] = counter

        # calculate percentage of client devices found within the meraki stack

        try:
            network["percentage"] =  (network["byod"] / network["count"]) * 100
        except ZeroDivisionError as err:
            network["percentage"] = 0

        used_byod.append(network["count"])
        total_byod.append(network["byod"])
        student_population.append(wireless_client_counter)
        networks.append(network)


    return render_template('devices.html',labels=labels,networks=networks,used_byod=used_byod,total_byod=total_byod,student_population=student_population)

@app.route('/latency')
def latency():
    total = {"clients":0,"latency":0}
    values = []
    labels = []


    networks = []

    response = dashboard.organizations.getOrganizationNetworks(organizationId=config.meraki_org_id,total_pages="all")

    # retrieving the name and id for each network within the org
    for network in response:
        item = {}
        
        item["id"] = network["id"]
        item["name"] = network["name"]
        
        networks.append(item)

    
    for network in networks:
        average_latency = 0
        average_client_count = 0 

        # appending network name to label list
        labels.append(network["name"])
        
        latency = dashboard.wireless.getNetworkWirelessLatencyHistory(networkId=network["id"])

        for day in latency:
            if day["avgLatencyMs"] == None:
                continue
            average_latency = day["avgLatencyMs"] + average_latency

        try:
            network['average_latency'] = average_latency / len(latency)
        except ZeroDivisionError as err:
            network['average_latency'] = 0
        values.append(network['average_latency'])

        total["latency"] = total["latency"] + network["average_latency"]

        client_count = dashboard.wireless.getNetworkWirelessClientCountHistory(networkId=network["id"])

        for day in client_count:
            if day["clientCount"] == None:
                continue
            average_client_count = day["clientCount"] + average_client_count
            
            
        try:
           network['average_client_count'] = int(average_client_count / len(client_count))
     
        except ZeroDivisionError as err:
            network['average_client_count'] = 0

        total['clients'] = total['clients'] + network['average_client_count']
    try:
        total["latency"] = total["latency"] / len(networks)
    except ZeroDivisionError as err:
        total['latency'] = 0

    return render_template('latency.html', 
                            labels=labels,
                            values=values,
                            total = total,
                            networks = networks,
                            max=max(values),)

if __name__ == "__main__":
    app.run(debug=False,host= '0.0.0.0',port=5010)