# Veriler doviz.com adresinden alınmaktadır.
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
import sys

if (sys.version_info[0] < 3):
    import urllib2
    import urllib
    import HTMLParser
else:
    from html.parser import HTMLParser
    import html.parser
    import urllib.request
    import urllib.parse

agent = {'User-Agent': "Mozilla/5.0 (Android 9; Mobile; rv:67.0.3) Gecko/67.0.3 Firefox/67.0.3"}


class MyHTMLParser(HTMLParser):
    taglar = [{"tag_s":[], "attrs":[], "tag_e":[], "data":""}]

    def handle_starttag(self, tag, attrs):
        self.taglar.append({})
        self.taglar[-1]["tag_s"] = tag
        self.taglar[-1]["attrs"] = attrs

    def handle_endtag(self, tag):
        self.taglar[-1]["tag_e"] = tag
        
    def handle_data(self, data):
        self.taglar[-1]["data"] = self.taglar[-1].get("data","") + data



def doviz(base_link):
    if (sys.version_info[0] < 3):
        request = urllib2.Request(base_link, headers=agent)
        raw_data = urllib2.urlopen(request).read()
    else:
        request = urllib.request.Request(base_link, headers=agent)
        raw_data = urllib.request.urlopen(request).read()
    data = raw_data.decode("utf-8")
    MyHTMLParser.taglar.clear()
    MyHTMLParser.taglar.append({"tag_s":[], "attrs":[], "tag_e":[], "data":""})
    parser = MyHTMLParser()
    parser.feed(data)
    alis = ""
    satis = ""
    sonzaman = None
    yasonra_alis = False
    yasonra_satis = False
    for i in parser.taglar:
        if yasonra_alis and len(i["attrs"])>0 and i["attrs"][0][1] and "value" in i["attrs"][0][1]:
            alis = "alış: " + i["data"].strip()
            yasonra_alis=False
        elif yasonra_satis and len(i["attrs"])>0 and i["attrs"][0][1] and "value" in i["attrs"][0][1]:
            satis = "satış: " + i["data"].strip()
            yasonra_satis=False
        if not alis and ( "Alış" in i.get("data","") or "Son" in i.get("data","")):
            yasonra_alis = True
        elif not satis and "Satış" in i.get("data",""):
            yasonra_satis = True
        if len(i["attrs"]) > 0 and "update" in i["attrs"][0]:
            sonzaman = i["data"].strip()

    return alis, satis, sonzaman
    


class DovizExtension(Extension):
    def __init__(self):
        super(DovizExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        
        for i in range(7):
            x = extension.preferences["dov"+str(i)].split(";")
            if len(x) < 2:
                continue
            metin = doviz(x[1].strip()) #Adres
            items.append(
                ExtensionResultItem(icon='images/icon.png',
                                    name= x[0].strip() + "\t" + metin[0] + "\t" + metin[1],
                                    description= metin[2],
                                    on_enter=HideWindowAction())
            )

        return RenderResultListAction(items)


if __name__ == '__main__':
    DovizExtension().run()
