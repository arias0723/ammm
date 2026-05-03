'''
AMMM Project Heuristics
BRKGA Decoder for the pipe-destruction problem.
Chromosome: one gene per base; gene < 0.5 => group 0, else group 1.
'''

from AMMMGlobals import AMMMException
from Heuristics.BRKGA_fwk.decoder import _Decoder


class Decoder(_Decoder):
    def __init__(self, config, instance):
        config.__dict__['numGenes'] = int(instance.getNumBases())
        config.__dict__['numIndividuals'] = int(config.IndividualsMultiplier * config.numGenes)
        config.__dict__['numElite'] = int(config.eliteProp * config.numIndividuals)
        config.__dict__['numMutants'] = int(config.mutantProp * config.numIndividuals)
        config.__dict__['numCrossover'] = int(config.numIndividuals - config.numElite - config.numMutants)
        super().__init__(config, instance)

    def decodeIndividual(self, chromosome):
        if len(chromosome) != self.instance.getNumBases():
            raise AMMMException("Error: chromosome length does not match number of bases")

        solution = self.instance.createSolution()

        for i in range(len(chromosome)):
            solution.setGroup(i, 0 if chromosome[i] < 0.5 else 1)

        if not solution.isValidPartition():
            solution.makeInfeasible()
            return solution, solution.getFitness()

        solution.computeCutPipes()
        feasible = solution.assignSpecialistsGreedy()
        if not feasible:
            solution.makeInfeasible()

        return solution, solution.getFitness()