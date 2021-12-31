import os
os.chdir(os.getcwd())

import json
import random
from cog import *

version = "basic"


with open("variables/settings.json") as f:
    settings = json.loads(f.read())
with open("variables/archetype.json") as f:
    archeType = json.loads(f.read())
    archeNames = []
    for x in archeType:
        archeNames.append(x)
with open("variables/ride.json") as f:
    ridesList = json.loads(f.read())
    rideNames = []
    for x in ridesList:
        rideNames.append(x)

class person:
    def __init__(self, type, location):
        self.type = type

agents = list()
for i in range(settings[version]['population']):
    agent = person(random.choice(archeNames), "Hub")
    agents.append(agent)

for x in agents:
    ride = random.choice(rideNames)
    