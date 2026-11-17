import json, glob, datetime
from collections import defaultdict
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Africa/Maputo")
except Exception:
    TZ = datetime.timezone(datetime.timedelta(hours=2))

def d(ms):
    if not ms: return None
    return datetime.datetime.fromtimestamp(int(ms)/1000, TZ).strftime("%Y-%m-%d")

TODAY="2026-11-17"; WEEK_START="2026-11-16"; WEEK_END="2026-11-22"; SINCE="2026-11-03"
FINISHED={"complete","completed","closed","done","cancelled"}
WAITING={"sent to client","revert","on hold","int approval","int. approval","pending","in review","planning"}

members={
 246151538:"Miguel Proença",152426592:"Miguel Proença",246151036:"Pedro Milreu",112612740:"Leopoldo Fernandes",
 112612689:"Helder Augusto",112612688:"Simao Djedje",246218470:"Carla Wendling",112610403:"Eduardo Changule",
 112610402:"Lúria Mabui",112610050:"Afonso Mulungo",112610048:"Esménia Macie",112610045:"Francisco Caetano",
 112610043:"Elton Macuácua",112609701:"Samuel Fernando",112605120:"Patricia Aquarelli",112608024:"Zelia Mahumane",
 112607426:"Melanie Vales",112607410:"Malika Miguel",112606431:"Helio Simoes"}
canon={152426592:246151538}

# list_id -> (client, project)
CL={}
def c(client, *lists):
    for l in lists: CL[l]=(client,None)
c("Absa","1200450000100009"); c("Aesthetic Experiences","1200450000119332","1200450000119363","1200450000119362")
c("African Media Agency","1200450000119251","1200450000094744"); c("Aga Khan Foundation","1200450000098881")
c("AMCHAM","1200450000099950"); c("BNI","1200450000096783","1200450000117830")
c("BVM - Bolsa de Valores de Moçambique","1200450000118819"); c("CCSJV","1200450000118715")
c("Client Onboarding | ClickUp Community Template","1200450000118767"); c("ComServe","1200450000100008")
c("CONCURSOS DIVERSOS","1200450000118225"); c("CORAL","1200450000102340","1200450000094210","1200450000118443")
c("CPMZ","1200450000118953"); c("Digital Learning Content","1200450000117053","1200450000100021")
c("DP WORLD","1200450000118433"); c("ECOLOG","1200450000118324"); c("ENH","1200450000117383"); c("ENI","1200450000099820")
c("ExxonMobilMozambique","1200450000099958"); c("FECOP","1200450000116748"); c("Fidelidade","1200450000098861")
c("Fundação Vodacom","1200450000100026"); c("Gep-Events","1200450000114892"); c("GIZ","1200450000116946")
c("HCB","1200450000114849","1200450000119942"); c("MCNet","1200450000116454","1200450000099956"); c("MEDIS","1200450000100120")
c("Millennium Bim","1200450000099957"); c("Mozabanco","1200450000112249")
c("Internal","1200450000118235","1200450000118604","1200450000117904","1200450000114343","1200450000117181")
c("Sasol","1200450000098917","1200450000117017","1200450000118168","1200450000093985"); c("Save the Children","1200450000100011")
c("Standard Bank","1200450000102172"); c("SwissContact","1200450000117191"); c("TATA Moçambique","1200450000117382")
c("TotalEnergies","1200450000097571"); c("UBA","1200450000116821")
c("Unicef","1200450000119218","1200450000118445","1200450000121033","1200450000118172"); c("UNIDO","1200450000118415")
c("Vista Bank","1200450000100086","1200450000117054"); c("Vodacom","1200450000100025"); c("Yango","1200450000100034","1200450000118340")
c("VIVO ENERGY","1200450000120707"); c("Visiled","1200450000120727"); c("ILO","1200450000121035")
# OPERATIONS -> Internal
c("Internal","1200450000094641","1200450000101000","1200450000094801","1200450000112259","1200450000113100","1200450000115015",
  "1200450000115030","1200450000116705","1200450000117305","1200450000094633","1200450000099905","1200450000108471","1200450000118768")
# GROWTH
for l,p in [("1200450000098945","New Business"),("1200450000100161","Marketing"),("1200450000118333","UNGM"),("1200450000118171","UNGM"),
            ("1200450000118397","UNGM"),("1200450000119244","AdM-26-001"),("1200450000098944","List")]:
    CL[l]=("New business",p)

