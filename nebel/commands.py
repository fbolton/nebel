'''
Created on January 2, 2019

@author fbolton
'''

import os
import re
import sys
import tempfile
import shutil
import argparse
import nebel.context
import nebel.factory

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

    def create_from(self,args):
        fromfile = args.FROM_FILE
        if not os.path.exists(fromfile):
            print 'ERROR: Cannot find file: ' + fromfile
            sys.exit()
        if fromfile.endswith('.csv'):
            self._create_from_csv(args)
            return
        elif fromfile.endswith('.adoc') and os.path.basename(fromfile).startswith('as'):
            self._create_from_assembly(args)
            return
        else:
            print 'ERROR: Unknown file type [' + fromfile + ']: must end either in .csv or .adoc'
            sys.exit()

    def type_of_file(self, basename):
        if basename.startswith('as_'):
            return 'assembly'
        elif basename.startswith('p_'):
            return 'procedure'
        elif basename.startswith('c_'):
            return 'concept'
        elif basename.startswith('r_'):
            return 'reference'
        else:
            return None

    def moduleid_of_file(self, basename):
        base, ext = os.path.splitext(basename)
        return base.split('_', 1)[1]

    def _create_from_assembly(self,args):
        asfile = args.FROM_FILE
        regexp = re.compile(r'^\s*include::[\./]*modules/([^\[]+)\[[^\]]*\]')
        with open(asfile, 'r') as f:
            for line in f:
                result = regexp.search(line)
                if result is not None:
                    modulefile = result.group(1)
                    category, basename = os.path.split(modulefile)
                    type = self.type_of_file(basename)
                    if type is not None and basename.endswith('.adoc'):
                        print modulefile
                        metadata = {}
                        metadata['Type'] = type
                        metadata['Category'] = category
                        metadata['ModuleID'] = self.moduleid_of_file(basename)
                        metadata['ParentAssemblies'] = asfile
                        self.context.moduleFactory.create(metadata)


    def _scan_assembly_for_includes(self,asfile):
        modulelist = []
        regexp = re.compile(r'^\s*include::[\./]*modules/([^\[]+)\[[^\]]*\]')
        with open(asfile, 'r') as f:
            for line in f:
                result = regexp.search(line)
                if result is not None:
                    modulefile = result.group(1)
                    category, basename = os.path.split(modulefile)
                    type = self.type_of_file(basename)
                    if type is not None and basename.endswith('.adoc'):
                        modulelist.append(os.path.join('modules', modulefile))
        return modulelist


    def _create_from_csv(self,args):
        csvfile = args.FROM_FILE
        with open(csvfile, 'r') as filehandle:
            # First line should be the column headings
            headings = filehandle.readline().strip().replace(' ','')
            headinglist = headings.split(',')
            # Check plausibility of headinglist
            if ('Category' not in headinglist) or ('ModuleID' not in headinglist):
                print 'ERROR: CSV file does not have correct format'
                sys.exit()
            completefile = filehandle.read()
            lines = self.smart_split(completefile, '\n', preserveQuotes=True)
            for line in lines:
                fieldlist = self.smart_split(line.strip())
                metadata = dict(zip(headinglist, fieldlist))
                # Skip rows with Implement field set to 'no'
                if ('Implement' in metadata) and (metadata['Implement'].lower() == 'no'):
                    print 'INFO: Skipping unimplemented module/assembly: ' + metadata['ModuleID']
                    continue
                # Weed out irrelevant metadata entries
                for field,value in metadata.items():
                    if (value == '') or (field not in self.context.allMetadataFields):
                        del(metadata[field])
                self.context.moduleFactory.create(metadata)


    def smart_split(self, line, splitchar=',', preserveQuotes=False):
        list = []
        isInQuotes = False
        currfield = ''
        for ch in line:
            if not isInQuotes:
                if ch == splitchar:
                    list.append(currfield)
                    currfield = ''
                    continue
                if ch == '"':
                    isInQuotes = True
                    if not preserveQuotes:
                        continue
                currfield += ch
            else:
                if ch == '\r' or ch == '\n':
                    # Eliminate newlines from quoted fields
                    continue
                if ch == '"':
                    isInQuotes = False
                    if not preserveQuotes:
                        continue
                currfield += ch
        return list


    def book(self,args):
        if args.create:
            # Create book and (optionally) add categories
            self._book_create(args)
        elif args.category_list:
            # Add categories
            self._book_categories(args)
        else:
            print 'ERROR: No options specified'


    def _book_create(self,args):
        bookdir = args.BOOK_DIR
        if os.path.exists(bookdir):
            print 'ERROR: Book directory already exists: ' + bookdir
            sys.exit()
        os.mkdir(bookdir)
        os.mkdir(os.path.join(bookdir, 'assemblies'))
        os.mkdir(os.path.join(bookdir, 'modules'))
        os.mkdir(os.path.join(bookdir, 'images'))
        os.symlink(os.path.join('..', 'shared', 'attributes.adoc'), os.path.join(bookdir, 'attributes.adoc'))
        os.symlink(
            os.path.join('..', 'shared', 'attributes-links.adoc'),
            os.path.join(bookdir, 'attributes-links.adoc')
        )
        templatefile = os.path.join(self.context.templatePath, 'master.adoc')
        shutil.copyfile(templatefile, os.path.join(bookdir, 'master.adoc'))
        templatefile = os.path.join(self.context.templatePath, 'master-docinfo.xml')
        shutil.copyfile(templatefile, os.path.join(bookdir, 'master-docinfo.xml'))
        # Add categories (if specified)
        if args.category_list:
            self._book_categories(args)


    def _book_categories(self, args):
        bookdir = args.BOOK_DIR
        if not os.path.exists(bookdir):
            print 'ERROR: Book directory does not exist: ' + bookdir
            sys.exit()
        imagesdir = os.path.join(bookdir, 'images')
        modulesdir = os.path.join(bookdir, 'modules')
        assembliesdir = os.path.join(bookdir, 'assemblies')
        if (not os.path.exists(imagesdir)) or (not os.path.exists(modulesdir)) or (not os.path.exists(assembliesdir)):
            print 'ERROR: Book directory must have the subdirectories images, modules, and assemblies'
            sys.exit()
        categorylist = args.category_list.split(',')
        map(str.strip, categorylist)
        for category in categorylist:
            os.symlink(
                os.path.join('..', '..', 'images', category),
                os.path.join(imagesdir, category)
            )
            os.symlink(
                os.path.join('..', '..', 'modules', category),
                os.path.join(modulesdir, category)
            )
            os.symlink(
                os.path.join('..', '..', 'assemblies', category),
                os.path.join(assembliesdir, category)
            )


    def update(self,args):
        if args.parent_assemblies:
            self._update_parent_assemblies(args)
        else:
            print 'ERROR: Missing required option(s)'


    def _update_parent_assemblies(self,args):
        # Get the list of assemblies to scan
        assemblylist = []
        categoryset = set()
        if args.category_list:
            categoryset = set(args.category_list.split(','))
            map(str.strip, categoryset)
        else:
            cwd = os.getcwd()
            os.chdir('assemblies')
            for root, dirs, files in os.walk(os.curdir):
                for dir in dirs:
                    categoryset.add(os.path.normpath(os.path.join(root, dir)))
            os.chdir(cwd)
        for category in categoryset:
            assemblycategorydir = os.path.join('assemblies', category)
            if os.path.exists(assemblycategorydir):
                for entry in os.listdir(assemblycategorydir):
                    pathname = os.path.join('assemblies', category, entry)
                    if os.path.isfile(pathname):
                        assemblylist.append(pathname)
        # Create dictionary of modules included by assemblies
        assemblyincludes = {}
        for assemblyfile in assemblylist:
            assemblyincludes[assemblyfile] = self._scan_assembly_for_includes(assemblyfile)
        # print assemblyincludes
        # Invert dictionary
        parentassemblies = {}
        for assemblyfile in assemblyincludes:
            for modulefile in assemblyincludes[assemblyfile]:
                if modulefile not in parentassemblies:
                    parentassemblies[modulefile] = [assemblyfile]
                else:
                    parentassemblies[modulefile].append(assemblyfile)
        # print parentassemblies
        # Update the ParentAssemblies metadata in each of the module files
        metadata = {}
        for modulefile in parentassemblies:
            metadata['ParentAssemblies'] = ','.join(parentassemblies[modulefile])
            self.update_metadata(modulefile, metadata)


    def update_metadata(self, file, metadata):
        print 'Updating metadata for file: ' + file
        regexp = re.compile(r'^\s*//\s*(\w+)\s*:.*')
        # Scan file for pre-existing metadata settings
        preexisting = set()
        with open(file) as scan_file:
            for line in scan_file:
                # Detect end of metadata section
                if line.startswith('='):
                    break
                result = regexp.search(line)
                if result is not None:
                    metaname = result.group(1)
                    if metaname in self.context.optionalMetadataFields:
                        preexisting.add(metaname)
        properties2add = (set(metadata.keys()) & self.context.optionalMetadataFields) - preexisting
        properties2update = set(metadata.keys()) & self.context.optionalMetadataFields & preexisting
        # Create temp file
        fh, abs_path = tempfile.mkstemp()
        with os.fdopen(fh, 'w') as new_file:
            with open(file) as old_file:
                START_OF_METADATA = False
                END_OF_METADATA = False
                NEW_PROPERTIES_ADDED = False
                for line in old_file:
                    # Detect start of metadata section
                    if line.startswith('// Metadata'):
                        new_file.write(line)
                        START_OF_METADATA = True
                        continue
                    # Detect end of metadata section
                    if line.startswith('='):
                        END_OF_METADATA = True
                    if START_OF_METADATA and not END_OF_METADATA:
                        if not NEW_PROPERTIES_ADDED:
                            for metaname in properties2add:
                                new_file.write('// ' + metaname + ': ' + metadata[metaname] + '\n')
                            NEW_PROPERTIES_ADDED = True
                        result = regexp.search(line)
                        if result is not None:
                            metaname = result.group(1)
                            if metaname in properties2update:
                                new_file.write('// ' + metaname + ': ' + metadata[metaname] + '\n')
                                continue
                    new_file.write(line)
        # Remove original file
        os.remove(file)
        # Move new file
        shutil.move(abs_path, file)


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
if not os.path.exists('nebel.cfg'):
  print 'WARN: No nebel.cfg file found in this directory.'
  sys.exit()
