'''
Created on January 2, 2019

@author fbolton
'''

class NebulaContext:
    def __init__(self):
        self.mandatoryMetadataFields = {
            'Type',
            'Category',
            'ModuleID'
        }
        self.optionalMetadataFields = {
            'ParentAssemblies',
            'UserStory',
            'VerifiedInVersion',
            'QuickstartID',
            'Jira'
        }
        self.allMetadataFields = self.mandatoryMetadataFields | self.optionalMetadataFields
        self.templatePath = ''
        self.moduleFactory = None

    def initializeFromFile(self, configfile):
        # print 'Initializing from file: ' + configfile
        pass
