"""HPArchive pipeline: python build_hp.py data/source_harry.json data
Sources: (1) 'harry.json' character dataset from GitHub (Laboratoria/BOG005-data-lovers), wiki-derived: associated_groups, houses, species, ancestry, books.
(2) curated.py: our own typed canon layer. Evidence classes: dataset | canon | film | derived."""
import json,re,sys,hashlib,collections,os,csv
import networkx as nx
sys.path.insert(0,os.path.dirname(__file__));import curated as C
SRC=sys.argv[1] if len(sys.argv)>1 else "data/source_harry.json";OUT=sys.argv[2] if len(sys.argv)>2 else "data"
raw=json.load(open(SRC,encoding="utf-8"))["characters"]
ALIAS={"Voldemort":"Lord Voldemort","Tom Marvolo Riddle":"Lord Voldemort","Tom Riddle (Voldemort)":"Lord Voldemort","Ginevra Weasley":"Ginny Weasley","Ron Weasley":"Ronald Weasley","Lily Potter":"Lily J. Potter","James Potter":"James Potter I","Wormtail":"Peter Pettigrew"}
HOUSES=["Gryffindor","Slytherin","Hufflepuff","Ravenclaw"]
slug=lambda s:re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
canon=lambda n:ALIAS.get(n,n)
def anc(a):
    a=(a or "").lower()
    for k,v in (("pure","Pure-blood"),("half","Half-blood"),("muggle-born","Muggle-born"),("muggleborn","Muggle-born"),("squib","Squib"),("muggle","Muggle")):
        if k in a:return v
    return "Unknown"
chars={}
for x in raw:
    n=x["name"]
    if n.startswith("User:") or re.search(r"'s(\s|$)",n) or "(Potter-era)" in n:continue
    n=canon(n);e=chars.setdefault(n,{"name":n,"house":None,"hu":False,"species":"Unknown","ancestry":"Unknown","gender":None,"hair":None,"eye":None,"wand":None,"patronus":None,"birth":None,"death":None,"fam":None,"books":set(),"groups":set()})
    h=x.get("house") or ""
    for hh in HOUSES:
        if h.startswith(hh):e["house"]=hh;e["hu"]="possibly" in h
    if h and not any(h.startswith(hh) for hh in HOUSES) and (h.startswith("House of") or h.endswith(" family")):e["fam"]=h
    sp=re.sub(r"\s*\(.*\)","",x.get("species") or "").strip()
    if sp in("Humans",""):sp="Human" if sp else "Unknown"
    if e["species"]=="Unknown":e["species"]=sp
    if e["ancestry"]=="Unknown":e["ancestry"]=anc(x.get("ancestry"))
    for k,s in (("gender","gender"),("hair","hair_color"),("eye","eye_color"),("wand","wand"),("patronus","patronus"),("birth","birth"),("death","death")):
        if not e[k] and x.get(s):e[k]=x[s]
    e["books"]|=set(x.get("books_featured_in") or []);e["groups"]|=set(x.get("associated_groups") or [])
nodes={};edges=[];EK=set()
def nid(k,n):return f"{k}:{slug(n)}"
def node(k,n,**kw):
    i=nid(k,n)
    if i not in nodes:nodes[i]={"id":i,"l":n,"k":k,**kw}
    return i
for n,e in chars.items(): node("character",n,src="dataset")
def edge(a,b,t,ev,note="",bk=(),conf="high"):
    k=(a,b,t,ev)
    if k in EK or a==b:return
    EK.add(k);edges.append({"a":a,"b":b,"t":t,"ev":ev,"note":note,"bk":list(bk),"conf":conf})
def char(n):
    n=canon(n);i=nid("character",n)
    if i not in nodes:node("character",n,src="canon")
    return i
# ---- groups ----
gcount=collections.Counter(g for e in chars.values() for g in e["groups"])
def classify(g):
    base=re.sub(r"\s*\(.*\)$","",g).strip();q=(re.search(r"\((.*)\)$",g) or [None,""])[1]
    base=canon(base)
    if base in HOUSES:return "house",base,q
    if base in chars and base!=g or canon(g) in chars:return "person",base,q
    if base.endswith(" family"):return "family",base,q
    return "org",base,q
need=collections.Counter()
for g,c in gcount.items():
    k,b,q=classify(g)
    if k in("org","family"):need[b]+=c
for n,e in chars.items():
    i=nid("character",n)
    if e["house"]:edge(i,node("house",e["house"]),"HOUSE","dataset","" if not e["hu"] else "house uncertain in source",[],"medium" if e["hu"] else "high")
    if e["fam"]:edge(i,node("family",e["fam"]),"FAMILY_MEMBER","dataset","family named in the source's house field")
    for g in e["groups"]:
        k,b,q=classify(g)
        if k=="house":edge(i,node("house",b),"HOUSE","dataset",q);continue
        if k=="person":edge(i,char(b),"ASSOCIATED_WITH","dataset",q or "associated group in source");continue
        if need[b]<3:continue
        edge(i,node("family" if k=="family" else "org",b),"FAMILY_MEMBER" if k=="family" else "MEMBER_OF","dataset",q)
