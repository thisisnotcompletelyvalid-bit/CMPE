const out=document.getElementById("output");
function show(data){out.textContent=JSON.stringify(data,null,2)}
async function call(path,method="GET",body=null){
  const headers={"X-CMPE-Key":document.getElementById("key").value};
  if(body!==null)headers["Content-Type"]="application/json";
  const r=await fetch(path,{method,headers,body:body===null?undefined:JSON.stringify(body)});
  const data=await r.json();show({http_status:r.status,data});
}
fetch("/health/ready").then(r=>r.json().then(x=>document.getElementById("health").textContent=r.status+" · "+JSON.stringify(x))).catch(()=>document.getElementById("health").textContent="Disconnected");
for(const [id,path,method] of [["status","/v1/status","GET"],["datasets","/v1/datasets","GET"],["observations","/v1/observations","GET"],["plan","/v1/plans","POST"]]){
 document.getElementById(id).addEventListener("click",()=>call(path,method).catch(e=>show({error:String(e)})));
}
document.getElementById("submit").addEventListener("click",async()=>{
 try{
 const file=document.getElementById("dataset-file").files[0];
 if(!file || file.size>512000)throw new Error("Select a valid JSON file below 512 KB");
 await call("/v1/datasets","POST",JSON.parse(await file.text()));
 }catch(e){show({error:String(e)})}
});
document.getElementById("approve").addEventListener("click",()=>{
 const id=Number(document.getElementById("dataset-id").value);
 if(!Number.isSafeInteger(id)||id<1){show({error:"Enter valid dataset ID"});return}
 call("/v1/datasets/"+id+"/approve","POST").catch(e=>show({error:String(e)}));
});
