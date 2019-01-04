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

    def _create(self, args, metadata):
        metadata['Category'] = args.CATEGORY
        metadata['ModuleID'] = args.MODULE_ID
        if args.user_story:
            metadata['UserStory'] = args.user_story
        if args.title:
            metadata['Title'] = args.title
        if args.jira:
            metadata['Jira'] = args.jira
        if args.parent_assemblies:
            metadata['ParentAssemblies'] = args.parent_assemblies
        self.context.moduleFactory.create(metadata)

    def create_assembly(self,args):
        metadata = {'Type':'assembly'}
        self._create(args, metadata)

    def create_procedure(self,args):
        metadata = {'Type':'procedure'}
        self._create(args, metadata)

    def create_concept(self,args):
        metadata = {'Type':'concept'}
        self._create(args, metadata)

    def create_reference(self,args):
        metadata = {'Type':'reference'}
        self._create(args, metadata)


def add_module_arguments(parser):
    parser.add_argument('CATEGORY', help='Category in which to store this module. Can use / as a separator to define sub-categories')
    parser.add_argument('MODULE_ID', help='Unique ID to identify this module')
    parser.add_argument('-u', '--user-story', help='Text of a user story (enclose in quotes)')
    parser.add_argument('-t', '--title', help='Title of the module (enclose in quotes)')
    parser.add_argument('-j', '--jira', help='Reference to a Jira issue related to the creation of this module')
    parser.add_argument('-p', '--parent-assemblies', help='List of assemblies that include this module, specified as a space-separated list (enclose in quotes)')


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
add_module_arguments(assembly_parser)
assembly_parser.set_defaults(func=tasks.create_assembly)

# Create the sub-parser for the 'procedure' command
procedure_parser = subparsers.add_parser('procedure', help='Generate a procedure module')
add_module_arguments(procedure_parser)
procedure_parser.set_defaults(func=tasks.create_procedure)

# Create the sub-parser for the 'concept' command
concept_parser = subparsers.add_parser('concept', help='Generate a concept module')
add_module_arguments(concept_parser)
concept_parser.set_defaults(func=tasks.create_concept)

# Create the sub-parser for the 'reference' command
reference_parser = subparsers.add_parser('reference', help='Generate a reference module')
add_module_arguments(reference_parser)
reference_parser.set_defaults(func=tasks.create_reference)

# Now, parse the args and call the relevant sub-command
args = parser.parse_args()
args.func(args)
