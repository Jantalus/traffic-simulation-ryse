import xml.etree.ElementTree as ET
import subprocess
from subprocess import DEVNULL,STDOUT
import numpy as np
import csv

import tqdm
from tqdm import tqdm


listOfMinus1 = [-1]
# Drivers that go faster than expected
uncooperativeAttributesToIterate = {
        'speedFactor': [1.0],
        'sigma': [0.5],
        'lcStrategic': [-1],
        'lcCooperative': [0.0],
        'lcSpeedGain': [0.0],
        'lcOvertakeRight': [0.0, 1.0],
}

# 3 * 3 * 11 * 5 * 11 * 11 = 59895

# p: 0%, 5%, 10%, ..., 100%
#for p in range(0, 101, 5):
#for vehsPerHour in range(0, 16000, 500):

rows = []

for speedFactor in tqdm(uncooperativeAttributesToIterate['speedFactor'], leave=False):
    for sigma in tqdm(uncooperativeAttributesToIterate['sigma'], leave=False):
        for lcStrategic in tqdm(uncooperativeAttributesToIterate['lcStrategic'], leave=False):
            for lcCooperative in tqdm(uncooperativeAttributesToIterate['lcCooperative'], leave=False):
                for lcSpeedGain in tqdm(uncooperativeAttributesToIterate['lcSpeedGain'], leave=False):
                    for lcOvertakeRight in tqdm(uncooperativeAttributesToIterate['lcOvertakeRight'], leave=False):
                        for vehsPerHour in tqdm(range(1000, 15001, 1000), leave=False): 
                            routes = ET.parse('default_route.rou.xml')

                            # Modify flow element 
                            for flow in routes.findall('flow'):
                                if flow.get('id') == 'f_3':
                                    currentVPH = flow.get('vehsPerHour')
                                    currentVPH = int(currentVPH)
                                    currentVPH = currentVPH - vehsPerHour
                                    flow.set('vehsPerHour', str(currentVPH))
                            
                            # print current iteration
                            #print('speedFactor: ', speedFactor, 'sigma: ', sigma, 'lcStrategic: ', lcStrategic, 'lcCooperative: ', lcCooperative, 'lcSpeedGain: ', lcSpeedGain, 'lcOvertakeRight: ', lcOvertakeRight, 'vehsPerHour: ', vehsPerHour)

                            newVehicleType = ET.Element('vType')
                            newVehicleType.set('id', 'uncooperative_driver')
                            newVehicleType.set('minGap', '1')
                            newVehicleType.set('sigma', str(sigma))
                            newVehicleType.set('speedFactor', str(speedFactor))
                            newVehicleType.set('lcStrategic', str(lcStrategic))
                            newVehicleType.set('lcCooperative', str(lcCooperative))
                            newVehicleType.set('lcSpeedGain', str(lcSpeedGain))
                            newVehicleType.set('lcOvertakeRight', str(lcOvertakeRight))

                            newFlow = ET.Element('flow')
                            newFlow.set('id', 'f_5')
                            newFlow.set('type', 'uncooperative_driver')
                            newFlow.set('departLane', '4')
                            newFlow.set('begin', '0.00')
                            newFlow.set('departSpeed', "max")
                            newFlow.set('route', 'straight')
                            newFlow.set('vehsPerHour', str(vehsPerHour))

                            routes.getroot().append(newVehicleType)


                            routes.getroot().append(newFlow)

                            routes.write('python_route.rou.xml')
                            subprocess.run(['sumo', '-c', 'conf.sumocfg', '--statistic-output', 'output_tripinfo.xml', '--duration-log.statistics'], stdout=DEVNULL, stderr=STDOUT)

                            output = ET.parse('output_tripinfo.xml')
                            vts = output.findall('vehicleTripStatistics')[0]
                            speed = vts.get('speed')
                            duration = vts.get('duration')
                            waitingTime = vts.get('waitingTime')
                            timeLoss = vts.get('timeLoss')
                            totalTravelTime = vts.get('totalTravelTime')

                            rows.append([vehsPerHour, speedFactor, sigma, lcStrategic, lcCooperative, lcSpeedGain, lcOvertakeRight, speed, duration, waitingTime, timeLoss, totalTravelTime])
                            break





# - speed : avg speed trip
#- duration: avg trip duration
#- waitingTime (?): avg time spent standing involuntarily
#- timeLoss : avg time due to driving slower than desired (includes waitingTime)
#- totalTravelTime (/ inserted + running)

csvOutputHeaders = ['vehsPerHour','speedFactor', 'sigma', 'lcStrategic', 'lcCooperative', 'lcSpeedGain', 'lcOvertakeRight', 'speed', 'duration', 'waitingTime', 'timeLoss', 'totalTravelTime']

with open('output.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(csvOutputHeaders)
    writer.writerows(rows)

