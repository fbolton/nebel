'''
Created on January 2, 2019

@author fbolton
'''

from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import re

class ModuleFactory:
    def __init__(self, context):
        self.context = context

    def lreplace(self, pat, sub, target):
        if target.startswith(pat):
            return sub + target[len(pat):]
        else:
            return target

    def name_of_file(self, metadata):
        type = metadata['Type'].lower()
        moduleid = metadata['ModuleID']
        if not moduleid.endswith('{context}'):
            coremoduleid = moduleid
        else:
            tmpstr = moduleid.replace('{context}', '')
            regexp = re.compile(r'[_\-]+$')
            result = regexp.search(tmpstr)
            if result is None:
                print('ERROR: Cannot parse ModuleID: ' + moduleid)
                sys.exit()
            coremoduleid = regexp.sub('', tmpstr)
        coremoduleid = coremoduleid.replace('_', '-')
        if type == 'assembly' and not coremoduleid.startswith(self.context.ASSEMBLY_PREFIX):
            return self.context.ASSEMBLY_PREFIX + coremoduleid + '.adoc'
        elif type == 'procedure' and not coremoduleid.startswith(self.context.PROCEDURE_PREFIX):
            return self.context.PROCEDURE_PREFIX + coremoduleid + '.adoc'
        elif type == 'concept' and not coremoduleid.startswith(self.context.CONCEPT_PREFIX):
            return self.context.CONCEPT_PREFIX + coremoduleid + '.adoc'
        elif type == 'reference' and not coremoduleid.startswith(self.context.REFERENCE_PREFIX):
            return self.context.REFERENCE_PREFIX + coremoduleid + '.adoc'
        else:
            # For a generic module of unknown type, do not attach a prefix
            return coremoduleid + '.adoc'

    def normalize_filename(self, filename):
        normalized = filename.replace('_', '-')
        return normalized


    def module_dirpath(self, metadata):
        category = metadata['Category']
        type = metadata['Type'].lower()
        if type == 'assembly':
            return os.path.join(self.context.ASSEMBLIES_DIR, category)
        elif type in ['procedure', 'concept', 'reference', 'module']:
            return os.path.join(self.context.MODULES_DIR, category)
        else:
            print('ERROR: Unknown module Type: ' + str(type))
            sys.exit()

    def module_or_assembly_path(self, metadata):
        return os.path.join(self.module_dirpath(metadata), self.name_of_file(metadata))

    def create(self, metadata, filecontents = None, clobber = False):
        type = metadata['Type'].lower()
        filename = self.name_of_file(metadata)
        dirpath = self.module_dirpath(metadata)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        filepath = os.path.join(dirpath, filename)
        if os.path.exists(filepath) and not clobber:
            print('INFO: File already exists, skipping: ' + filename)
            return filepath
        with open(filepath, 'w') as filehandle:
            filehandle.write('// Metadata created by nebel\n')
            filehandle.write('//\n')
            for field in self.context.optionalMetadataFields:
                if (field in metadata) and (field.lower() != 'title') and (field.lower() != 'includefiles'):
                    filehandle.write('// ' + field + ': ' + metadata[field] + '\n')
            filehandle.write('\n')
            filehandle.write('[id="' + metadata['ModuleID'] + '"]\n')
            if filecontents is not None:
                # If filecontents is provided, write the contents verbatim
                filehandle.write('= ' + metadata['Title'] + '\n')
                filehandle.writelines(filecontents)
                return filepath
            elif type == 'module':
                # Cannot use a template, because we do not know the exact module type
                filehandle.write('= ' + metadata['Title'] + '\n')
                return filepath
            else:
                # Generate contents from template
                templatefile = os.path.join(self.context.templatePath, type + '.adoc')
                with open(templatefile, 'r') as templatehandle:
                    if 'Title' in metadata:
                        # Replace the title from the first line of the template
                        templatehandle.readline()
                        filehandle.write('= ' + metadata['Title'] + '\n')
                    # Process the rest of the file
                    for line in templatehandle:
                        if line.startswith('//INCLUDE') and ('IncludeFiles' in metadata):
                            for includedfilepath in metadata['IncludeFiles'].split(','):
                                filehandle.write('include::' + os.path.relpath(includedfilepath, dirpath) + '[leveloffset=+1]\n\n')
                        else:
                            filehandle.write(line)
        return filepath
