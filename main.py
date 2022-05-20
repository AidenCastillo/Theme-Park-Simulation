from cmath import inf
import os
import sys
os.chdir(os.getcwd())
total = 0
import json
import random
from cog import *
import logging
logging.basicConfig(filename='report.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.DEBUG)

with open("variables/settings.json") as f:
    settings = json.loads(f.read())
    settings = settings[version]
with open("variables/archetype.json") as f:
    archeType = json.loads(f.read())
    archeNames = []
    for x in archeType:
        archeNames.append(x)
with open("variables/ride.json") as f:
    rides = json.loads(f.read())
    rideNames = []
    for x in rides:
        rideNames.append(x)
class person:
    def __init__(self, arche, location, exp_ability=False):
        self.tag = 0
        self.arche = arche
        self.location = location
        self.CurrentWait = 0
        self.stay = 0
        self.exp_ability = exp_ability

class ParkSim:
    def __init__(self):
        '''
        Seed: Randomizer seed

        Time: Runs on military time for simplicity
        '''
        self.seed = settings['seed']
        self.time = 7
        self.agents = list()

    def runSim(self):
        self.CreateAgents(100)
        while True:
            self.event()
            self.timeChange()
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
                        try:
                            rides[i.location]['reg_queue'].remove(i)
                        except:
                            rides[i.location]['exp_queue'].remove(i)
                        self.weightedChoice(i, "ride")
                        i.CurrentWait = 0

            self.FindWait(rides['hexagon'])
            
    
    def CreateAgents(self, count):
        '''
        Initiates the person class and places in `self.agents`

        Count: Number of Agents to create
        '''
        
        for i in range(int(count)):
            agent = person(self.weightedChoice(type="arche"), "Hub", self.weightedChoice(type="exp_ability"))
            self.agents.append(agent)
        global total
        total += count
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
            if target.exp_ability == False:
                rides[ride]['reg_queue'].append(target)
            else:
                if self.FindWait(rides[ride])[1] > 1:
                    rides[ride]['exp_queue'].append(target)
                else:
                    rides[ride]['reg_queue'].append(target)

        elif type == "arche":
            for x in archeNames:
                weight.append(settings["agent_distribution"][x])
            return random.choices(archeNames, weights=weight)[0]
        
        elif type == "exp_ability":
            weight.append(settings['exp_ability_pct'])
            weight.append(1 - settings['exp_ability_pct'])
            return random.choices([True, False], weights=weight)[0]
    def FindWait(self, ride):
        '''
        Finds selected rides wait time

        wait (in hours) = (queue/throughput)
        wait (in minutes) = (queue/throughput) 60
        
        '''
        
        expRatio = ride['hourly_throughput'] * ride['expedited_queue_ratio']
        regRatio = ride['hourly_throughput'] - expRatio
        regWait = (len(ride['reg_queue']) / regRatio) * 60
        expWait = (len(ride['exp_queue']) / expRatio) * 60
        wait = (regWait + expWait) / 2
        return wait, regWait, expWait
  
    def timeChange(self):
        """
        If the time is less than 22, add one to the time and add one to the current wait time of each
        agent. If the time is equal to 22, log the data
        """
        if self.time < 22:
            self.time += 1
            logging.info('Time: %s, Population: %a', self.time, total)
            for i in self.agents:
                i.CurrentWait += 1
                i.stay += 1
            if self.time > 8:
                for i in rides:
                    ratio = rides[i]['expedited_queue_ratio']
                    n = int(rides[i]['hourly_throughput'] * ratio)
                    while n > 0:
                        try:
                            rides[i]['exp_queue'] = rides[i]['exp_queue'].remove(0)
                        except:
                            try:
                                rides[i]['reg_queue'] = rides[i]['reg_queue'].remove(0)
                            except:
                                break
                        
                        n-=1
                for i in self.agents:                    
                    if i.location == 'Hub':
                        continue
                    elif i not in rides[i.location]['exp_queue'] and rides[i.location]['reg_queue']:
                        i.location = 'Hub'
                
        elif self.time == 22:
            print("exit")
            self.log("data/log.json")
            sys.exit()

    def event(self):
        if self.time == 7:
            pass
        else:
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
            form['population']['total'] = settings['population']
            
            for x in rides:
                form['ride'][x]['waitTime'] = self.FindWait(rides[x])[0]
                form['ride'][x]['reg_queue'] = self.FindWait(rides[x])[1]
                form['ride'][x]['exp_queue'] = self.FindWait(rides[x])[2]
            
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