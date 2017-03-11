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

    def toInlineOmex(self):
        """ Converts a COMBINE archive into an inline phrasedml / antimony string.

        :returns: A string with the inline phrasedml / antimony source
        """
        n_master_sedml = 0
        # match sedml, any level
        sedml_fmt_expr = re.compile(r'^http[s]?://identifiers\.org/combine\.specifications/sed-ml.*$')
        n_sbml = 0
        # match sbml, any level
        sbml_fmt_expr = re.compile(r'^http[s]?://identifiers\.org/combine\.specifications/sbml.*$')
        for k in range (self.omex.getNumEntries()):
            entry = self.omex.getEntry(k);
            if sedml_fmt_expr.match(entry.getFormat()) != None:
                if entry.isSetMaster() and entry.getMaster():
                    n_master_sedml += 1
                    if n_master_sedml > 1:
                        raise RuntimeError('Multiple "master" SED-ML files')
                            # 'Please file a bug at https://github.com/sys-bio/tellurium/issues and include the file you are trying to import.')
                    phrasedml_header = '// Converted from {}'.format(os.path.basename(entry.getLocation()))
                    phrasedml = phrasedmlImporter().fromContent(self.omex.extractEntryToString(entry.getLocation())).toPhrasedml()

        return phrasedml
