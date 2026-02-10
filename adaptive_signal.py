import traci

# Start SUMO
traci.start(["sumo-gui", "-c", "simulation.sumocfg"])

TLS_ID = "J0"

# Incoming edges
incoming_edges = {
    "N": "E5",
    "S": "E4",
    "W": "E3",
    "E": "E0"
}

def get_density(edge):
    return traci.edge.getLastStepVehicleNumber(edge)

# Force SUMO to use TraCI control (disable static all-red program)
traci.trafficlight.setProgram(TLS_ID, "0")

while traci.simulation.getMinExpectedNumber() > 0:

    densities = {d: get_density(e) for d, e in incoming_edges.items()}
    max_dir = max(densities, key=densities.get)

    # 12 SIGNAL LINKS → 12 CHARACTERS REQUIRED
    # r = red, g = green, y = yellow

    if max_dir == "N":       # Only North open
        state = "GGGrrrrrrrrr"   # 3 greens, rest red

    elif max_dir == "S":     # Only South open
        state = "rrrGGGrrrrrr"

    elif max_dir == "W":     # Only West open
        state = "rrrrrrGGGrrr"

    else:                    # Only East open
        state = "rrrrrrrrrGGG"

    traci.trafficlight.setRedYellowGreenState(TLS_ID, state)

    # Keep that signal green for 10 seconds
    for _ in range(10):
        traci.simulationStep()

traci.close()
