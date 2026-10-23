#!/usr/bin/env python3
import json, os, webbrowser, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, quote
from datetime import datetime

HOST="127.0.0.1"; PORT=int(os.environ.get("GDORK_PORT",8765))
BASE=os.path.dirname(os.path.abspath(__file__))
STATIC=os.path.join(BASE,"static")
HIST=os.path.join(BASE,"history.json")
DORKS=os.path.join(BASE,"dorks.json")

def load_dorks():
    return json.load(open(DORKS,encoding="utf-8")) if os.path.exists(DORKS) else {}

def load_hist():
    try: return json.load(open(HIST,encoding="utf-8"))
    except: return []

def save_hist(h): json.dump(h[:200],open(HIST,"w",encoding="utf-8"),ensure_ascii=False,indent=2)

def add_hist(q,e):
    h=load_hist()
    h=[{"query":q,"engine":e,"ts":datetime.now().isoformat(timespec="seconds")}]+[x for x in h if x.get("query")!=q][:199]
    save_hist(h)

def op(v,o):
    v=(v or "").strip()
    return "" if not v else (v if v.lower().startswith(o+":") else f"{o}:{v}")

def build(p,d):
    r=[]
    if p.get("cat") and p["cat"] in d: r.append(d[p["cat"]])
    for f,o in [("site","site"),("ft","filetype"),("it","intitle"),("iu","inurl"),("ix","intext")]:
        x=op(p.get(f,""),o)
        if x: r.append(x)
    for w in (p.get("ex","") or "").split():
        w=w.lstrip("-")
        if w: r.append("-"+w)
    if (p.get("cu","") or "").strip(): r.append(p["cu"].strip())
    return " ".join(r)

ENG={"google":"https://www.google.com/search?q=","bing":"https://www.bing.com/search?q=","duckduckgo":"https://duckduckgo.com/?q=","startpage":"https://www.startpage.com/sp/search?query=","brave":"https://search.brave.com/search?q="}

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _s(self,c,b,ct="text/plain; charset=utf-8"):
        if isinstance(b,str): b=b.encode()
        self.send_response(c)
        self.send_header("Content-Type",ct)
        self.send_header("Content-Length",str(len(b)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(b)
    def _j(self,c,o): self._s(c,json.dumps(o,ensure_ascii=False),"application/json; charset=utf-8")
    def _f(self,p):
        p="/index.html" if p in("","/") else p
        s=os.path.normpath(p).lstrip("/")
        f=os.path.join(STATIC,s)
        if not f.startswith(STATIC) or not os.path.isfile(f):
            return self._s(404,"Not Found")
        e=os.path.splitext(f)[1].lower()
        ct={".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",".js":"application/javascript; charset=utf-8"}.get(e,"application/octet-stream")
        self._s(200,open(f,"rb").read(),ct)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/api/dorks": self._j(200,load_dorks())
        elif p=="/api/history": self._j(200,load_hist())
        elif p=="/api/health": self._j(200,{"status":"ok"})
        else: self._f(p)
    def do_POST(self):
        p=urlparse(self.path).path
        n=int(self.headers.get("Content-Length","0"))
        try: d=json.loads(self.rfile.read(n).decode()) if n else {}
        except: return self._j(400,{"error":"bad json"})
        if p=="/api/build":
            q=build(d,load_dorks())
            if not q: return self._j(400,{"error":"empty query"})
            e=d.get("engine","google")
            add_hist(q,e)
            self._j(200,{"query":q,"url":ENG.get(e,ENG["google"])+quote(q)})
        elif p=="/api/history/clear":
            save_hist([])
            self._j(200,{"ok":True})
        elif p=="/api/export":
            h=load_hist()
            fmt=d.get("format","json")
            if fmt=="csv":
                lines=["timestamp,engine,query"]+[f'"{x["ts"]}","{x["engine"]}","{x["query"].replace(chr(34),chr(34)*2)}"' for x in h]
                self._s(200,"\n".join(lines),"text/csv; charset=utf-8")
            else:
                self._s(200,json.dumps(h,ensure_ascii=False,indent=2),"application/json; charset=utf-8")
        else:
            self._j(404,{"error":"not found"})

def main():
    s=HTTPServer((HOST,PORT),H)
    url=f"http://{HOST}:{PORT}/"
    print(f"[+] {url}")
    print("[+] Ctrl+C للإيقاف")
    threading.Timer(1.0,lambda:webbrowser.open(url)).start()
    try: s.serve_forever()
    except KeyboardInterrupt: s.server_close()

if __name__=="__main__": main()
