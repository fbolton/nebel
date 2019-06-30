'''
Created on January 2, 2019

@author fbolton
'''

import re

class NebelContext:
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
            'Jira',
            'Title',
            'IncludeFiles',
            'ConversionStatus',
            'ConversionDate',
            'ConvertedFromFile',
            'ConvertedFromID',
            'ConvertedFromTitle'
        }
        self.allMetadataFields = self.mandatoryMetadataFields | self.optionalMetadataFields
        self.templatePath = ''
        self.moduleFactory = None
        self.attributeDict = {}
        self.bookUrlAttributes = {}

    def initializeFromFile(self, configfile):
        # print 'Initializing from file: ' + configfile
        pass

    def parse_attribute_files(self, filelist):
        regexp = re.compile(r'^:([\w\-]+):\s+(.*)')
        for file in filelist:
            with open(file, 'r') as f:
                for line in f:
                    result = regexp.search(line)
                    if result is not None:
                        name = result.group(1)
                        value = result.group(2).strip()
                        self.attributeDict[name] = [value, None]
        for name in self.attributeDict:
            self.attributeDict[name][1] = self.resolve_raw_attribute_value(self.attributeDict[name][0])
        #for (name,duple) in self.attributeDict.items():
        #    print name + ': ' + duple[0] + ', ' + duple[1]
        self.scan_attributes_for_book_urls()
        # print self.bookUrlAttributes


    def resolve_raw_attribute_value(self, value):
        regexp = re.compile(r'\{([\w\-]+)\}')
        new_value = regexp.sub(self.replace_matching_attribute, value)
        return new_value


    def replace_matching_attribute(self, match_obj):
        name = match_obj.group(1)
        duple = self.attributeDict[name]
        if duple[1] is None:
            duple[1] = self.resolve_raw_attribute_value(duple[0])
        return duple[1]


    def scan_attributes_for_book_urls(self):
        regexp = re.compile(r'https://access.redhat.com/documentation/en-us/([^/]+)/([^/]+)/html-single/([^/]+)/?')
        for name in self.attributeDict:
            resolved_value = self.attributeDict[name][1]
            result = regexp.search(resolved_value)
            if result is not None:
                productpkg = result.group(1)
                version = result.group(2)
                bookslug = result.group(3)
                if productpkg not in self.bookUrlAttributes:
                    self.bookUrlAttributes[productpkg] = {}
                self.bookUrlAttributes[productpkg][bookslug] = name