notes=[]
unmapped=set()
tasks={}
for f in sorted(glob.glob("tasks_*.txt")):
    for line in open(f,encoding="utf-8"):
        line=line.rstrip("\n")
        if not line: continue
        tid,status,prio,due,upd,closed,lid,ass,name=line.split("¦",8)
        if tid in tasks: continue
        if lid in CL: client,project=CL[lid]
        else:
            client,project="(list %s)"%lid,None; unmapped.add(lid)
        st=status.lower()
        if st in FINISHED: group="done"
        elif st in WAITING: group="waiting"
        else: group="active"
        ids=[int(a) for a in ass.split(",") if a]
        people=[]
        for a in ids:
            a=canon.get(a,a)
            if a not in members:
                notes.append("Task %s has assignee id %d who is not a workspace member; ignored."%(tid,a)); continue
            if a not in people: people.append(a)
        duedate=d(due); upddate=d(upd); closeddate=d(closed) if closed else None
        done14 = group=="done" and (closeddate or upddate) >= SINCE
        tasks[tid]=dict(id=tid,name=name,client=client,project=project,status=status,group=group,due=duedate,
            overdue=(group!="done" and duedate is not None and duedate<WEEK_START),
            due_this_week=(group!="done" and duedate is not None and WEEK_START<=duedate<=WEEK_END),
            priority=prio or None,updated=upddate,closed=closeddate,done14=done14,people=people,lid=lid,
            url="https://app.clickup.com/t/"+tid)
if unmapped: notes.append("Lists not in hierarchy map (list id used as client): "+", ".join(sorted(unmapped)))

# extra task->list for subtasks seen only in time entries
extra_list={"123tp5xf6v3":"1200450000100009","123tp5xfcp9":"1200450000100009","123tp5xefvy":"1200450000114849","123tp5xf8tn":"1200450000118324"}
entries={}
short=0
for f in sorted(glob.glob("time_*.txt")):
    for line in open(f,encoding="utf-8"):
        line=line.rstrip("\n")
        if not line: continue
        eid,start,uid,tid,dur,_=line.split("¦",5)
        if eid in entries: continue
        dur=int(dur)
        if dur<300000: short+=1; continue
        uid=canon.get(int(uid),int(uid))
        entries[eid]=dict(day=d(start),uid=uid,tid=tid,h=dur/3600000)
def client_of_task(tid):
    if tid in tasks: return tasks[tid]["client"]
    if tid in extra_list: return CL[extra_list[tid]][0]
    return "Unknown"

hours_user=defaultdict(float); hours_user_day=defaultdict(lambda: defaultdict(float))
hours_user_task=defaultdict(float); hours_user_client=defaultdict(float); hours_client=defaultdict(float); hours_task=defaultdict(float)
for e in entries.values():
    hours_user[e["uid"]]+=e["h"]; hours_user_day[e["uid"]][e["day"]]+=e["h"]
    hours_user_task[(e["uid"],e["tid"])]+=e["h"]; hours_task[e["tid"]]+=e["h"]
    cl=client_of_task(e["tid"]); hours_user_client[(e["uid"],cl)]+=e["h"]; hours_client[cl]+=e["h"]

r1=lambda x: round(x+1e-9,1)
def initials(n):
    p=n.split(); return (p[0][0]+p[-1][0]).upper()

people=[]
all_uids=set(members)-set(canon)
for uid in all_uids:
    mine=[t for t in tasks.values() if uid in t["people"]]
    if not mine and hours_user.get(uid,0)==0: continue
    opn=[t for t in mine if t["group"]!="done"]
    done=[t for t in mine if t["done14"]]
    clients=defaultdict(lambda: dict(open=0,overdue=0,completed_14d=0,hours=0.0))
    for t in opn:
        clients[t["client"]]["open"]+=1; clients[t["client"]]["overdue"]+=t["overdue"]
    for t in done: clients[t["client"]]["completed_14d"]+=1
    for (u,cl),h in hours_user_client.items():
        if u==uid: clients[cl]["hours"]+=h
    cl_list=[dict(name=k,open=v["open"],overdue=v["overdue"],completed_14d=v["completed_14d"],hours=r1(v["hours"])) for k,v in clients.items()]
    cl_list.sort(key=lambda x:(-x["open"],-x["completed_14d"],-x["hours"],x["name"]))
    ov=sorted([t for t in opn if t["overdue"]],key=lambda t:t["due"])
    other=sorted([t for t in opn if not t["overdue"]],key=lambda t:(t["due"] is None,t["due"] or ""))
    dn=sorted(done,key=lambda t:t["updated"],reverse=True)
    tl=[]
    for t in ov+other+dn:
        rec=dict(id=t["id"],name=t["name"],client=t["client"],status=t["status"],group=t["group"],due=t["due"],overdue=t["overdue"],
                 priority=t["priority"],updated=t["updated"],hours=r1(hours_user_task.get((uid,t["id"]),0)),url=t["url"])
        if t["project"]: rec["project"]=t["project"]
        tl.append(rec)
    name=members[uid]
    people.append(dict(id=str(uid),name=name,first=name.split()[0],initials=initials(name),
        open=len(opn),active=sum(1 for t in opn if t["group"]=="active"),waiting=sum(1 for t in opn if t["group"]=="waiting"),
        overdue=sum(1 for t in opn if t["overdue"]),due_this_week=sum(1 for t in opn if t["due_this_week"]),completed_14d=len(done),
        hours=r1(hours_user.get(uid,0)),hours_by_day={k:r1(v) for k,v in sorted(hours_user_day[uid].items())},
        clients=cl_list,tasks=tl[:80]))
