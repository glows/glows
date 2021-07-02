import  json
import feedparser
import  datetime
from time import mktime
import email.utils
import  pathlib
import re

root = pathlib.Path(__file__).parent.resolve()

def formatGMTime(timestamp):
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    dateStr = datetime.datetime.strptime(timestamp, GMT_FORMAT) + datetime.timedelta(hours=8)
    return dateStr.date()

def formatRFC822Time(timestamp):
    date_parsed = email.utils.parsedate(timestamp)
    dt = datetime.datetime.fromtimestamp(mktime(date_parsed))
    return dt.date()

def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->\n{}\n<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_douban():
    entries = feedparser.parse("https://www.douban.com/feed/people/65855501/interests")["entries"]
    return [
        {
            "title": "["+item["title"][0:2]+"]"+item["title"][2:],
            "url": item["link"].split("#")[0],
            "published": formatGMTime(item["published"])
        }
        for item in entries
    ]


def fetch_blog_entries():
    entries = feedparser.parse("https://glows.github.io/index.xml")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": formatRFC822Time(entry["published"]),
        }
        for entry in entries
    ]
    
    
if __name__ == "__main__":
    readme = root / "NEW.md"
    
    doubans = fetch_douban()[:5]
    entries = fetch_blog_entries()[:5]
    doubans_md = "\n".join(
        ["- <a href='{url}' target='_blank'>{title}</a> - {published}".format(**item) for item in
         doubans]
    )
    
    entries_md = "\n".join(
        ["- <a href='{url}' target='_blank'>{title}</a> - {published}".format(**entry) for entry in
         entries]
    )
    readme_contents = open(readme, encoding='utf-8').read()
    rewritten = replace_chunk(readme_contents, "douban", doubans_md)
    readme.open("w", encoding='utf-8').write(rewritten)
    
    
    rewritten_blog = replace_chunk(rewritten, "blog", entries_md)
    readme.open("w", encoding='utf-8',).write(rewritten_blog)
    