"""
AMMM Project Heuristics
Alpha Tuning Config attributes validator.
"""

from AMMMGlobals import AMMMException


class ValidateAlphaConfig(object):
    # Validate config attributes read from a DAT file for alpha tuning.

    @staticmethod
    def validate(data):
        # Validate that mandatory input parameters were found
        paramList = ['instancesDirectory', 'fileNamePrefix', 'fileNameExtension', 'numInstances',
                     'numBases', 'minHours', 'maxHours',
                     'numSpecialists', 'minCapacity', 'maxCapacity', 'minFee', 'maxFee',
                     'alphaValues', 'numRunsPerAlpha', 'outputFile', 'verbose']

        for paramName in paramList:
            if paramName not in data.__dict__:
                raise AMMMException('Parameter(%s) has not been specified in Configuration' % str(paramName))

        # Validate instance generation parameters
        instancesDirectory = data.instancesDirectory
        if len(instancesDirectory) == 0:
            raise AMMMException('Value for instancesDirectory is empty')

        fileNamePrefix = data.fileNamePrefix
        if len(fileNamePrefix) == 0:
            raise AMMMException('Value for fileNamePrefix is empty')

        fileNameExtension = data.fileNameExtension
        if len(fileNameExtension) == 0:
            raise AMMMException('Value for fileNameExtension is empty')

        numInstances = data.numInstances
        if not isinstance(numInstances, int) or (numInstances <= 0):
            raise AMMMException('numInstances(%s) has to be a positive integer value.' % str(numInstances))

        numBases = data.numBases
        if not isinstance(numBases, int) or (numBases <= 0):
            raise AMMMException('numBases(%s) has to be a positive integer value.' % str(numBases))

        minHours = data.minHours
        if not isinstance(minHours, int) or (minHours <= 0):
            raise AMMMException('minHours(%s) has to be a positive integer value.' % str(minHours))

        maxHours = data.maxHours
        if not isinstance(maxHours, int) or (maxHours <= 0):
            raise AMMMException('maxHours(%s) has to be a positive integer value.' % str(maxHours))

        if maxHours < minHours:
            raise AMMMException('maxHours(%s) has to be >= minHours(%s).' % (str(maxHours), str(minHours)))

        numSpecialists = data.numSpecialists
        if not isinstance(numSpecialists, int) or (numSpecialists <= 0):
            raise AMMMException('numSpecialists(%s) has to be a positive integer value.' % str(numSpecialists))

        minCapacity = data.minCapacity
        if not isinstance(minCapacity, int) or (minCapacity <= 0):
            raise AMMMException('minCapacity(%s) has to be a positive integer value.' % str(minCapacity))

        maxCapacity = data.maxCapacity
        if not isinstance(maxCapacity, int) or (maxCapacity <= 0):
            raise AMMMException('maxCapacity(%s) has to be a positive integer value.' % str(maxCapacity))

        if maxCapacity < minCapacity:
            raise AMMMException('maxCapacity(%s) has to be >= minCapacity(%s).' % (str(maxCapacity), str(minCapacity)))

        minFee = data.minFee
        if not isinstance(minFee, int) or (minFee <= 0):
            raise AMMMException('minFee(%s) has to be a positive integer value.' % str(minFee))

        maxFee = data.maxFee
        if not isinstance(maxFee, int) or (maxFee <= 0):
            raise AMMMException('maxFee(%s) has to be a positive integer value.' % str(maxFee))

        if maxFee < minFee:
            raise AMMMException('maxFee(%s) has to be >= minFee(%s).' % (str(maxFee), str(minFee)))

        # Validate alpha tuning specific parameters
        data.alphaValues = list(data.alphaValues)
        alphaValues = data.alphaValues
        if len(alphaValues) == 0:
            raise AMMMException('alphaValues list is empty')

        for alpha in alphaValues:
            if not isinstance(alpha, (int, float)) or (alpha < 0.0) or (alpha > 1.0):
                raise AMMMException('Alpha value(%s) must be between 0.0 and 1.0.' % str(alpha))

        numRunsPerAlpha = data.numRunsPerAlpha
        if not isinstance(numRunsPerAlpha, int) or (numRunsPerAlpha <= 0):
            raise AMMMException('numRunsPerAlpha(%s) has to be a positive integer value.' % str(numRunsPerAlpha))

        outputFile = data.outputFile
        if len(outputFile) == 0:
            raise AMMMException('Value for outputFile is empty')

        verbose = data.verbose
        if not isinstance(verbose, bool):
            raise AMMMException('verbose(%s) has to be a boolean value.' % str(verbose))