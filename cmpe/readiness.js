"use strict";
const el=(t,v)=>{let x=document.createElement(t);x.textContent=v;return x};
async function main(){
 const [a,b]=await Promise.all([fetch("/v1/readiness"),fetch("/v1/catalog")]);
 if(!a.ok||!b.ok)throw Error("verified service metadata unavailable");
 const r=await a.json(),c=await b.json();
 document.getElementById("state").textContent=r.national_planning_ready?"Data readiness assessed":"National planning: NOT READY";
 document.getElementById("statetext").textContent=r.independently_calibrated_domains+" of "+r.required_information_domains+" required domains independently calibrated. "+r.note;
 const root=document.getElementById("sectors");
 for(const x of c.requirements){
  const card=el("article","");card.append(el("strong",x.code.replaceAll("_"," ")),el("p",x.data),el("small","Cadence: "+x.update_frequency+" | Independent check: "+x.cross_check));root.append(card)
 }
}
main().catch(e=>{document.getElementById("state").textContent="Data readiness unavailable";document.getElementById("statetext").textContent="Failing closed: "+String(e)});
