from __future__ import print_function

import os, re

import phrasedml
from tesedml import SedReader

class phrasedmlImporter:
    @classmethod
    def fromContent(cls, sedml_str):
        importer = phrasedmlImporter()
        importer.sedml_str = sedml_str
        # test for errors
        result = phrasedml.convertString(sedml_str)
        if result is None:
            # get errors from libsedml
            doc = SedReader().readSedMLFromString(sedml_str)
            if doc.getNumErrors():
                max_len = 100
                message = doc.getError(doc.getNumErrors()-1).getMessage()
                message = message[:max_len] + '...' if len(message) > max_len else message
                raise RuntimeError('Errors reading SED-ML: {}'.format(message))
            else:
                raise RuntimeError('Unable to read SED-ML.')
        return importer

    def __init__(self):
        self.sedml_str = None
        self.sedml_path = None

    def isInRootDir(self, file):
        return os.path.split(file)[0] == ''

    def removeFileExt(self, filename):
        return os.path.splitext(filename)[0]

    def fixModelRefs(self, phrasedml_str):
        ''' Changes all references of type myModel.xml to myModel.'''
        model_ref = re.compile(r'^.*\s*model\s*"([^"]*)"\s*$')
        out_str = ''
        for line in phrasedml_str.splitlines():
            match = model_ref.match(line)
            if match:
                filename = match.group(1)
                if self.isInRootDir(filename):
                    line = line.replace(filename,self.removeFileExt(filename))
            out_str += line+'\n'
        return out_str

    def toPhrasedml(self):
        if self.sedml_str:
            result = phrasedml.convertString(self.sedml_str)
            if result is None:
                raise RuntimeError(phrasedml.getLastError())
            return self.fixModelRefs(phrasedml.getLastPhraSEDML())
        elif self.sedml_path:
            result = phrasedml.convertFile(self.sedml_str)
            if result is None:
                raise RuntimeError(phrasedml.getLastError())
            return self.fixModelRefs(phrasedml.getLastPhraSEDML())
