from glob import glob
from json_to_xml import json_to_xml
from xml.etree.ElementTree import Element, tostring
import json

path = '/Users/lawrence.phillips/synth_dat/generated_data/'

extns = ['patients/', 'family_questionnaires/', 'risk_questionnaires/',
         'conditions/', 'family_histories/', 'obersvations/',
         'diagnostic_reports/']

paths = [path + extn for extn in extns]

for p in paths:
    for rp in glob(p+'*'):
        record = json.load(open(rp))
        el = Element(record['resourceType'])
        el.set('xmlns', 'http://hl7.org/fhir')
        el = json_to_xml(record, el)
        with open(rp.replace('json', 'xml'), 'w') as f:
            f.write(str(tostring(el)))
