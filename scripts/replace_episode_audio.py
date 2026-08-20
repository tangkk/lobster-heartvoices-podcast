#!/usr/bin/env python3
import argparse
import os
import xml.etree.ElementTree as ET
from pathlib import Path


def client():
    import boto3
    from botocore.config import Config
    return boto3.client('s3', endpoint_url=os.environ['R2_ENDPOINT'].strip('"'), aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'], region_name='auto', config=Config(s3={'addressing_style':'path'}))


def find_item(feed, slug):
    tree=ET.parse(feed); ch=tree.getroot().find('channel')
    if ch is None: raise SystemExit('Missing RSS channel')
    for item in ch.findall('item'):
        if (item.findtext('guid') or '')==slug: return tree,item
    raise SystemExit(f'Episode does not exist: {slug}')


def prepare(args):
    audio=Path(args.audio)
    if not audio.is_file() or audio.stat().st_size<=0: raise SystemExit('Replacement audio missing or empty')
    tree,item=find_item(args.feed,args.slug); enc=item.find('enclosure'); dur=item.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
    if enc is None or dur is None: raise SystemExit('Existing RSS item missing enclosure/duration')
    key=f"{args.prefix.rstrip('/')}/{args.slug}.mp3"; c=client(); old=c.head_object(Bucket=os.environ['R2_BUCKET'],Key=key)
    backup=f"_replacement_backups/{args.slug}/{os.environ.get('GITHUB_SHA','manual')}.mp3"
    c.copy_object(Bucket=os.environ['R2_BUCKET'],Key=backup,CopySource={'Bucket':os.environ['R2_BUCKET'],'Key':key},ContentType='audio/mpeg',MetadataDirective='REPLACE')
    c.upload_file(str(audio),os.environ['R2_BUCKET'],key,ExtraArgs={'ContentType':'audio/mpeg'})
    new=c.head_object(Bucket=os.environ['R2_BUCKET'],Key=key)
    if new['ContentLength']!=args.bytes:
        c.copy_object(Bucket=os.environ['R2_BUCKET'],Key=key,CopySource={'Bucket':os.environ['R2_BUCKET'],'Key':backup},ContentType='audio/mpeg',MetadataDirective='REPLACE')
        raise SystemExit('R2 replacement size verification failed; old object restored')
    enc.set('length',str(args.bytes)); dur.text=args.duration
    ET.register_namespace('itunes','http://www.itunes.com/dtds/podcast-1.0.dtd'); ET.register_namespace('atom','http://www.w3.org/2005/Atom')
    tree.write(args.feed,encoding='utf-8',xml_declaration=True); Path(args.state).write_text(backup+'\n',encoding='utf-8')
    print(f'replacement prepared: {key}; {old["ContentLength"]} -> {new["ContentLength"]}; backup={backup}')


def rollback(args):
    backup=Path(args.state).read_text(encoding='utf-8').strip(); key=f"{args.prefix.rstrip('/')}/{args.slug}.mp3"; c=client()
    c.copy_object(Bucket=os.environ['R2_BUCKET'],Key=key,CopySource={'Bucket':os.environ['R2_BUCKET'],'Key':backup},ContentType='audio/mpeg',MetadataDirective='REPLACE'); c.delete_object(Bucket=os.environ['R2_BUCKET'],Key=backup)


def cleanup(args):
    client().delete_object(Bucket=os.environ['R2_BUCKET'],Key=Path(args.state).read_text(encoding='utf-8').strip())


def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('prepare'); q.add_argument('--feed',default='feed.xml'); q.add_argument('--audio',required=True); q.add_argument('--slug',required=True); q.add_argument('--prefix',required=True); q.add_argument('--bytes',type=int,required=True); q.add_argument('--duration',required=True); q.add_argument('--state',required=True)
    for name in ('rollback','cleanup'):
        q=sub.add_parser(name); q.add_argument('--slug',required=True); q.add_argument('--prefix',required=True); q.add_argument('--state',required=True)
    args=p.parse_args(); missing=[v for v in ['R2_ACCESS_KEY_ID','R2_SECRET_ACCESS_KEY','R2_ENDPOINT','R2_BUCKET'] if not os.environ.get(v)]
    if missing: raise SystemExit('Missing env: '+', '.join(missing))
    {'prepare':prepare,'rollback':rollback,'cleanup':cleanup}[args.cmd](args)

if __name__=='__main__': main()
