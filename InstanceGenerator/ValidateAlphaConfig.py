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