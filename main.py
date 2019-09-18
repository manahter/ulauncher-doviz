# Veriler doviz.com adresinden alınmaktadır.
import re
from requests import get
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko"}

def doviz(base_link):
    data = get(base_link, headers=headers)
    veri = data.content.decode("utf-8")
    
    real = "col.*[\n].*label.*Alış.*[\n].*value"   if "endeksler" not in base_link else "col.*[\n].*label.*Son.*[\n].*value"
    resa = "col.*[\n]*.*label.*Satı.*[\n].*value"  if "endeksler" not in base_link else "col.*[\n].*label.*Son.*[\n].*value"
    reup = "col.*[\n]*.*update"
        
    x = re.search(real, veri)
    x = x.span()[1] if x else False
    alis = ( "Alış: " + veri[veri.find(">",x)+1:veri.find("<",x)] ) if x else ""
    
    y = re.search(resa, veri)
    y = y.span()[1] if y else False
    sats = ( "Satış: " + veri[veri.find(">",y)+1:veri.find("<",y)] ) if y else ""
    
    z = re.search(reup, veri)
    z = z.span()[1] if z else False
    updt = veri[veri.find(">",z)+1:veri.find("<",z)] if z else ""
    
    return alis, sats, updt


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
            items.append(   ExtensionResultItem(icon='images/icon.png',
                                                name= "{:10}{:20}{}".format(x[0].strip(), metin[0], metin[1]),
                                                description= metin[2],
                                                on_enter=OpenUrlAction(x[1] and x[1].strip()))
            )

        return RenderResultListAction(items)


if __name__ == '__main__':
    DovizExtension().run()