people.sort(key=lambda p:(-p["open"],-p["completed_14d"],p["name"]))

clients=defaultdict(lambda: dict(open=0,overdue=0,completed_14d=0,hours=0.0,people=defaultdict(int)))
for t in tasks.values():
    cc=clients[t["client"]]
    if t["group"]!="done":
        cc["open"]+=1; cc["overdue"]+=t["overdue"]
        for u in t["people"]: cc["people"][members[u]]+=1
    if t["done14"]:
        cc["completed_14d"]+=1
        for u in t["people"]: cc["people"][members[u]]+=0
for cl,h in hours_client.items(): clients[cl]["hours"]+=h
clist=[dict(name=k,open=v["open"],overdue=v["overdue"],completed_14d=v["completed_14d"],hours=r1(v["hours"]),
            people=[n for n,_ in sorted(v["people"].items(),key=lambda x:(-x[1],x[0]))]) for k,v in clients.items()]
clist.sort(key=lambda x:(-x["open"],-x["completed_14d"],x["name"]))

unassigned=[dict(id=t["id"],name=t["name"],client=t["client"],status=t["status"],due=t["due"],overdue=t["overdue"],priority=t["priority"],url=t["url"])
            for t in tasks.values() if t["group"]!="done" and not t["people"]]
unassigned.sort(key=lambda t:(t["due"] is None,t["due"] or ""))

opn=[t for t in tasks.values() if t["group"]!="done"]
totals=dict(open=len(opn),overdue=sum(1 for t in opn if t["overdue"]),due_this_week=sum(1 for t in opn if t["due_this_week"]),
            completed_14d=sum(1 for t in tasks.values() if t["done14"]),hours=r1(sum(hours_user.values())),
            people_with_hours=sum(1 for p in people if p["hours"]>0),people_active=sum(1 for p in people if p["open"]>0))

notes=list(dict.fromkeys(notes))
notes+= [
 "Time entries: plain-date queries (YYYY-MM-DD) proved date-shifted (query for 2026-11-12 returned entries started 2026-11-13), so every day 2026-10-19..2026-11-17 was re-queried with explicit 00:00-23:59 windows in Africa/Maputo plus 20:00-04:00 night windows, because the API only returns entries fully inside the window and Pedro's bulk entries start at 22:59 and cross midnight.",
 "Plain-date query for 2026-11-04 and the night window 2026-11-04 20:00 - 2026-11-05 04:00 (and sub-windows 22:58-00:00, 22:58-00:59, 22:58-01:00, 22:58-02:00) failed with 'Tool result does not match outputSchema' because 2-3 entries have no task attached; those task-less entries (all start 2026-11-04 22:59, 1h each) could not be read and are not counted.",
 "To recover the 2026-11-04 night batch, time entries were fetched per task for all 108 of Pedro Milreu's tasks (dedupe by entry id); entries on other people's tasks or on subtasks not in the task set would be missed, but none were seen in any window.",
 "%d timer-test entries under 5 minutes ignored (Francisco Caetano 2026-10-19, Pedro Milreu 2026-11-05)."%short,
 "Only Pedro Milreu has tracked hours in the window; all entries are manual blocks (1h-4h) logged in bulk on 2026-11-03, 2026-11-04 and 2026-11-13.",
 "Task hours on subtasks/cancelled tasks not in the task list (Criar Script para a gracacao, Follow Up Mariana, Follow up, marcar reuniao) are attributed to their client (Absa, HCB, ECOLOG) but do not appear in per-task lists.",
 "completed_14d uses date_closed when present, otherwise date_updated; many Sasol tasks share date_updated 2026-11-12 (bulk edit) and are counted as completed in the last 14 days.",
 "Tasks with no due date were taken from the first 3 pages of an order_by=updated query only; older open tasks without due date may be missing.",
 "Subtasks excluded (subtasks=false).",
 "Pedro Milreu's tracked hours are not plausible as elapsed time: 36h logged on 2026-11-03 and 126h on 2026-11-04 (dozens of 1h-4h entries all starting 22:59, overlapping). Treat hours as retroactive effort estimates per task, not time worked that day.",
]
out=dict(generated_at=datetime.datetime.now(TZ).replace(microsecond=0).isoformat(),week_start=WEEK_START,
         hours_window={"from":"2026-10-19","to":"2026-11-17"},totals=totals,people=people,clients=clist,unassigned=unassigned,
         data_quality=dict(tasks_fetched=len(tasks),time_entries=len(entries),notes=notes))
s="{\n"+",\n".join('"%s": %s'%(k,json.dumps(v,ensure_ascii=False,separators=(",",":"))) for k,v in out.items())+"\n}\n"
open("/home/user/profile/brief/team-data.json","w",encoding="utf-8").write(s)
print(totals); print(len(people),len(clist),len(unassigned),len(tasks),len(entries))
for p in people: print(p["name"],p["open"],p["overdue"],p["due_this_week"],p["completed_14d"],p["hours"],p["hours_by_day"])