# ---- curated ----
for a,b,t,note,bk,conf in C.R:
    def get(n):
        if n in HOUSES:return node("house",n)
        if n in C.PL:return node("place",n,desc=C.PL[n])
        if n in C.OBJ:return node("object",n,desc=C.OBJ[n])
        if n=="Nagini" and nid("character",n) not in nodes:return char(n)
        return char(n)
    edge(get(a),get(b),t,"canon",note,bk,conf)
actors={}
for act,ch,films in C.CAST:
    ai=node("actor",act);edge(ai,char(ch),"PLAYED","film","films "+films,[],"high");actors.setdefault(char(ch),[]).append(f"{act} (films {films})")
def fset(f):
    out=set()
    for p in f.split(","):
        p=p.strip()
        if "-" in p:x,y=p.split("-");out|=set(range(int(x),int(y)+1))
        elif p:out.add(int(p))
    return out
# ---- metrics ----
W={"PARENT_OF":4,"SPOUSE_OF":4,"SIBLING_OF":3,"PARTNER_OF":2,"GODPARENT_OF":2,"MENTOR_OF":2,"FRIEND_OF":1.5,"ENEMY_OF":1.5,"KILLED":1.5,"HOUSE":.6,"MEMBER_OF":.5,"FAMILY_MEMBER":2,"ASSOCIATED_WITH":1,"PLAYED":.3}
G=nx.Graph()
for e in edges:
    w=W.get(e["t"],1)
    if G.has_edge(e["a"],e["b"]):G[e["a"]][e["b"]]["weight"]+=w
    else:G.add_edge(e["a"],e["b"],weight=w)
core=max(nx.connected_components(G),key=len);G=G.subgraph(core).copy()
pr=nx.pagerank(G,weight="weight");bt=nx.betweenness_centrality(G,k=300,seed=7);dg=dict(G.degree())
comm=nx.community.louvain_communities(G.subgraph([n for n in G if nodes[n]["k"]!="actor"]),weight="weight",seed=7,resolution=1.1)
cid={}
for i,cset in enumerate(sorted(comm,key=len,reverse=True)):
    for n in cset:cid[n]=i
def clabel(cset):
    o=sorted((n for n in cset if nodes[n]["k"] in("org","family","house","place")),key=lambda n:-sum(1 for m in G[n] if m in cset))[:2]
    return " · ".join(re.sub(r" School of Witchcraft and Wizardry","",nodes[n]["l"]) for n in o) or nodes[max(cset,key=lambda n:pr[n])]["l"]
cname={i:clabel(cset) for i,cset in enumerate(sorted(comm,key=len,reverse=True))}
for n,c in list(cid.items()):
    if c>=10:cid[n]=10
cname={k:v for k,v in cname.items() if k<10};cname[10]="Smaller clusters"
lay=nx.spring_layout(G,dim=3,k=.35,iterations=220,seed=7,weight="weight",scale=420)
for i,n in nodes.items():
    if i in G:n.update({"deg":dg[i],"pr":round(pr[i],5),"bt":round(bt[i],5),"cm":cid.get(i,-1),"p":[round(float(v),1) for v in lay[i]]})
# ---- directory ----
bookn=collections.Counter(b for e in chars.values() for b in e["books"])
seen=set();newper={}
for b in range(1,8):
    new=[n for n,e in chars.items() if b in e["books"] and n not in seen];newper[b]=len(new);seen|=set(new)
CH={e["a"]:(nodes[e["b"]]["l"],e["conf"]=="medium") for e in edges if e["t"]=="HOUSE" and e["ev"]=="canon"}
directory=[]
for n,e in sorted(chars.items()):
    i=nid("character",n);directory.append({"id":i,"name":n,"house":e["house"] or CH.get(i,(None,))[0],"hu":e["hu"] or (not e["house"] and CH.get(i,(0,False))[1]),"species":e["species"],"ancestry":e["ancestry"],"gender":e["gender"],"hair":e["hair"],"eye":e["eye"],"wand":e["wand"],"patronus":e["patronus"],"birth":e["birth"],"death":e["death"],"books":sorted(e["books"]),"groups":sorted(e["groups"]),"actors":actors.get(i,[]),"inGraph":i in G})
