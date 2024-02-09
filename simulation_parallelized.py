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
        'speedFactor': np.arange(1.0, 1.31, 0.1),# 3
        'sigma': np.arange(0.5, 1.1, 0.25),# 3
        'lcStrategic': np.append([-1], np.arange(0.0, 10.1, 1)),# 12
        'lcCooperative': np.arange(0.0, 1.1, 0.25), # 5
        'lcSpeedGain': np.arange(0.0, 10.1, 1), # 11
        'lcOvertakeRight': np.arange(0.0, 10.1, 1), # 11
}

def runSimulationAndSave(speedFactor: float, sigma: float, lcStrategic: float):
    #print(f'Running simulation with speedFactor: {speedFactor}, sigma: {sigma}, lcStrategic: {lcStrategic}')
    rows = []
    csvOutputHeaders = ['vehsPerHour','speedFactor', 'sigma', 'lcStrategic', 'lcCooperative', 'lcSpeedGain', 'lcOvertakeRight', 'speed', 'duration', 'waitingTime', 'timeLoss', 'totalTravelTime']
    csvFileName = f'csvs2/output-SF{speedFactor}-sigma{sigma}-lcStra{lcStrategic}.csv'

    with open(csvFileName, 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(csvOutputHeaders)

    for lcCooperative in tqdm(uncooperativeAttributesToIterate['lcCooperative'], desc = f'speedFactor: {speedFactor}, sigma: {sigma}, lcStrategic: {lcStrategic}'):
        for lcSpeedGain in tqdm(uncooperativeAttributesToIterate['lcSpeedGain'], leave=False):
            for lcOvertakeRight in tqdm(uncooperativeAttributesToIterate['lcOvertakeRight'], leave=False):
    #for lcCooperative in uncooperativeAttributesToIterate['lcCooperative']:
    #    for lcSpeedGain in uncooperativeAttributesToIterate['lcSpeedGain']:
    #        for lcOvertakeRight in uncooperativeAttributesToIterate['lcOvertakeRight']:
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

                    pythonRoute = f'routes/python_route.rou-{speedFactor}-{sigma}-{lcStrategic}.xml'
                    outputInfo = f'outputs/output_tripinfo-{speedFactor}-{sigma}-{lcStrategic}.xml'
                    routes.write(pythonRoute)
                    subprocess.run(['sumo', '-c', 'conf.sumocfg', '-r', pythonRoute, '--statistic-output', outputInfo, '--duration-log.statistics'], stdout=DEVNULL, stderr=STDOUT)

                    output = ET.parse(outputInfo)
                    vts = output.findall('vehicleTripStatistics')[0]
                    speed = vts.get('speed')
                    duration = vts.get('duration')
                    waitingTime = vts.get('waitingTime')
                    timeLoss = vts.get('timeLoss')
                    totalTravelTime = vts.get('totalTravelTime')

                    rows.append([vehsPerHour, speedFactor, sigma, lcStrategic, lcCooperative, lcSpeedGain, lcOvertakeRight, speed, duration, waitingTime, timeLoss, totalTravelTime])

                    if len(rows) > 1000:
                        with open(csvFileName, 'a') as csvFile:
                            writer = csv.writer(csvFile)
                            writer.writerows(rows)
                        rows = []

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

if __name__ == '__main__':
    items = [(sf, s, lcS) for sf in uncooperativeAttributesToIterate['speedFactor'] for s in uncooperativeAttributesToIterate['sigma'] for lcS in uncooperativeAttributesToIterate['lcStrategic']]
    items.append((1.2, 1.0, 8.0))

    listSplitted = list(split(items, multiprocessing.cpu_count()))
    with Pool() as pool:
        for chunk in listSplitted:
            _ = pool.starmap_async(runSimulationAndSave, chunk)
        
        pool.close()
        print("Waiting for pool")
        pool.join()

        print('Results Done')

    print("csv AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")





# - speed : avg speed trip
#- duration: avg trip duration
#- waitingTime (?): avg time spent standing involuntarily
#- timeLoss : avg time due to driving slower than desired (includes waitingTime)
#- totalTravelTime (/ inserted + running)



