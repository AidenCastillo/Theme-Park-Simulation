import os
import sys
os.chdir(os.getcwd())

import json
import random
from cog import *


with open("variables/settings.json") as f:
    settings = json.loads(f.read())
with open("variables/archetype.json") as f:
    archeType = json.loads(f.read())
    print(archeType)
    archeNames = []
    for x in archeType:
        archeNames.append(x)
with open("variables/ride.json") as f:
    rides = json.loads(f.read())
    rideNames = []
    for x in rides:
        rideNames.append(x)

class person:
    def __init__(self, arche, location, CurrentWait):
        self.arche = arche
        self.location = location
        self.CurrentWait = CurrentWait

class ParkSim:
    def __init__(self):
        '''
        Seed: Randomizer seed

        Time: Runs on military time for simplicity
        '''
        self.seed = settings[version]['seed']
        self.time = 8
        self.agents = list()

    def runSim(self):
        self.CreateAgents(100)
        print(self.agents)
        while True:
            self.event()
          
            for i in self.agents:
              
                if i.location == "Hub":
                    self.weightedChoice(i, "ride")
                elif i.location in rideNames:
                    if i.CurrentWait == archeType[i.arche]["wait"]:
                        self.weightedChoice(i, "ride")
                        i.CurrentWait = 0

            self.log(self.agents, "data/log.json")
            self.timeChange()            
    
    def CreateAgents(self, count):
        for i in range(int(count)):
            agent = person(random.choice(archeNames), "Hub", 0)
            self.agents.append(agent)
    
    def weightedChoice(self, target, type):
        weight = list()
        if  type == "ride":
            for x in rideNames:
                weight.append(rides[x]["popularity"])
                
            target.location = random.choices(rideNames, weights=weight)[0]
    def timeChange(self):
        if self.time < 22:
            self.time += 1
            for i in self.agents:
                i.CurrentWait += 1
        elif self.time == 22:
            print(self.time)
            sys.exit()
    def event(self):
        count = settings[version]['population'] * settings[version]['hourly_percent'][str(self.time)]
        print(count)
        self.CreateAgents(count)
    def log(self, data, file):
        if logging:
            with open(file) as f:
                current = json.loads(f.read())
            for i in data:
                
                current.append(i.location)
            with open(file, "w") as f:
                f.write(json.dumps(current))
def main():
    simulation = ParkSim()
    simulation.runSim()

            

#start sim
#if __name__ == '__main__':
main()