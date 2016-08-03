import xml.etree.ElementTree as x


def json_to_xml(record, element):
    for k in record.keys():
        if k == 'resourceType':
            continue
        e = x.SubElement(element, k)
        if type(record[k]) == list:
            if len(record[k]) == 1:
                record[k] = record[k][0]
            else:
                for item in record[k]:
                    e = json_to_xml(item, e)
                continue
        if type(record[k]) == dict:
            e = json_to_xml(record[k], e)
            continue
        e.set('value', str(record[k]))
    return element
