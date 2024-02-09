import xml.etree.ElementTree as ET
import subprocess
from subprocess import DEVNULL,STDOUT
import numpy as np
import csv
import multiprocessing
from multiprocessing.pool import Pool

import tqdm
from tqdm import tqdm


# Drivers that go faster than expected
#uncooperativeAttributesToIterate = {
#        'speedFactor': np.arange(1.0, 1.31, 0.1),# 3
#        'sigma': np.arange(0.5, 1.1, 0.25),# 3
#        'lcStrategic': np.append([-1], np.arange(0.0, 10.1, 1)),# 11
#        'lcCooperative': np.arange(0.0, 1.1, 0.25), # 5
#        'lcSpeedGain': np.arange(0.0, 10.1, 1), # 11
#        'lcOvertakeRight': np.arange(0.0, 10.1, 1), # 11
#}

uncooperativeAttributesToIterate = {
        'speedFactor': [1.0, 1.1, 1.2, 1.3],
        'sigma': np.arange(0.5, 1.1, 0.25),# 3
        'lcStrategic': np.append([-1], np.arange(0.0, 10.1, 1)),# 12
        'lcCooperative': np.arange(0.0, 1.1, 0.25), # 5
        'lcSpeedGain': np.arange(0.0, 10.1, 1), # 11
        'lcOvertakeRight': np.arange(0.0, 10.1, 1), # 11
}

attributesDefaultValues = {
        'speedFactor': 1.0,
        'sigma': 0.5,
        'lcStrategic': 1.0,
        'lcCooperative': 1.0,
        'lcSpeedGain': 1.0,
        'lcOvertakeRight': 0.0,
}

csvOutputHeaders = ['vehsPerHour','speedFactor', 'sigma', 'lcStrategic', 'lcCooperative', 'lcSpeedGain', 'lcOvertakeRight', 'speed', 'duration', 'waitingTime', 'timeLoss', 'totalTravelTime']
csvFileName = f'csvs3/output.csv'

with open(csvFileName, 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(csvOutputHeaders)


def runSimulationAndSave(speedFactor: float, sigma: float, lcStrategic: float, lcCooperative: float, lcSpeedGain: float, lcOvertakeRight: float):
    rows = []

    for vehsPerHour in range(1000, 15001, 1000):
        routes = ET.parse('default_route.rou.xml')

        # Modify flow element 
        for flow in routes.findall('flow'):
            if flow.get('id') == 'f_3':
                currentVPH = flow.get('vehsPerHour')
                currentVPH = int(currentVPH)
                currentVPH = currentVPH - vehsPerHour
                flow.set('vehsPerHour', str(currentVPH))
        
        # print current iteration

        newVehicleType = ET.Element('vType')
        newVehicleType.set('id', 'uncooperative_driver')
        newVehicleType.set('length', '5.00')
        newVehicleType.set('accel', '2.00')
        newVehicleType.set('decel', '6.00')
        newVehicleType.set('minGap', '1')
        newVehicleType.set('sigma', str(sigma))
        newVehicleType.set('speedFactor', str(speedFactor))
        newVehicleType.set('lcStrategic', str(lcStrategic))
        newVehicleType.set('lcCooperative', str(lcCooperative))
        newVehicleType.set('lcSpeedGain', str(lcSpeedGain))
        newVehicleType.set('lcOvertakeRight', str(lcOvertakeRight))
        newVehicleType.set('desiredMaxSpeed', '32')

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

        pythonRoute = 'routes/python_route.rou.xml'
        outputInfo = 'outputs/output_tripinfo.xml'
        routes.write(pythonRoute)
        print(f'Running simulation with speedFactor: {speedFactor}, sigma: {sigma}, lcStrategic: {lcStrategic}, lcCooperative: {lcCooperative}, lcSpeedGain: {lcSpeedGain}, lcOvertakeRight: {lcOvertakeRight}, vehsPerHour: {vehsPerHour}')
        subprocess.run(['sumo', '-c', 'conf.sumocfg', '-r', pythonRoute, '--statistic-output', outputInfo, '--duration-log.statistics'], stdout=DEVNULL, stderr=STDOUT)

        output = ET.parse(outputInfo)
        vts = output.findall('vehicleTripStatistics')[0]
        speed = vts.get('speed')
        duration = vts.get('duration')
        waitingTime = vts.get('waitingTime')
        timeLoss = vts.get('timeLoss')
        totalTravelTime = vts.get('totalTravelTime')

        rows.append([vehsPerHour, speedFactor, sigma, lcStrategic, lcCooperative, lcSpeedGain, lcOvertakeRight, speed, duration, waitingTime, timeLoss, totalTravelTime])
    
    with open(csvFileName, 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(rows)
    rows = []

for speedFactor in uncooperativeAttributesToIterate['speedFactor']:
    runSimulationAndSave(speedFactor, attributesDefaultValues['sigma'], attributesDefaultValues['lcStrategic'], attributesDefaultValues['lcCooperative'], attributesDefaultValues['lcSpeedGain'], attributesDefaultValues['lcOvertakeRight'])

for sigma in uncooperativeAttributesToIterate['sigma']:
    runSimulationAndSave(attributesDefaultValues['speedFactor'], sigma, attributesDefaultValues['lcStrategic'], attributesDefaultValues['lcCooperative'], attributesDefaultValues['lcSpeedGain'], attributesDefaultValues['lcOvertakeRight'])

for lcStrategic in uncooperativeAttributesToIterate['lcStrategic']:
    runSimulationAndSave(attributesDefaultValues['speedFactor'], attributesDefaultValues['sigma'], lcStrategic, attributesDefaultValues['lcCooperative'], attributesDefaultValues['lcSpeedGain'], attributesDefaultValues['lcOvertakeRight'])

for lcCooperative in uncooperativeAttributesToIterate['lcCooperative']:
    runSimulationAndSave(attributesDefaultValues['speedFactor'], attributesDefaultValues['sigma'], attributesDefaultValues['lcStrategic'], lcCooperative, attributesDefaultValues['lcSpeedGain'], attributesDefaultValues['lcOvertakeRight'])

for lcSpeedGain in uncooperativeAttributesToIterate['lcSpeedGain']:
    runSimulationAndSave(attributesDefaultValues['speedFactor'], attributesDefaultValues['sigma'], attributesDefaultValues['lcStrategic'], attributesDefaultValues['lcCooperative'], lcSpeedGain, attributesDefaultValues['lcOvertakeRight'])

for lcOvertakeRight in uncooperativeAttributesToIterate['lcOvertakeRight']:
    runSimulationAndSave(attributesDefaultValues['speedFactor'], attributesDefaultValues['sigma'], attributesDefaultValues['lcStrategic'], attributesDefaultValues['lcCooperative'], attributesDefaultValues['lcSpeedGain'], lcOvertakeRight)


# - speed : avg speed trip
#- duration: avg trip duration
#- waitingTime (?): avg time spent standing involuntarily
#- timeLoss : avg time due to driving slower than desired (includes waitingTime)
#- totalTravelTime (/ inserted + running)



