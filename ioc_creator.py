import optparse
import os
import fileinput
import uuid
import re
from datetime import datetime


def printIOCHeader(f):
    f.write('<?xml version="1.0" encoding="us-ascii"?>\n')
    f.write('<ioc xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" id="' + f.name.rstrip(".ioc") + '" last-modified="' + datetime.now().replace(microsecond=0).isoformat() + '" xmlns="http://schemas.mandiant.com/2010/ioc">\n')
    f.write('\t<short_description>Bulk (IMPORTER)</short_description>\n')
    f.write('\t<description>Bulk Import - Remember to clean and lint  your IOCs</description>\n')
    f.write('\t<authored_by>BulkImport</authored_by>\n')
    f.write('\t<authored_date>' + datetime.now().replace(microsecond=0).isoformat() + '</authored_date>\n')
    f.write('\t<links />\n')
    f.write('\t<definition>\n')
    f.write('\t\t<Indicator operator="OR" id="' + str(uuid.uuid4()) + '">\n')


def printIOCFooter(f):
    f.write('\t\t</Indicator>\n')
    f.write('\t</definition>\n')
    f.write('</ioc>\n')


def sha256TermPopulate(line, f):
    #for line in fileinput.input(inputfile):
    f.write('\t\t\t<IndicatorItem id="' + str(
        uuid.uuid4()) + '" condition="is">\n\t\t\t\t<Context document="FileItem" search="FileItem/Sha256sum" type="mir" />\n\t\t\t\t<Content type="string">' + line.rstrip() + '</Content>\n\t\t\t</IndicatorItem>\n')


def sha1TermPopulate(line, f):
    #for line in fileinput.input(inputfile):
    f.write('\t\t\t<IndicatorItem id="' + str(
        uuid.uuid4()) + '" condition="is">\n\t\t\t\t<Context document="FileItem" search="FileItem/Sha1sum" type="mir" />\n\t\t\t\t<Content type="string">' + line.rstrip() + '</Content>\n\t\t\t</IndicatorItem>\n')


def md5TermPopulate(line, f):
    #for line in fileinput.input(inputfile):
    f.write('\t\t\t<IndicatorItem id="' + str(
        uuid.uuid4()) + '" condition="is">\n\t\t\t\t<Context document="FileItem" search="FileItem/Md5sum" type="mir" />\n\t\t\t\t<Content type="md5">' + line.rstrip() + '</Content>\n\t\t\t\t</IndicatorItem>\n')


def domainTermPopulate(line, f):
    #for line in fileinput.input(inputfile):
    f.write('\t\t\t<IndicatorItem id="' + str(
        uuid.uuid4()) + '" condition="contains">\n\t\t\t\t<Context document="Network" search="Network/DNS" type="mir" />\n\t\t\t\t<Content type="string">' + line.rstrip() + '</Content>\n\t\t\t\t</IndicatorItem>\n')


def ipTermPopulate(line, f):
    #for line in fileinput.input(inputfile):
    f.write('\t\t\t<IndicatorItem id="' + str(
        uuid.uuid4()) + '" condition="is">\n\t\t\t\t<Context document="PortItem" search="PortItem/remoteIP" type="mir" />\n\t\t\t\t<Content type="IP">' + line.rstrip() + '</Content>\n\t\t\t</IndicatorItem>\n')


def fileTermPopulate(line, f):
    f.write('\t\t\t<IndicatorItem id="' + str(
        uuid.uuid4()) + '" condition="contains">\n\t\t\t\t<Context document="FileItem" search="FileItem/FullPath" type="mir" />\n\t\t\t\t<Content type="string">' + line.rstrip() + '</Content>\n\t\t\t</IndicatorItem>\n')


def fileNamePopulate(line, f):
    f.write('\t\t\t<IndicatorItem id="' + str(
        uuid.uuid4()) + '" condition="contains">\n\t\t\t\t<Context document="FileItem" search="FileItem/FileName" type="mir" />\n\t\t\t\t<Content type="string">' + line.rstrip() + '</Content>\n\t\t\t</IndicatorItem>\n')


def regTermPopulate(line, f):
    f.write('\t\t\t<IndicatorItem id="' + str(
        uuid.uuid4()) + '" condition="contains">\n\t\t\t\t<Context document="RegistryItem" search="RegistryItem/Path" type="mir" />\n\t\t\t\t<Content type="string">' + line.rstrip() + '</Content>\n\t\t\t</IndicatorItem>\n')


