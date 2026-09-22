#!/usr/bin/env python3
import json, re, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET

# High-frequency layer: only recent headlines. Older official releases belong in latestData, not "today".
QUERIES = [
 ("科技","中国","China AI semiconductor robotics technology site:reuters.com when:1d"),
 ("科技","美国","US AI semiconductor chips AMD Nvidia Intel site:reuters.com when:1d"),
 ("科技","日韩","Japan Korea Taiwan semiconductor AI chips site:reuters.com when:1d"),
 ("科技","全球","global AI semiconductor robotics site:reuters.com when:1d"),
 ("宏观","中国","China PBOC yuan economy trade site:reuters.com when:1d"),
 ("宏观","美国","Federal Reserve Treasury yields US economy site:reuters.com when:1d"),
 ("宏观","日韩","Japan Korea central bank economy yen won site:reuters.com when:1d"),
 ("宏观","全球","global central banks rates inflation markets site:reuters.com when:1d"),
 ("消费","中国","China consumer retail catering travel luxury site:reuters.com when:1d"),
 ("消费","美国","US consumer retail travel luxury site:reuters.com when:1d"),
 ("消费","日韩","Japan Korea consumer retail travel luxury site:reuters.com when:1d"),
 ("消费","全球","global consumer retail luxury travel site:reuters.com when:1d"),
 ("周期","中国","China oil copper steel chemicals shipping site:reuters.com when:1d"),
 ("周期","美国","US oil copper industrial manufacturing shipping site:reuters.com when:1d"),
 ("周期","日韩","Japan Korea autos shipping refinery chemicals site:reuters.com when:1d"),
 ("周期","全球","global oil copper commodities shipping site:reuters.com when:1d"),
 ("大宗商品","中国","China commodities oil copper gold iron ore site:reuters.com when:1d"),
 ("大宗商品","美国","US oil gold copper natural gas commodities site:reuters.com when:1d"),
 ("大宗商品","日韩","Japan Korea commodities LNG oil metals site:reuters.com when:1d"),
 ("大宗商品","全球","global commodities oil gold copper iron ore grains site:reuters.com when:1d"),
 ("期货","中国","China futures SHFE DCE CZCE INE commodities site:reuters.com when:1d"),
 ("期货","美国","CME futures Treasury oil gold equity futures site:reuters.com when:1d"),
 ("期货","日韩","Japan Korea futures derivatives commodities site:reuters.com when:1d"),
 ("期货","全球","global futures commodities derivatives positioning site:reuters.com when:1d"),
 ("政治","中国","China politics trade diplomacy summit sanctions site:reuters.com when:1d"),
 ("政治","美国","US politics trade diplomacy sanctions Congress site:reuters.com when:1d"),
 ("政治","日韩","Japan Korea politics trade diplomacy security site:reuters.com when:1d"),
 ("政治","全球","global geopolitics war diplomacy sanctions UN site:reuters.com when:1d"),
 # Chinese high-frequency financial media as supplements.
 ("科技","中国","AI 半导体 机器人 财联社 when:1d"),
 ("宏观","中国","人民币 央行 宏观 财联社 证券时报 when:1d"),
 ("消费","中国","消费 零售 餐饮 旅游 财联社 商务部 when:1d"),
 ("周期","中国","原油 铜 化工 航运 财联社 when:1d"),
]

MAX_AGE_HOURS=36

def fetch(q):
    url="https://news.google.com/rss/search?q="+urllib.parse.quote(q)+"&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 AssetNote/1.0"})
    with urllib.request.urlopen(req,timeout=20) as r:
        return r.read()

def parse_feed(xml, theme, region):
    root=ET.fromstring(xml); out=[]; now=datetime.now(timezone.utc)
    for item in root.findall("./channel/item")[:8]:
        title=(item.findtext("title") or "").strip()
        link=(item.findtext("link") or "").strip()
        pub=(item.findtext("pubDate") or "").strip()
        source_el=item.find("source")
        source=(source_el.text or "").strip() if source_el is not None else ""
        if " - " in title and not source: title,source=title.rsplit(" - ",1)
        try:
            dt=parsedate_to_datetime(pub).astimezone(timezone.utc)
        except Exception:
            continue
        if now-dt>timedelta(hours=MAX_AGE_HOURS) or dt-now>timedelta(hours=2):
            continue
        out.append({"theme":theme,"region":region,"title":title,"summary":"","why":"","source":source or "Google News","url":link,"publishedAt":dt.isoformat(),"freshness":"recent"})
    return out

def main():
    items=[]; seen=set()
    for theme,region,q in QUERIES:
        try: feed=parse_feed(fetch(q),theme,region)
        except Exception: continue
        for x in feed:
            key=re.sub(r"\W+","",x["title"].lower())
            if key in seen: continue
            seen.add(key); items.append(x)
    items.sort(key=lambda x:x["publishedAt"],reverse=True)
    if len(items)<6:
        raise SystemExit("Too few <36h items; preserve previous brief instead of filling with stale news.")
    old={}
    try:
        with open("data/daily-brief.json",encoding="utf-8") as f: old=json.load(f)
    except Exception: pass
    data={
      "asOf":datetime.now(timezone.utc).isoformat(),
      "title":"每日市场研究",
      "freshnessRule":"今日动态仅展示最近36小时；官方低频数据单列并显示发布日期。",
      "items":items[:48],
      "latestData":old.get("latestData",[])
    }
    with open("data/daily-brief.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

if __name__=="__main__":
    main()
