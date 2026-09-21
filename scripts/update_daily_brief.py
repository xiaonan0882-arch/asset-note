#!/usr/bin/env python3
import json, re, urllib.parse, urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

QUERIES = [
 ("科技","中国","China AI semiconductor robotics technology when:2d"),
 ("科技","美国","US AI semiconductor technology when:2d"),
 ("科技","日韩","Japan Korea AI semiconductor technology when:2d"),
 ("科技","全球","global AI semiconductor technology when:2d"),
 ("宏观","中国","China economy monetary policy yuan bonds when:2d"),
 ("宏观","美国","Federal Reserve inflation Treasury yields US economy when:2d"),
 ("宏观","日韩","Japan Korea central bank inflation economy when:2d"),
 ("宏观","全球","global central banks inflation rates economy when:2d"),
 ("消费","中国","China consumer retail catering travel luxury when:3d"),
 ("消费","美国","US consumer retail spending travel luxury when:3d"),
 ("消费","日韩","Japan Korea consumer retail travel luxury when:3d"),
 ("消费","全球","global consumer retail luxury travel when:3d"),
 ("周期","中国","China oil copper steel chemicals shipping industry when:3d"),
 ("周期","美国","US oil copper industrial manufacturing shipping when:3d"),
 ("周期","日韩","Japan Korea autos shipping refinery chemicals when:3d"),
 ("周期","全球","global oil copper steel shipping commodities when:3d"),
]

def fetch(q):
    url="https://news.google.com/rss/search?q="+urllib.parse.quote(q)+"&hl=en-US&gl=US&ceid=US:en"
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 AssetNote/1.0"})
    with urllib.request.urlopen(req,timeout=20) as r:
        return r.read()

def parse_feed(xml, theme, region):
    root=ET.fromstring(xml)
    out=[]
    for item in root.findall("./channel/item")[:4]:
        title=(item.findtext("title") or "").strip()
        link=(item.findtext("link") or "").strip()
        pub=(item.findtext("pubDate") or "").strip()
        source_el=item.find("source")
        source=(source_el.text or "").strip() if source_el is not None else ""
        if " - " in title and not source:
            title,source=title.rsplit(" - ",1)
        try:
            dt=parsedate_to_datetime(pub)
            published=dt.astimezone(timezone.utc).isoformat()
        except Exception:
            published=pub
        out.append({"theme":theme,"region":region,"title":title,"summary":"","why":"","source":source or "Google News","url":link,"publishedAt":published})
    return out

def main():
    items=[]; seen=set()
    for theme,region,q in QUERIES:
        try:
            feed=parse_feed(fetch(q),theme,region)
        except Exception:
            continue
        for x in feed:
            key=re.sub(r"\W+","",x["title"].lower())
            if key in seen: continue
            seen.add(key); items.append(x)
    if len(items)<8:
        raise SystemExit("Too few fresh items; keep previous brief.")
    data={"asOf":datetime.now(timezone.utc).isoformat(),"title":"每日市场研究","items":items}
    with open("data/daily-brief.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

if __name__=="__main__":
    main()