for i,n in nodes.items():
    if n["k"]=="character" and n["src"]=="canon":directory.append({"id":i,"name":n["l"],"house":None,"hu":False,"species":"Unknown","ancestry":"Unknown","books":[],"groups":[],"actors":actors.get(i,[]),"inGraph":i in G,"canonOnly":True})
# ---- missing-name report ----
canon_only=[n["l"] for n in nodes.values() if n["k"]=="character" and n["src"]=="canon"]
gn=lambda n:[nid("character",canon(x)) for x in n if nid("character",canon(x)) in nodes]
tours=[{"t":t,"d":d,"ids":gn(l)+[nid(k,x) for x in l for k in("object",) if nid(k,x) in nodes]} for t,d,l in C.TOURS]
events=[{"d":d,"t":t,"bk":b,"ids":gn(w)} for d,t,b,w in C.EVENTS]
ev=collections.Counter(e["ev"] for e in edges);et=collections.Counter(e["t"] for e in edges)
house_anc=collections.Counter((e["house"],e["ancestry"]) for e in chars.values() if e["house"])
vis=[n for n in nodes.values() if "p" in n];ek=[e for e in edges if e["a"] in G and e["b"] in G]
top=sorted([n for n in vis if n["k"]=="character"],key=lambda n:-n["pr"])[:20]
DATA={"meta":{"title":"HPArchive","version":"1.0.0","chars":len(directory),"nodes":len(vis),"edges":len(ek),"evidence":dict(ev),"types":dict(et),"canonOnly":canon_only,"note":"Unofficial fan archive. No book or film text, images or scripts are included."},
"nodes":vis,"edges":ek,"dir":directory,"books":[{"n":n,"t":t,"y":y,"chars":bookn[n],"new":newper[n]} for n,t,y in C.BOOKS],"films":[{"n":n,"t":t,"y":y,"dir":d,"book":bk,"cast":[f"{a} as {c.replace(' (Voldemort)','')} (films {f})" for a,c,f in C.CAST if f and n in fset(f)],"other":[f"{a} as {c}" for a,c,f in C.CAST if not f]} for n,t,y,d,bk in C.FILMS],
"events":events,"tours":tours,"comm":{str(k):v for k,v in cname.items()},"top":[{"id":n["id"],"l":n["l"],"pr":n["pr"],"bt":n["bt"],"deg":n["deg"]} for n in top],"houseAnc":{f"{h}|{a}":c for (h,a),c in house_anc.items()},"houses":HOUSES}
s=json.dumps(DATA,ensure_ascii=False,separators=(',',':'));open(f"{OUT}/hp.json","w",encoding="utf-8").write(s)
man={"hp.json":hashlib.sha256(s.encode()).hexdigest(),"source_harry.json":hashlib.sha256(open(SRC,"rb").read()).hexdigest()}
with open(f"{OUT}/nodes.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f);w.writerow(["id","label","kind","community","degree","pagerank"]);[w.writerow([n["id"],n["l"],n["k"],n.get("cm"),n.get("deg"),n.get("pr")]) for n in vis]
with open(f"{OUT}/edges.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f);w.writerow(["source","target","type","evidence","confidence","books","note"]);[w.writerow([e["a"],e["b"],e["t"],e["ev"],e["conf"],"|".join(map(str,e["bk"])),e["note"]]) for e in ek]
GX=nx.MultiDiGraph()
for n in vis:GX.add_node(n["id"],label=n["l"],kind=n["k"],community=n.get("cm",-1))
for e in ek:GX.add_edge(e["a"],e["b"],type=e["t"],evidence=e["ev"],confidence=e["conf"])
nx.write_graphml(GX,f"{OUT}/hp.graphml")
q=json.dumps
cy=["CREATE CONSTRAINT IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE;"]+[f"MERGE (n:Node:{n['k'].title()} {{id:{q(n['id'])}}}) SET n.label={q(n['l'])};" for n in vis]+[f"MATCH (a:Node {{id:{q(e['a'])}}}),(b:Node {{id:{q(e['b'])}}}) MERGE (a)-[r:{e['t']}]->(b) SET r.evidence={q(e['ev'])},r.confidence={q(e['conf'])};" for e in ek]
open(f"{OUT}/hp-cypher-seed.cypher","w",encoding="utf-8").write("\n".join(cy))
for fn in("nodes.csv","edges.csv","hp.graphml","hp-cypher-seed.cypher"):man[fn]=hashlib.sha256(open(f"{OUT}/{fn}","rb").read()).hexdigest()
json.dump(man,open(f"{OUT}/MANIFEST.sha256.json","w"),indent=1)
print("directory",len(directory),"graph nodes",len(vis),"edges",len(ek),"evidence",dict(ev));print("types",dict(et));print("canon-only (not in dataset):",canon_only[:40]);print("communities",len(comm),list(cname.values())[:10]);print("top",[n["l"] for n in top[:12]])
