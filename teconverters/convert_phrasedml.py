from __future__ import print_function

import os, re

import phrasedml

class phrasedmlImporter:
    @classmethod
    def fromContent(cls, sedml_str):
        importer = phrasedmlImporter()
        importer.sedml_str = sedml_str
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
            phrasedml.convertString(self.sedml_str)
            return self.fixModelRefs(phrasedml.getLastPhraSEDML())
        elif self.sedml_path:
            phrasedml.convertFile(self.sedml_str)
            return self.fixModelRefs(phrasedml.getLastPhraSEDML())
