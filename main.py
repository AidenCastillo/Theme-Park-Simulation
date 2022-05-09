from cmath import inf
import os
import sys
os.chdir(os.getcwd())

import json
import random
from cog import *


with open("variables/settings.json") as f:
    settings = json.loads(f.read())
    settings = settings[version]
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
    def __init__(self, arche, location):
        self.arche = arche
        self.location = location
        self.CurrentWait = 0
        self.stay = 0

class ParkSim:
    def __init__(self):
        '''
        Seed: Randomizer seed

        Time: Runs on military time for simplicity
        '''
        self.seed = settings['seed']
        self.time = 8
        self.agents = list()

    def runSim(self):
        self.CreateAgents(100)
        print(self.agents)
        while True:
            self.event()
          
            for i in self.agents:
                '''
                if the agent's location is `hub`, send the agent to a new ride

                if the agent's location is a ride, check if their `CurrentWait` is at the max for their archeType
                if `CurrentWait` is at max, remove them from the queue or line, send to new location, and change `CurrentWait` to 0
                '''
                if i.location == "Hub":
                    self.weightedChoice(i, "ride")
                elif i.location in rideNames:
                    if i.CurrentWait == archeType[i.arche]["wait"]:
                        rides[i.location]['reg_queue'].remove(i)
                        
                        self.weightedChoice(i, "ride")
                        i.CurrentWait = 0

            self.FindWait(rides['hexagon'])
            self.timeChange()            
    
    def CreateAgents(self, count):
        '''
        Initiates the person class and places in `self.agents`

        Count: Number of Agents to create
        '''
        for i in range(int(count)):
            agent = person(self.weightedChoice(type="arche"), "Hub")
            self.agents.append(agent)
    
    def weightedChoice(self, target=None, type=None):
        '''
        Random choice that has weights for each choice in list

        type: Which kind of weighted choice. 'ride, 'arche'
        target: When type is 'ride', the target is the object thats location will be changed
        '''
        weight = list()
        if type == "ride":
            for x in rideNames:
                weight.append(rides[x]["popularity"])
            ride = random.choices(rideNames, weights=weight)[0] 
            target.location = ride
            rides[ride]['reg_queue'].append(target)

        elif type == "arche":
            for x in archeNames:
                weight.append(settings["agent_distribution"][x])
            return random.choices(archeNames, weights=weight)[0]
    def FindWait(self, ride):
        '''
        Finds selected rides wait time

        wait (in hours) = (queue/throughput)
        wait (in minutes) = (queue/throughput) 60
        
        '''
        wait = (len(ride['reg_queue']) / ride['hourly_throughput']) * 60
        print(len(ride['reg_queue']))
        print(wait)
        return wait
  
    def timeChange(self):
        """
        If the time is less than 22, add one to the time and add one to the current wait time of each
        agent. If the time is equal to 22, log the data
        """
        if self.time < 22:
            self.time += 1
            for i in self.agents:
                i.CurrentWait += 1
                i.stay += 1
        elif self.time == 22:
            print("exit")
            self.log("data/log.json")
            sys.exit()

    def event(self):
        percent = settings['hourly_percent'][str(self.time)] / 100
        count = settings['population'] * percent
        self.CreateAgents(count)

        for x in self.agents:
            if x.stay == archeType[x.arche]['stay']:
                self.agents.remove(x)

    def log(self, file):
        """
        It takes a list of agents and writes their data to a json file
        
        :param file: the file to write to
        """
        if makeLog:
            with open("data/template.json") as f:
                form = json.loads(f.read())
            form['version'] = version
            form['ride']['hexagon']['waitTime'] = self.FindWait(rides['hexagon'])
            form['ride']['triangle']['waitTime'] = self.FindWait(rides['triangle'])

            form['population']['total'] = settings['population']

            for x in self.agents:
                form['population'][x.arche] += 1

            if logRewrite == True:

                with open(file, "w") as f:
                    f.write(json.dumps(form, indent=4))
            else:
                with open(file, "a") as f:
                    f.write(json.dumps(form, indent=4))
def main():
    simulation = ParkSim()
    simulation.runSim()

            

#start sim
#if __name__ == '__main__':
main()