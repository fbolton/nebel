'''
Created on January 2, 2019

@author fbolton
'''

import os
import sys
import nebel.context

class ModuleFactory:
    def __init__(self, context):
        self.context = context

    def lreplace(self, pat, sub, target):
        if target.startswith(pat):
            return sub + target[len(pat):]
        else:
            return target

    def name_of_file(self, metadata):
        moduleid = metadata['ModuleID']
        type = metadata['Type'].lower()
        if type == 'assembly':
            return 'as_' + moduleid + '.adoc'
        elif type == 'procedure':
            return 'p_' + moduleid + '.adoc'
        elif type == 'concept':
            return 'c_' + moduleid + '.adoc'
        elif type == 'reference':
            return 'r_' + moduleid + '.adoc'
        else:
            print 'ERROR: Unknown module Type: ' + str(type)
            sys.exit()

    def normalize_filename(self, filename):
        normalized = filename.replace('_', '-')
        normalized = self.lreplace('as-', 'as_', normalized)
        normalized = self.lreplace('p-', 'p_', normalized)
        normalized = self.lreplace('c-', 'c_', normalized)
        normalized = self.lreplace('r-', 'r_', normalized)
        return normalized


    def module_dirpath(self, metadata):
        category = metadata['Category']
        type = metadata['Type'].lower()
        if type == 'assembly':
            return os.path.join('assemblies', category)
        elif type in ['procedure', 'concept', 'reference']:
            return os.path.join('modules', category)
        else:
            print 'ERROR: Unknown module Type: ' + str(type)
            sys.exit()

    def module_or_assembly_path(self, metadata):
        return os.path.join(self.module_dirpath(metadata), self.name_of_file(metadata))

    def create(self, metadata):
        type = metadata['Type'].lower()
        filename = self.name_of_file(metadata)
        dirpath = self.module_dirpath(metadata)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        filepath = os.path.join(dirpath, filename)
        if os.path.exists(filepath):
            print 'INFO: File already exists, skipping: ' + filename
            return
        with open(filepath, 'w') as filehandle:
            filehandle.write('// Metadata created by nebel\n')
            filehandle.write('//\n')
            for field in self.context.optionalMetadataFields:
                if (field in metadata) and (field.lower() != 'title') and (field.lower() != 'includefiles'):
                    filehandle.write('// ' + field + ': ' + metadata[field] + '\n')
            filehandle.write('\n')
            filehandle.write('[id="' + metadata['ModuleID'] + '"]\n')
            templatefile = os.path.join(self.context.templatePath, type + '.adoc')
            with open(templatefile, 'r') as templatehandle:
                if 'Title' in metadata:
                    # Replace the title from the first line of the template
                    templatehandle.readline()
                    filehandle.write('= ' + metadata['Title'] + '\n')
                # Process the rest of the file
                for line in templatehandle:
                    if line.startswith('//INCLUDE') and ('IncludeFiles' in metadata):
                        for filepath in metadata['IncludeFiles'].split(','):
                            filehandle.write('include::../../' + filepath + '[leveloffset=+1]\n\n')
                    else:
                        filehandle.write(line)
