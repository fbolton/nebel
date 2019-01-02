'''
Created on January 2, 2019

@author fbolton
'''

import nebula.context

class ModuleFactory:
    def __init__(self, context):
        self.context = context

    def create_assembly(self):
        print 'Called ModuleFactory.create_assembly()'

    def create_procedure(self):
        print 'Called ModuleFactory.create_procedure()'

    def create_concept(self):
        print 'Called ModuleFactory.create_concept()'

    def create_reference(self):
        print 'Called ModuleFactory.create_reference()'
