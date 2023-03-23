from lxml.etree import CDATA
import lxml.etree as ET
from datetime import datetime
from dateutil import parser
import pytz


def tsConverter(s):
    timeorigin = parser.parse(s)
    timediff = timeorigin - datetime(1970, 1, 1, tzinfo=pytz.utc)
    return round(timediff.total_seconds() * 1000)


def sub(parentItem, tag, content=None):
    element = ET.SubElement(parentItem, tag)
    if content:
        element.text = stringWrapper(tag, content)
    return element

    
# Can not accept structure contains 'array of array'
def recparse(parentItem, obj):
    t = type(obj)
    if t is dict:
        for name, value in obj.items():
            subt = type(value)
            # print(name, value)
            if subt is dict:
                thisItem = ET.SubElement(parentItem, name)
                recparse(thisItem, value)
            elif subt is list:
                for item in value:
                    if  type(item) is ET._Element:
                        thisItem = parentItem.append(item)
                    else:
                        thisItem = ET.SubElement(parentItem, name)
                        recparse(thisItem, item)
            elif subt is ET._Element:
                thisItem = parentItem.append(value)
            elif subt is not str:
                thisItem = ET.SubElement(parentItem, name)
                thisItem.text = str(value)
            else:
                thisItem = ET.SubElement(parentItem, name)
                thisItem.text = stringWrapper(name, value)
    elif t is list:
        raise Exception('unsupported structure')
    elif t is str:
        parentItem.text = obj
    return


def stringWrapper(name, s):
    if name in ['title', 'content', 'author', 'writer', 'brief']:
        return CDATA(s)
    else:
        return s