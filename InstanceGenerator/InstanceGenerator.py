'''
AMMM Project Heuristics
Instance generator.'''

import os, random
from AMMMGlobals import AMMMException


class InstanceGenerator(object):
    # Generate instances based on read configuration.

    def __init__(self, config):
        self.config = config

    def generate(self):
        instancesDirectory = self.config.instancesDirectory
        fileNamePrefix = self.config.fileNamePrefix
        fileNameExtension = self.config.fileNameExtension
        numInstances = self.config.numInstances

        numBases = self.config.numBases
        nPipes = self.config.numPipes
        minHours = self.config.minHours
        maxHours = self.config.maxHours

        numSpecialists = self.config.numSpecialists
        minCapacity = self.config.minCapacity
        maxCapacity = self.config.maxCapacity
        minFee = self.config.minFee
        maxFee = self.config.maxFee

        if not os.path.isdir(instancesDirectory):
            os.makedirs(instancesDirectory)

        if not os.path.isdir(instancesDirectory):
            raise AMMMException('Directory(%s) does not exist' % instancesDirectory)

        for i in range(numInstances):
            instancePath = os.path.join(instancesDirectory, '%s_%d.%s' % (fileNamePrefix, i, fileNameExtension))
            fInstance = open(instancePath, 'w')

            specialistCapacity = [0] * numSpecialists
            for c in range(numSpecialists):
                specialistCapacity[c] = random.randint(minCapacity, maxCapacity)

            specialistFee = [0] * numSpecialists
            for t in range(numSpecialists):
                specialistFee[t] = random.randint(minFee, maxFee)

            pipeHours = [[-1 for _ in range(numBases)] for _ in range(numBases)]
            for a in range(numBases):
                pipeHours[a][a] = 0

            added_edges = 0
            # Generate a random spanning tree to ensure connectivity
            connected_nodes = [0]
            unconnected_nodes = list(range(1, numBases))
            random.shuffle(unconnected_nodes)

            while unconnected_nodes:
                u = random.choice(connected_nodes)
                v = unconnected_nodes.pop()
                value = random.randint(minHours, maxHours)
                pipeHours[u][v] = value
                pipeHours[v][u] = value
                connected_nodes.append(v)
                added_edges += 1

            possible_edges = []
            for k in range(numBases):
                for r in range(k + 1, numBases):
                    if pipeHours[k][r] == -1:
                        possible_edges.append((k, r))
            
            random.shuffle(possible_edges)

            while added_edges < nPipes and possible_edges:
                k, r = possible_edges.pop()
                value = random.randint(minHours, maxHours)
                pipeHours[k][r] = value
                pipeHours[r][k] = value
                added_edges += 1

            fInstance.write('n=%d;\n' % numBases)
            fInstance.write('m=%d;\n' % numSpecialists)

            # translate vector of floats into vector of strings and concatenate that strings separating them by a single space character
            fInstance.write('c=[%s];\n' % (' '.join(map(str, specialistFee))))
            fInstance.write('w=[%s];\n' % (' '.join(map(str, specialistCapacity))))
            fInstance.write('t=[\n')
            for row in pipeHours:
                row_str = ' '.join(map(str, row))
                fInstance.write('[%s]\n' % row_str)
            fInstance.write('];\n')

            fInstance.close()
