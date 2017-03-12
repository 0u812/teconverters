from __future__ import print_function

import os, re

from tecombine import CombineArchive
from .convert_phrasedml import phrasedmlImporter

class omexImporter:
    @classmethod
    def fromFile(cls, path):
        """ Initialize from a file location.

        :param path: The path to the omex file
        """
        omex = CombineArchive()
        if not omex.initializeFromArchive(path):
            raise IOError('Could not read COMBINE archive.')
        return omexImporter(omex)

    def __init__(self, omex):
        """ Initialize from a CombineArchive instance
        (https://sbmlteam.github.io/libCombine/html/class_combine_archive.html).

        :param omex: A CombineArchive instance
        """
        self.omex = omex

        self.n_master_sedml = 0
        self.sedml_entries = []
        # match sedml, any level/ver
        self.sedml_fmt_expr = re.compile(r'^http[s]?://identifiers\.org/combine\.specifications/sed-ml.*$')

        self.sbml_entries = []
        # match sbml, any level/ver
        self.sbml_fmt_expr = re.compile(r'^http[s]?://identifiers\.org/combine\.specifications/sbml.*$')

        # Prevents %antimony and %phrasedml headers from
        # being written when all entries are in root of archive
        # and no sedml entries have master=False.
        self.headerless = True
        for entry in self.getEntries():
            # shouldn't happen
            if not entry.isSetLocation():
                raise RuntimeError('Entry has no location')
            if not self.isInRootDir(entry.getLocation()):
                # must write headers to specify entry paths
                self.headerless = False
            # count number of master sedml entries
            if self.sedml_fmt_expr.match(entry.getFormat()) != None:
                if entry.isSetMaster() and entry.getMaster():
                    self.n_master_sedml += 1
                    if self.n_master_sedml > 1:
                        # must write headers to specify non-master sedml
                        self.headerless = False
                    self.sedml_entries.append(entry)
            elif self.sbml_fmt_expr.match(entry.getFormat()) != None:
                self.sbml_entries.append(entry)

    def getEntries(self):
        for k in range (self.omex.getNumEntries()):
            yield self.omex.getEntry(k)

    def isInRootDir(self, path):
        """ Returns true if path specififies a root location like ./file.ext."""
        return os.path.split(path)[0] == ''

    def toInlineOmex(self):
        """ Converts a COMBINE archive into an inline phrasedml / antimony string.

        :returns: A string with the inline phrasedml / antimony source
        """
        # convert sedml entries to phrasedml
        for entry in self.sedml_entries:
            if self.headerless:
                # the "header" is just a comment
                phrasedml_header = '// Converted from {}\n'.format(os.path.basename(entry.getLocation()))
            else:
                phrasedml_header = '%phrasedml {}'.format(entry.getLocation())
                if entry.isSetMaster() and entry.getMaster():
                    phrasedml_header += ' --master=True'
            phrasedml = phrasedml_header + phrasedmlImporter().fromContent(self.omex.extractEntryToString(entry.getLocation())).toPhrasedml()

        return phrasedml
