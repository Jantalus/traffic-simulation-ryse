# Notas 

- Tomando como ejemplo arbitrario el mes de junio del 2015, la cantidad de vehiculos segun [datos](https://www.estadisticaciudad.gob.ar/eyc/?p=29183) 
del gobierno de BA es de 28.750.000, osea 28millones de autos en el mes. 
Rondando aproximadamente en 958333 autos por dia, osea 39930 autos por hora

- La definicion de conductor que no respeta las normas seria que 
    * Maneje a mayor o menor velocidad que el carril correspondiente
    * Con cierto bajo grado de cooperacion entre cambios de carriles


## Algunas defs de SUMO

La velocidad en "flujo libre" deseada de un vehiculo esta dictada por el factor de velocidad (speedFactor)
multiplicado por el límite de velocidad del carril, es decir que cuando tenemos un speedFactor de 1 
nuestra velocidad deseada es la máxima, a menos que el tipo de vehiculo defina distinto ya sea con:
- Velocidad máxima técnica del vehiculo
- Velocidad máxima deseada (media) del conductor

Para mantener la simulación realista y que los gaps entre vehiculos no sean constante el speedFactor
se determina bajo una distribucion normal con la media en 1 y una deviacion standard del 0,1.

## Que voy a medir
Sumar flujo de: conductores "normales" VS conductores "poco cooperativos"
- speed : avg speed trip
- duration: avg trip duration
- waitingTime (?): avg time spent standing involuntarily
- timeLoss : avg time due to driving slower than desired (includes waitingTime)
- totalTravelTime (/ inserted + running)
C/u de estas métricas en función de *la probabilidad del flujo de conductores* o  *vehiculos por hora*, sean cooperativos o no
y luego compararlas en un mismo gráfico

## Parámetros de cooperacion 
- speedFactor: >1 para apurados <1 para "lentejas"
- sigma: driver imperfection default 0.5
- lcStrategic: eagerness to lane change. default: 1.0, range \[0, inf\)
- lcCooperative: willingnes to perform cooperative lane changes. Default: 1.0,
- lcOvertakeRight: prob of violating rules against overtaking on the right. Default: 0, range \[0-1\]
- lcSpeedGain: eagerness to lane change in results for higher speed. Default: 1.0, range \[0, inf\]

## Graficos
- 

## Observaciones de la medición
Se definen 3 perfiles de conductores por default con sus velocidades máximas deseadas (desiredMaxSpeed): 
- Rapido, 150km/h (41,67m/s)
- Modeardo, 115km/h (32m/s)
- Lento, 90km/h (25m/s)

Donde la velocidad tope de cada uno esta dictaminada por (donde por default el speedFactor es 1): 
speed = min(speedFactor * desiredMaxSpeed, speedFactor * speedLimit)

Y las lineas de la autopista, siendo 5 y una banquina con los siguientes límites de velocidad:
- Linea rápida, 130km/h (36,11m/s)
- Segunda línea, 120km/h (33,33m/s)
- Tercer línea, 110km/h (30,55m/s)
- Cuarta línea, 100 km/h (27,78m/s)
- Quinta línea, 80km/h (22,22m/s)
- Banquina *, 60km/h (16,67m/s) donde solo pueden manejar los "banquineros"

## Route shit
```
		<vTypeDistribution id="non_cooperative_driver">
			<vType id="1" color="1,1,1" departSpeed="max" lcCooperative="-1" probability="0.5"/>
			<vType id="2" color="1,100,100" departSpeed="max" lcCooperative="-1" probability="0.5"/>
		</vTypeDistribution>

    <vType id="banquineros" vClass="custom1" length="5.00" departSpeed="max" maxSpeed="41.67" color="0,100,0" accel="3.0" decel="7.0" sigma="0.5" />
    
    <route id="straight" edges="highway" /> 

		<flow id="f_0" type="slow_driver" departLane="1" begin="0.00" route="straight" end="3600.00" vehsPerHour="1000000" />
		<flow id="f_1" type="moderate_driver" departLane="2" begin="0.00" route="straight" end="3600.00" vehsPerHour="1000000" />
		<flow id="f_2" type="moderate_driver" departLane="3" begin="0.00" route="straight" end="3600.00" vehsPerHour="1000000" />
		<flow id="f_3" type="moderate_driver" departLane="4" begin="0.00" route="straight" end="3600.00" vehsPerHour="1000000" />
		<flow id="f_4" type="fast_driver" departLane="5" begin="0.00" route="straight" end="3600.00" vehsPerHour="1000000" />

		<flow id="f_5" type="non_cooperative_driver" departLane="5" begin="0.00" route="straight" end="3600.00" probability="0.3"/>
		<flow id="f_6" type="banquineros" departLane="0" begin="0.00" route="straight" end="3600.00" probability="0.3"/>
```
