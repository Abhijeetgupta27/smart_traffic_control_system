import traci

traci.start(["sumo-gui", "-c", "simulation.sumocfg"])

TLS_ID = "J0"

incoming_edges = {
    "N": "E5",
    "S": "E4",
    "W": "E3",
    "E": "E0"
}

def get_density(edge):
    return traci.edge.getLastStepVehicleNumber(edge)

# Force TraCI control
traci.trafficlight.setProgram(TLS_ID, "0")

previous_dir = None

while traci.simulation.getMinExpectedNumber() > 0:

    densities = {d: get_density(e) for d, e in incoming_edges.items()}
    max_dir = max(densities, key=densities.get)

    # --- YELLOW PHASE before switching ---
    if previous_dir and previous_dir != max_dir:

        if previous_dir == "N":
            yellow = "yyyrrrrrrrrr"
        elif previous_dir == "S":
            yellow = "rrryyyrrrrrr"
        elif previous_dir == "W":
            yellow = "rrrrrryyyrrr"
        else:  # East
            yellow = "rrrrrrrrryyy"

        traci.trafficlight.setRedYellowGreenState(TLS_ID, yellow)

        # Hold yellow for 3 seconds
        for _ in range(3):
            traci.simulationStep()

    # --- GREEN PHASE ---
    if max_dir == "N":
        state = "GGGrrrrrrrrr"
    elif max_dir == "S":
        state = "rrrGGGrrrrrr"
    elif max_dir == "W":
        state = "rrrrrrGGGrrr"
    else:  # East
        state = "rrrrrrrrrGGG"

    traci.trafficlight.setRedYellowGreenState(TLS_ID, state)
    previous_dir = max_dir

    # --- DYNAMIC GREEN TIME ---
    vehicle_count = densities[max_dir]

    if vehicle_count <= 5:
        green_time = 6
    elif vehicle_count <= 12:
        green_time = 10
    else:
        green_time = 15

    print(f"Direction {max_dir} | Vehicles: {vehicle_count} | Green Time: {green_time}s")

    for _ in range(green_time):
        traci.simulationStep()

traci.close()
