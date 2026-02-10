import traci
import matplotlib.pyplot as plt

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
MIN_GREEN_TIME = 8
green_timer = 0

time_data = []
north_data = []
south_data = []
west_data = []
east_data = []
current_time = 0

def step_and_record():
    global current_time
    traci.simulationStep()
    densities = {d: get_density(e) for d, e in incoming_edges.items()}
    time_data.append(current_time)
    north_data.append(densities["N"])
    south_data.append(densities["S"])
    west_data.append(densities["W"])
    east_data.append(densities["E"])
    current_time += 1



while traci.simulation.getMinExpectedNumber() > 0:

    densities = {d: get_density(e) for d, e in incoming_edges.items()}

    desired_dir = max(densities, key=densities.get)

    # Enforce minimum green lock
    if previous_dir is not None and desired_dir != previous_dir and green_timer < MIN_GREEN_TIME:
        max_dir = previous_dir
    else:
        max_dir = desired_dir

    # --- SWITCHING PHASE (add yellow only if direction changes) ---
    if previous_dir and previous_dir != max_dir:
        if previous_dir == "N":
            yellow = "yyyrrrrrrrrr"
        elif previous_dir == "S":
            yellow = "rrryyyrrrrrr"
        elif previous_dir == "W":
            yellow = "rrrrrryyyrrr"
        else:
            yellow = "rrrrrrrrryyy"

        traci.trafficlight.setRedYellowGreenState(TLS_ID, yellow)

        for _ in range(3):
            step_and_record()


        green_timer = 0  # Reset timer after switching

    # --- GREEN PHASE ---
    if max_dir == "N":
        state = "GGGrrrrrrrrr"
    elif max_dir == "S":
        state = "rrrGGGrrrrrr"
    elif max_dir == "W":
        state = "rrrrrrGGGrrr"
    else:
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
        step_and_record()
        green_timer += 1



traci.close()

plt.figure(figsize=(10,6))

plt.plot(time_data, north_data, label="North", color='blue')
plt.plot(time_data, south_data, label="South", color='red')
plt.plot(time_data, west_data, label="West", color='green')
plt.plot(time_data, east_data, label="East", color='orange')

plt.xlabel("Simulation Time (seconds)")
plt.ylabel("Number of Vehicles Waiting")
plt.title("Traffic Density vs Time (Adaptive Signal Control)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.pause(0.1)


plt.show()

