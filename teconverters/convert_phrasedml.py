from __future__ import print_function
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

    def fixModelRefs(self, phrasedml_str):
        ''' Changes all references of type myModel.xml to myModel.'''
        return phrasedml_str

    def toPhrasedml(self):
        if self.sedml_str:
            phrasedml.convertString(self.sedml_str)
            return self.fixModelRefs(phrasedml.getLastPhraSEDML())
        elif self.sedml_path:
            phrasedml.convertFile(self.sedml_str)
            return self.fixModelRefs(phrasedml.getLastPhraSEDML())