def main():
    parser = optparse.OptionParser('usage %prog -f <input file>')
    parser.add_option('-f', dest='tgtFile', type='string', help='specify input file')
    (options, args) = parser.parse_args()
    inputfile = options.tgtFile
    if inputfile == None:
        print parser.usage
        exit(0)
    else:
        try:
            iocname = str(uuid.uuid4())
            f = open(iocname + '.ioc', 'w')
            printIOCHeader(f)
            termlist = []

            for line in fileinput.input(inputfile):
                line = line.rstrip()

                if re.search('[a-fA-F0-9]{32,64}', line):
                    term = re.search('[a-fA-F0-9]{32,64}', line)
                    if term.group(0) not in termlist:
                        termlist.append(term.group(0))
                        if len(term.group(0)) == 64:
                            sha256TermPopulate(term.group(0), f)
                        if len(term.group(0)) == 40:
                            sha1TermPopulate(term.group(0), f)
                        if len(term.group(0)) == 32:
                            md5TermPopulate(term.group(0), f)
                        #print "sha256/1/md5ioc - " + term.group(0)

                if re.search('[a-zA-Z\d-]{1,63}(\.[a-zA-Z]{3})', line):
                    if (re.search('.exe', line, re.IGNORECASE) or re.search('.dll', line, re.IGNORECASE) or re.search('.bat', line, re.IGNORECASE) or re.search('.tmp', line, re.IGNORECASE) or re.search('.rar', line, re.IGNORECASE)):
                        term = re.search('[a-zA-Z\d-]{1,63}(\.[a-zA-Z]{3})', line)
                        if term.group(0) not in termlist:
                            termlist.append(term.group(0))
                            fileNamePopulate(term.group(0), f)

                if re.search('\\\\[a-zA-Z0-9]', line) and not re.search('HKLM', line) and not re.search('HKEY', line) and not re.search('HKCU', line) and not re.search('SYSTEM', line):
                    termssplit = line.split(' ')
                    for termssplits in termssplit:
                        if re.search('\\\\[a-zA-Z0-9]', termssplits):
                            term = termssplits
                            term = re.sub('[a-zA-Z]:', '', term)
                    if term not in termlist:
                        termlist.append(term)
                        fileTermPopulate(term, f)
                        #print "fileioc - " + term

                if re.search('HKLM', line) or re.search('HKCU', line) or re.search('HKEY', line) or re.search('SYSTEM', line):
                    termssplit = line.split(' ')
                    for termssplits in termssplit:
                        if re.search('HKLM', termssplits) or re.search('HKCU', termssplits) or re.search('HKEY', termssplits) or re.search('SYSTEM', termssplits):
                            term = termssplits
                            term = re.sub('HKLM\\\\|HKCU\\\\|hklm\\\\\|hkcu\\\\|SYSTEM\\\\|system\\\\', '', term)
                    if term not in termlist:
                        termlist.append(term)
                        regTermPopulate(term, f)
                        #print "regioc - " + term

                if re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line):
                    term = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
                    if term.group(0) not in termlist:
                        termlist.append(term.group(0))
                        ipTermPopulate(term.group(0), f)
                        #print "ipIOC - " + term.group(0)

                if re.search('[a-zA-Z\d-]{2,63}(\.[a-zA-Z\d-]{2,63}).', line) and not re.search('.exe', line, re.IGNORECASE) and not re.search('.dll', line, re.IGNORECASE) and not re.search('.pdf', line, re.IGNORECASE) and not re.search('.doc', line, re.IGNORECASE):
                    term = re.search('[a-zA-Z\d-]{2,63}(\.[a-zA-Z\d-]{2,63}).', line)
                    termssplit = line.split(' ')

                    for termssplits in termssplit:
                        if not re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', termssplits) and re.search('[a-zA-Z\d-]{2,63}(\.[a-zA-Z\d-]{2,63}).', termssplits):
                            thisterm = termssplits
                            thisterm = thisterm.rstrip('.')
                            if thisterm not in termlist:
                                termlist.append(thisterm)
                                domainTermPopulate(thisterm, f)
                                #print "domainIOC - " + thisterm

            printIOCFooter(f)
            f.close()
        except Exception, e:
            print '[-] ' + str(e)


if __name__ == '__main__':
    main()
