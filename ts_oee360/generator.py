import simpy, random, numpy as np, pandas as pd

SIM_HOURS = 8760
env = simpy.Environment()

# Shared state
raw_inventory = 1000.0
finished_inventory = 0
energy_price = 50.0
env_temp = 25.0
env_humidity = 40.0
worker_fatigue = 1.0

# WIP buffer
lag = 3
wip_buffer = [0] * lag

# Worker pool
workers = simpy.Container(env, init=3, capacity=4)

data = []

class PowerGrid:
    def __init__(self, env):
        self.env = env
        self.voltage = 1.0
        env.process(self.fluctuate())

    def fluctuate(self):
        for _ in range(SIM_HOURS):
            yield self.env.timeout(1)
            self.voltage = max(0.5, min(1.5, self.voltage + random.gauss(0, 0.01)))
            if random.random() < 0.002:
                down = random.randint(1, 5)
                self.voltage = 0
                yield self.env.timeout(down)
                self.voltage = 1.0

class Supplier:
    def __init__(self, env):
        self.env = env
        env.process(self.deliver())

    def deliver(self):
        global raw_inventory
        for _ in range(SIM_HOURS // 24 + 20):
            yield self.env.timeout(24)
            lead = random.randint(12, 72)
            yield self.env.timeout(lead)
            raw_inventory += random.uniform(200, 800)

class Machine:
    def __init__(self, env):
        self.env = env
        self.health = 1.0
        self.working = True
        self.last_pm = 0
        self.uptime = 0
        self.failures = 0
        env.process(self.run())

    def run(self):
        global raw_inventory
        for _ in range(SIM_HOURS):
            yield self.env.timeout(1)
            if self.working:
                load = random.uniform(0.8, 1.2)
                stress = load * (30 / env_temp) * random.uniform(0.9, 1.1)
                self.health -= 0.0003 * stress
                self.uptime += 1
                if (self.env.now - self.last_pm) >= 500:
                    self.last_pm = self.env.now
                    self.health = min(1.0, self.health + 0.25)
                if random.random() < 0.0005 * (2 - self.health) or Power.voltage < 0.8:
                    self.working = False
                    self.health = 0
                    env.process(self.repair(random.random() < 0.3))
                elif random.random() < 0.0015 * (2 - self.health):
                    env.process(self.repair(False))
            if random.random() < 0.001:
                self.working = False
                down = random.randint(1, 3)
                yield self.env.timeout(down)
                self.working = True

    def repair(self, major):
        dur = random.randint(12, 24) if major else random.randint(3, 8)
        dur *= worker_fatigue
        yield workers.get(1)
        yield self.env.timeout(dur)
        self.health = min(1.0, self.health + random.uniform(0.3, 0.6))
        self.working = True
        yield workers.put(1)

# Instantiate environment components
Power = PowerGrid(env)
Supp = Supplier(env)
machines = [Machine(env) for _ in range(5)]

def simulate(env):
    global raw_inventory, finished_inventory
    global energy_price, env_temp, env_humidity, worker_fatigue
    for hour in range(SIM_HOURS):
        if raw_inventory < 200:
            raw_inventory += random.uniform(300, 600)

        energy_price += random.uniform(-1, 1)
        env_temp = 25 + 10 * np.sin(2 * np.pi * hour / 24) + random.gauss(0, 0.5)
        env_humidity = 40 + 20 * np.sin(2 * np.pi * hour / (24 * 7)) + random.gauss(0, 1)

        shift = (hour // 8) % 3
        target = 4 if shift == 1 else 2
        delta = target - workers.level
        if delta > 0:
            yield workers.put(delta)
        elif delta < 0:
            yield workers.get(-delta)

        worker_fatigue = 1 + 0.5 * (shift == 2)

        effs = [m.health if m.working else 0 for m in machines]
        availability = sum(m.working for m in machines) / len(machines)
        performance = np.mean(effs)
        quality = np.mean([0.99 if h > 0.85 else 0.92 if h > 0.6 else 0.85 for h in effs])
        oee = availability * performance * quality

        demand = random.uniform(0.85, 1.15)
        throughput = int(450 * oee * demand * Power.voltage)
        raw_inventory = max(0, raw_inventory - throughput * 0.6)

        wip_buffer.append(throughput)
        finished_inventory += wip_buffer.pop(0)

        maintenance = int(any((hour - m.last_pm) < 1 for m in machines))
        downtime = int(availability < 1)
        mtbf = np.mean([m.uptime / m.failures if m.failures > 0 else m.uptime for m in machines])

        data.append([
            hour, oee, availability, performance, quality, throughput,
            raw_inventory, sum(wip_buffer), finished_inventory,
            round(energy_price, 2), round(env_temp, 1), round(env_humidity, 1),
            round(Power.voltage, 2), workers.level, round(worker_fatigue, 2),
            maintenance, downtime, round(mtbf, 1), shift
        ])
        yield env.timeout(1)

# Start simulation
env.process(simulate(env))
env.run()

# Save data
df = pd.DataFrame(data, columns=[
    "hour", "OEE", "availability", "performance", "quality", "throughput",
    "raw_inventory", "wip", "finished", "energy_price", "temp", "humidity",
    "voltage", "available_workers", "fatigue", "maintenance", "downtime", "MTBF", "shift"
])
df.to_csv("data/ultra_complex_OEE.csv", index=False)