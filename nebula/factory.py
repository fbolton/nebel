'''
Created on January 2, 2019

@author fbolton
'''

import os
import sys
import nebula.context

class ModuleFactory:
    def __init__(self, context):
        self.context = context

    def name_of_file(self, metadata):
        storyid = metadata['StoryID']
        type = metadata['Type'].lower()
        if type == 'assembly':
            return 'as_' + storyid + '.adoc'
        elif type == 'procedure':
            return 'p_' + storyid + '.adoc'
        elif type == 'concept':
            return 'c_' + storyid + '.adoc'
        elif type == 'reference':
            return 'r_' + storyid + '.adoc'
        else:
            print 'ERROR: Unknown module Type: ' + str(type)
            sys.exit()

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
            filehandle.write('// Metadata created by nebula\n')
            filehandle.write('//\n')
            for field in self.context.optionalMetadataFields:
                if field in metadata:
                    filehandle.write('// ' + field + ': ' + metadata[field] + '\n')
            filehandle.write('\n')
            filehandle.write("[id='" + metadata['StoryID'] + "']\n")
            templatefile = os.path.join(self.context.templatePath, type + '.adoc')
            with open(templatefile, 'r') as templatehandle:
                filehandle.writelines(templatehandle.readlines())
