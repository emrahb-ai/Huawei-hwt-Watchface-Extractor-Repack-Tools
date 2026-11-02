"""Inspect/edit probable layout bounding boxes. No vendor schema is assumed."""
import json,sys
from pathlib import Path

def vi(b,p):
    v=0;s=0
    while True:
        c=b[p];p+=1;v|=(c&127)<<s
        if c<128:return v,p
        s+=7
def enc(n):
    a=bytearray()
    while n>=128:a.append((n&127)|128);n>>=7
    return bytes(a+[n])
def parse(b):
    p=0;o=[]
    while p<len(b):
        tag,p=vi(b,p);n,w=tag>>3,tag&7
        if w==0:v,p=vi(b,p)
        elif w==2:
            z,p=vi(b,p);v=b[p:p+z];p+=z
        elif w in (1,5):
            z=8 if w==1 else 4;v=b[p:p+z];p+=z
        else:raise ValueError('unsupported wire type')
        o.append([n,w,v])
    return o
def dump(arr):
    o=bytearray()
    for n,w,v in arr:
        o+=enc(n*8+w)
        if w==0:o+=enc(v)
        elif w==2:o+=enc(len(v))+v
        else:o+=v
    return bytes(o)
def get_boxes(data):
    root=parse(data);result=[]
    for i,r in enumerate(root):
        if r[:2]!=[1,2]:continue
        a=parse(r[2]);group=next((v for n,w,v in a if (n,w)==(1,0)),None)
        for j,e in enumerate(a):
            if e[:2]!=[8,2]:continue
            el=parse(e[2]);ident=next((v for n,w,v in el if (n,w)==(1,0)),None)
            for k,box in enumerate(el):
                if box[:2]!=[5,2]:continue
                xy={n:v for n,w,v in parse(box[2]) if w==0 and n in (1,2,3,4)}
                if len(xy)!=4:continue
                result.append(dict(key=f'{i}.{j}.{k}',group_id=group,item_id=ident,x=xy[1],y=xy[2],width=xy[3],height=xy[4]))
    return result
def main(folder,action):
    base=Path(folder)/'watchface_extracted';p=base/'layout.protobuf';j=base/'layout_boxes.json';data=p.read_bytes()
    if action=='inspect':
        a=dict(note='Candidate positions, schema not verified; edit x/y/width/height only',entries=get_boxes(data))
        j.write_text(json.dumps(a,indent=2),encoding='utf8')
        print('Exported',len(a['entries']),'candidate boxes to',j);return
    if action!='apply':raise ValueError('action must be inspect or apply')
    before={v['key']:v for v in get_boxes(data)};root=parse(data)
    changes=0
    for box in json.loads(j.read_text(encoding='utf8'))['entries']:
        key=box['key']
        if key not in before:raise ValueError('Unknown key: '+key)
        if all(box[t]==before[key][t] for t in ('x','y','width','height')):continue
        values={1:box['x'],2:box['y'],3:box['width'],4:box['height']}
        if any(type(v)!=int or not 0<=v<=65535 for v in values.values()):raise ValueError('invalid dimensions')
        i,jj,k=map(int,key.split('.'));group=parse(root[i][2]);element=parse(group[jj][2]);dims=parse(element[k][2])
        for entry in dims:
            if entry[1]==0 and entry[0] in values:entry[2]=values[entry[0]]
        element[k][2]=dump(dims);group[jj][2]=dump(element);root[i][2]=dump(group);changes+=1
    backup=p.with_suffix('.protobuf.original')
    if backup.exists():raise FileExistsError('Backup already exists: '+str(backup))
    output=dump(root)
    if len(get_boxes(output))!=len(before):raise ValueError('layout validation failed')
    backup.write_bytes(data);p.write_bytes(output)
    print('Updated',changes,'layout boxes. Backup:',backup)
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: python hwt_layout_editor.py inspect|apply extracted_folder')
    main(sys.argv[2],sys.argv[1])