context = nebel.context.NebelContext()
context.initializeFromFile('nebel.cfg')
this_script_path = os.path.dirname(os.path.abspath(__file__))
context.templatePath = os.path.abspath(os.path.join(this_script_path, '..', 'template'))
context.moduleFactory = nebel.factory.ModuleFactory(context)
tasks = Tasks(context)

# Create the top-level parser
parser = argparse.ArgumentParser(prog='nebel')
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

# Create the sub-parser for the 'create-from' command
create_parser = subparsers.add_parser('create-from', help='Create multiple assemblies/modules from a CSV file or from an assembly file')
create_parser.add_argument('FROM_FILE', help='Can be either a comma-separated values (CSV) file (ending with .csv) or an assembly file (ending with .adoc)')
create_parser.set_defaults(func=tasks.create_from)

# Create the sub-parser for the 'book' command
book_parser = subparsers.add_parser('book', help='Create and manage book directories')
book_parser.add_argument('BOOK_DIR', help='The book directory')
book_parser.add_argument('--create', help='Create a new book directory', action='store_true')
book_parser.add_argument('-c', '--category-list', help='Comma-separated list of categories to add to book (enclose in quotes)')
book_parser.set_defaults(func=tasks.book)

# Create the sub-parser for the 'update' command
update_parser = subparsers.add_parser('update', help='Update metadata in modules and assemblies')
update_parser.add_argument('-p','--parent-assemblies', help='Update ParentAssemblies property in modules and assemblies', action='store_true')
update_parser.add_argument('-c', '--category-list', help='Apply update only to this comma-separated list of categories (enclose in quotes)')
update_parser.set_defaults(func=tasks.update)


# Now, parse the args and call the relevant sub-command
args = parser.parse_args()
args.func(args)
