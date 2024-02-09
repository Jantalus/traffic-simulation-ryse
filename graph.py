import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


data = pd.read_csv('csvs4/output.csv', dtype={
    'vehsPerHour': int, 
    'speedFactor': float,
    'sigma': float,
    'lcStrategic': float,
    'lcCooperative': float,
    'lcSpeedGain': float,
    'speed': float,
    'duration': float,
    'waitingTime': float,
    'totalTravelTime': int,
})

otherDefaultValues = {
        'speedFactor': 1.0,
        'sigma': 0.5,
        'lcStrategic': 1.0,
        'lcCooperative': 1.0,
        'lcSpeedGain': 1.0,
        'lcOvertakeRight': 0.0,
}

evalStringForHues = {
        'speedFactor': f'sigma == {otherDefaultValues["sigma"]} & lcStrategic == {otherDefaultValues["lcStrategic"]} & lcCooperative == {otherDefaultValues["lcCooperative"]} & lcSpeedGain == {otherDefaultValues["lcSpeedGain"]} & lcOvertakeRight == {otherDefaultValues["lcOvertakeRight"]}',
        'sigma': f'speedFactor == {otherDefaultValues["speedFactor"]} & lcStrategic == {otherDefaultValues["lcStrategic"]} & lcCooperative == {otherDefaultValues["lcCooperative"]} & lcSpeedGain == {otherDefaultValues["lcSpeedGain"]} & lcOvertakeRight == {otherDefaultValues["lcOvertakeRight"]}',
        'lcStrategic': f'speedFactor == {otherDefaultValues["speedFactor"]} & sigma == {otherDefaultValues["sigma"]} & lcCooperative == {otherDefaultValues["lcCooperative"]} & lcSpeedGain == {otherDefaultValues["lcSpeedGain"]} & lcOvertakeRight == {otherDefaultValues["lcOvertakeRight"]}',
        'lcCooperative': f'speedFactor == {otherDefaultValues["speedFactor"]} & sigma == {otherDefaultValues["sigma"]} & lcStrategic == {otherDefaultValues["lcStrategic"]} & lcSpeedGain == {otherDefaultValues["lcSpeedGain"]} & lcOvertakeRight == {otherDefaultValues["lcOvertakeRight"]}',
        'lcSpeedGain': f'speedFactor == {otherDefaultValues["speedFactor"]} & sigma == {otherDefaultValues["sigma"]} & lcStrategic == {otherDefaultValues["lcStrategic"]} & lcCooperative == {otherDefaultValues["lcCooperative"]} & lcOvertakeRight == {otherDefaultValues["lcOvertakeRight"]}',
}


output = ET.parse('default_output.xml')
vts = output.findall('vehicleTripStatistics')[0]

defaultRouteMetrics = {
        'speed': float(str(vts.get('speed'))),
        'duration': float(str(vts.get('duration'))),
        'waitingTime': float(str(vts.get('waitingTime'))),
        'timeLoss': float(str(vts.get('timeLoss'))),
        'totalTravelTime': float(str(vts.get('totalTravelTime'))),
}



defaultEvaluation = f'speedFactor == {otherDefaultValues["speedFactor"]} & sigma == {otherDefaultValues["sigma"]} & lcStrategic == {otherDefaultValues["lcStrategic"]} & lcCooperative == {otherDefaultValues["lcCooperative"]} & lcOvertakeRight == {otherDefaultValues["lcOvertakeRight"]} & lcSpeedGain == {otherDefaultValues["lcSpeedGain"]}'

fixedVariable = 'vehsPerHour'

metricsToGraph = ['speed', 'duration', 'waitingTime', 'timeLoss', 'totalTravelTime']

availableHues = ['speedFactor', 'sigma', 'lcStrategic', 'lcCooperative', 'lcSpeedGain']

# Iterate through the columns and create graphs for each metric against the fixed variable
for metric in metricsToGraph:
    for hueMetric in availableHues:
        plt.figure(figsize=(8, 6))
        print(f"Plotting {metric} by {hueMetric}")
        dataWithHueAndOtherDefaults = data[data.eval(evalStringForHues[hueMetric])]
        allDefaultData = data[data.eval(defaultEvaluation)]
        sns.lineplot(data=dataWithHueAndOtherDefaults, x=fixedVariable, y=metric, hue=hueMetric, palette='viridis')
        plt.axhline(y=defaultRouteMetrics[metric], color='r', linestyle='--', label='Default Route')
        plt.title(f"{fixedVariable} vs {metric} colored by {hueMetric}(banquineros)")
        plt.xlabel(fixedVariable)
        plt.ylabel(metric)
        #plt.legend(title=hueMetric)
        plt.tight_layout()

        # Save the image with a descriptive filename
        plt.savefig(f"graficos_banquineros/{metric}_by_{hueMetric}(banquineros).png")
        plt.close()


#sns.lineplot(data=data[data['speedFactor'] = speedFactor & data['sigma'] = sigma & data['lcSpeedGain'] = lcSpeedGain & data['lcOvertakeRight'] = lcOvertakeRight], x="vehsPerHour", y="timeLoss", hue="lcCooperative")
#user_ratings = pd.read_csv(f"{BASE_PATH}/ratings.csv", dtype={'userId': str, 'movieId': str, 'rating': float,'timestamp': int})
#                                                                                                                                                                                                                       
#plt.figure(figsize = (15,8))
#for lcCooperative in uncooperativeAttributesToIterate['lcCooperative']:
#    plt.figure()
#    sns.lineplot(
#    data=data[data.eval(f'lcCooperative == {lcCooperative} & speedFactor == {speedFactor} & sigma == {sigma} & lcSpeedGain == {lcSpeedGain} & lcOvertakeRight == {lcOvertakeRight} & lcStrategic == {lcStrategic}')], 
#         x="vehsPerHour", y="speed",
#         markers="True", dashes=False)
#
#    plt.title(f"Cooperative: {lcCooperative}")
#    plt.savefig(f"graficos/cooperative_{lcCooperative}.png")
