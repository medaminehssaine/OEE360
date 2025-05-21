# ts_oee360/simulator.py

import simpy
import random
import numpy as np

SIM_HOURS = 8760

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
        from .generator import raw_inventory  # Access shared state
        for _ in range(SIM_HOURS // 24 + 20):
            yield self.env.timeout(24)
            lead = random.randint(12, 72)
            yield self.env.timeout(lead)
            raw_inventory += random.uniform(200, 800)

class Machine:
    def __init__(self, env, workers, power):
        self.env = env
        self.workers = workers
        self.power = power
        self.health = 1.0
        self.working = True
        self.last_pm = 0
        self.uptime = 0
        self.failures = 0
        env.process(self.run())

    def run(self):
        from .generator import raw_inventory, env_temp
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
                if random.random() < 0.0005 * (2 - self.health) or self.power.voltage < 0.8:
                    self.working = False
                    self.health = 0
                    self.env.process(self.repair(major=random.random() < 0.3))
                elif random.random() < 0.0015 * (2 - self.health):
                    self.env.process(self.repair(major=False))
            if random.random() < 0.001:
                self.working = False
                down = random.randint(1, 3)
                yield self.env.timeout(down)
                self.working = True

    def repair(self, major):
        from .generator import worker_fatigue
        dur = random.randint(12, 24) if major else random.randint(3, 8)
        dur *= worker_fatigue
        yield self.workers.get(1)
        yield self.env.timeout(dur)
        self.health = min(1.0, self.health + random.uniform(0.3, 0.6))
        self.working = True
        yield self.workers.put(1)
