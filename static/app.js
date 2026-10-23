"use strict";
const $=i=>document.getElementById(i);
async function ld(){
  try{
    const r=await fetch("/api/dorks"),d=await r.json(),s=$("cat");
    const L={login:"دخول",error:"أخطاء",directory:"فهرسة",docs:"مستندات",backup:"نسخ",logs:"سجلات",config:"إعدادات",password:"كلمات مرور",bigbackup:"نسخ ضخمة",database:"قواعد",archive:"أرشيفات",diskimg:"أقراص",media:"وسائط",git:"Git",env:".env",aws:"AWS",api_keys:"API",jenkins:"Jenkins",grafana:"Grafana",kibana:"Kibana",docker:"Docker",cctv:"كاميرات"};
    for(const k in d){const o=document.createElement("option");o.value=k;o.textContent=L[k]||k;s.appendChild(o)}
  }catch(e){}
}
async function gen(){
  $("msg").textContent="";
  const p={cat:$("cat").value,site:$("site").value,ft:$("ft").value,it:$("it").value,iu:$("iu").value,ix:$("ix").value,ex:$("ex").value,cu:$("cu").value,engine:$("eng").value};
  try{
    const r=await fetch("/api/build",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(p)}),d=await r.json();
    if(!r.ok){$("msg").textContent=d.error;$("res").hidden=true;return}
    show(d.query,d.url);lh()
  }catch(e){$("msg").textContent="خطأ: "+e.message}
}
function show(q,u){$("q").textContent=q;if(u)$("go").href=u;$("res").hidden=false}
async function lh(){
  try{
    const r=await fetch("/api/history"),h=await r.json(),b=$("hist"),l=$("hl");
    l.innerHTML="";
    if(!h.length){b.hidden=true;return}
    b.hidden=false;
    const E={google:"https://www.google.com/search?q=",bing:"https://www.bing.com/search?q=",duckduckgo:"https://duckduckgo.com/?q=",startpage:"https://www.startpage.com/sp/search?query=",brave:"https://search.brave.com/search?q="};
    for(const e of h){
      const d=document.createElement("div");
      d.className="h";d.textContent=e.query;d.title=e.ts;
      d.onclick=()=>show(e.query,(E[e.engine]||E.google)+encodeURIComponent(e.query));
      l.appendChild(d)
    }
  }catch(e){}
}
async function cp(){try{await navigator.clipboard.writeText($("q").textContent);$("msg").textContent="✓ تم النسخ"}catch{$("msg").textContent="تعذر"}}
function clr(){["site","ft","it","iu","ix","ex","cu"].forEach(i=>$(i).value="");$("cat").value="";$("res").hidden=true;$("msg").textContent=""}
async function exp(f){
  const r=await fetch("/api/export",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({format:f})});
  const b=await r.blob(),a=document.createElement("a");
  a.href=URL.createObjectURL(b);a.download="gdork."+f;a.click()
}
$("gen").onclick=gen;$("cp").onclick=cp;$("clr").onclick=clr;
$("dm").onclick=()=>{document.body.classList.toggle("dark");localStorage.setItem("dark",document.body.classList.contains("dark")?"1":"0")};
$("hc").onclick=async()=>{await fetch("/api/history/clear",{method:"POST"});lh()};
$("expj").onclick=()=>exp("json");$("expc").onclick=()=>exp("csv");
$("eng").onchange=()=>{if(!$("res").hidden)gen()};
if(localStorage.getItem("dark")==="1")document.body.classList.add("dark");
ld();lh();
