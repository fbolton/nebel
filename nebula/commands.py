'''
Created on January 2, 2019

@author fbolton
'''

import os
import sys
import argparse
import nebula.context
import nebula.factory

class Tasks:
    def __init__(self, context):
        self.context = context

    def create_assembly(self,args):
        self.context.moduleFactory.create(
            {'Type':'assembly', 'StoryID':'story-for-assembly', 'Category':'test',
             'UserStory':'As a user, I want to do the thing so that I can do the other thing'}
        )

    def create_procedure(self,args):
        self.context.moduleFactory.create(
            {'Type': 'procedure', 'StoryID': 'story-for-procedure', 'Category':'test',
             'UserStory':'As a user, I want to do the thing so that I can do the other thing'}
        )

    def create_concept(self,args):
        self.context.moduleFactory.create(
            {'Type': 'concept', 'StoryID': 'story-for-concept', 'Category':'test',
             'UserStory':'As a user, I want to do the thing so that I can do the other thing'}
        )

    def create_reference(self,args):
        self.context.moduleFactory.create(
            {'Type': 'reference', 'StoryID': 'story-for-reference', 'Category':'test',
             'UserStory':'As a user, I want to do the thing so that I can do the other thing'}
        )


# MAIN CODE - PROGRAM STARTS HERE!
# --------------------------------

# Basic initialization
if not os.path.exists('nebula.cfg'):
  print 'WARN: No nebula.cfg file found in this directory.'
  sys.exit()
context = nebula.context.NebulaContext()
context.initializeFromFile('nebula.cfg')
this_script_path = os.path.dirname(os.path.abspath(__file__))
context.templatePath = os.path.abspath(os.path.join(this_script_path, '..', 'template'))
context.moduleFactory = nebula.factory.ModuleFactory(context)
tasks = Tasks(context)

# Create the top-level parser
parser = argparse.ArgumentParser(prog='nebula')
subparsers = parser.add_subparsers()

# Create the sub-parser for the 'assembly' command
assembly_parser = subparsers.add_parser('assembly', help='Generate an assembly')
# assembly_parser.add_argument('-m', '--modtime', help='Generate any books modified after the specified time')
# assembly_parser.add_argument('-s', '--sincelastcommit', help='Generate any books modified since the last commit',
# action='store_true')
# assembly_parser.add_argument('-p', '--profile', help='Specify the build profile')
assembly_parser.set_defaults(func=tasks.create_assembly)

# Create the sub-parser for the 'procedure' command
procedure_parser = subparsers.add_parser('procedure', help='Generate a procedure module')
procedure_parser.set_defaults(func=tasks.create_procedure)

# Create the sub-parser for the 'concept' command
concept_parser = subparsers.add_parser('concept', help='Generate a concept module')
concept_parser.set_defaults(func=tasks.create_concept)

# Create the sub-parser for the 'reference' command
reference_parser = subparsers.add_parser('reference', help='Generate a reference module')
reference_parser.set_defaults(func=tasks.create_reference)

# Now, parse the args and call the relevant sub-command
args = parser.parse_args()
args.func(args)
