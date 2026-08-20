#!/usr/bin/env python3
import argparse, datetime as dt, os, xml.etree.ElementTree as ET
from email.utils import format_datetime

def ns(): ET.register_namespace('itunes','http://www.itunes.com/dtds/podcast-1.0.dtd'); ET.register_namespace('atom','http://www.w3.org/2005/Atom'); ET.register_namespace('content','http://purl.org/rss/1.0/modules/content/')
def client(endpoint):
    import boto3
    from botocore.config import Config
    return boto3.client('s3',endpoint_url=endpoint,aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],region_name='auto',config=Config(s3={'addressing_style':'path'}))
def ensure_absent(c,bucket,key):
    try: c.head_object(Bucket=bucket,Key=key)
    except Exception as e:
        r=getattr(e,'response',{}) or {}; code=str(r.get('Error',{}).get('Code','')); status=r.get('ResponseMetadata',{}).get('HTTPStatusCode')
        if code in {'404','NoSuchKey','NotFound'} or status==404: return
        raise
    raise SystemExit(f'R2 object already exists: {key}')
def add(feed,url,size,slug,title,desc,duration):
    t=ET.parse(feed); ch=t.getroot().find('channel')
    if ch is None: raise SystemExit('Missing RSS channel')
    if any((i.findtext('guid') or '')==slug for i in ch.findall('item')): raise SystemExit(f'GUID already exists: {slug}')
    i=ET.Element('item'); ET.SubElement(i,'title').text=title; ET.SubElement(i,'description').text=desc; ET.SubElement(i,'pubDate').text=format_datetime(dt.datetime.now(dt.timezone.utc)); ET.SubElement(i,'guid',{'isPermaLink':'false'}).text=slug; ET.SubElement(i,'enclosure',{'url':url,'length':str(size),'type':'audio/mpeg'}); ET.SubElement(i,'{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text=duration; ET.SubElement(i,'{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text='false'; first=ch.find('item'); ch.insert(list(ch).index(first),i) if first is not None else ch.append(i); lb=ch.find('lastBuildDate');
    if lb is not None: lb.text=format_datetime(dt.datetime.now(dt.timezone.utc))
    t.write(feed,encoding='utf-8',xml_declaration=True)
def main():
    ns(); p=argparse.ArgumentParser(); p.add_argument('--feed',default='feed.xml'); p.add_argument('--audio',required=True); p.add_argument('--slug',required=True); p.add_argument('--title',required=True); p.add_argument('--description',required=True); p.add_argument('--duration',required=True); p.add_argument('--prefix',required=True); a=p.parse_args(); missing=[v for v in ['R2_ACCESS_KEY_ID','R2_SECRET_ACCESS_KEY','R2_ENDPOINT','R2_BUCKET','R2_PUBLIC_URL'] if not os.environ.get(v)]
    if missing: raise SystemExit('Missing env: '+', '.join(missing))
    if not os.path.isfile(a.audio) or os.path.getsize(a.audio)<=0: raise SystemExit('Audio missing or empty')
    c=client(os.environ['R2_ENDPOINT'].strip('"')); key=f"{a.prefix.rstrip('/')}/{a.slug}{os.path.splitext(a.audio)[1].lower() or '.mp3'}"; ensure_absent(c,os.environ['R2_BUCKET'],key); size=os.path.getsize(a.audio); c.upload_file(a.audio,os.environ['R2_BUCKET'],key,ExtraArgs={'ContentType':'audio/mpeg'}); add(a.feed,f"{os.environ['R2_PUBLIC_URL'].rstrip('/')}/{key}",size,a.slug,a.title,a.description,a.duration)
if __name__=='__main__': main()
