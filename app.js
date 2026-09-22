const KEY="nexxty_one_leads_v2";
let leads=loadLeads(), lastResults=[];

const categories={
 "Restaurantes":[["amenity","restaurant"],["amenity","fast_food"],["amenity","food_court"]],
 "Cafés":[["amenity","cafe"]],"Bares":[["amenity","bar"],["amenity","pub"]],
 "Hotéis":[["tourism","hotel"],["tourism","hostel"],["tourism","guest_house"]],
 "Lojas":[["shop","*"]],"Barbearias":[["shop","hairdresser"],["shop","beauty"]],
 "Farmácias":[["amenity","pharmacy"]],"Academias":[["leisure","fitness_centre"],["sport","fitness"]],
 "Imobiliárias":[["office","estate_agent"]],"Advogados":[["office","lawyer"]],
 "Fotógrafos":[["craft","photographer"]],"Oficinas":[["shop","car_repair"],["shop","motorcycle"]],
 "Pet shops":[["shop","pet"]],"Dentistas":[["amenity","dentist"],["amenity","doctors"]],
 "Clínicas":[["amenity","clinic"],["amenity","doctors"]],"Salões de beleza":[["shop","beauty"],["shop","hairdresser"]],
 "Padarias":[["shop","bakery"]],"Mercados":[["shop","supermarket"],["shop","convenience"]],
 "Concessionárias":[["shop","car"]],"Escolas":[["amenity","school"],["amenity","college"]],
 "Veterinários":[["amenity","veterinary"]],"Floriculturas":[["shop","florist"]],
 "Lojas de roupas":[["shop","clothes"],["shop","fashion"]],"Móveis":[["shop","furniture"]]
};

function loadLeads(){try{return JSON.parse(localStorage.getItem(KEY)||"[]")}catch(e){return[]}}
function save(){localStorage.setItem(KEY,JSON.stringify(leads)); renderAll()}
function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function toast(msg){const x=document.getElementById("toast");x.textContent=msg;x.classList.add("show");setTimeout(()=>x.classList.remove("show"),2600)}
function normPhone(v){let n=String(v||"").replace(/\D/g,"");if(n.startsWith("55")&&n.length>=12)n=n.slice(2);return n}
function phone(v){let n=normPhone(v);return n.length===11?`(${n.slice(0,2)}) ${n.slice(2,7)}-${n.slice(7)}`:n.length===10?`(${n.slice(0,2)}) ${n.slice(2,6)}-${n.slice(6)}`:(v||"")}
function url(v){if(!v)return"";v=String(v).trim();return /^https?:\/\//i.test(v)?v:"https://"+v}
function key(x){return (x.Nome||"").trim().toLowerCase()+"|"+(x.Cidade||"").trim().toLowerCase()}
function badge(status){let c=status==="Cliente"?"cliente":status==="Respondeu"?"respondeu":status==="Contato feito"?"contato":status==="Sem interesse"?"sem":"";return `<span class="badge ${c}">${esc(status||"Novo lead")}</span>`}
function table(data, editable=false){
 if(!data.length)return `<div class="empty">Nenhum lead encontrado.<br><br><button class="primary" data-go="search">Procurar novos negócios</button></div>`;
 return `<div class="table-wrap"><table><thead><tr><th>Nome</th><th>Cidade</th><th>Telefone</th><th>WhatsApp</th><th>Instagram</th><th>Site</th><th>Status</th><th>Fonte</th>${editable?"<th></th>":""}</tr></thead><tbody>${data.map((x,i)=>`<tr>
 <td><b>${esc(x.Nome)}</b></td><td>${esc(x.Cidade)}</td><td>${esc(phone(x.Telefone))}</td>
 <td>${x.WhatsApp?`<a target="_blank" href="${esc(url(x.WhatsApp))}">Abrir</a>`:"—"}</td>
 <td>${x.Instagram?`<a target="_blank" href="${esc(url(x.Instagram))}">Instagram</a>`:"—"}</td>
 <td>${x.Site?`<a target="_blank" href="${esc(url(x.Site))}">Abrir</a>`:"—"}</td>
 <td>${editable?`<select class="row-status" data-index="${leads.indexOf(x)}">${["Novo lead","Contato feito","Respondeu","Cliente","Sem interesse"].map(s=>`<option ${s===(x.Status||"Novo lead")?"selected":""}>${s}</option>`).join("")}</select>`:badge(x.Status)}</td>
 <td>${esc(x.Fonte||"OSM")}</td>${editable?`<td><button class="mini-delete" data-index="${leads.indexOf(x)}">×</button></td>`:""}</tr>`).join("")}</tbody></table></div>`
}
function renderAll(){
 document.getElementById("mTotal").textContent=leads.length;
 document.getElementById("mNew").textContent=leads.filter(x=>(x.Status||"Novo lead")==="Novo lead").length;
 document.getElementById("mReply").textContent=leads.filter(x=>x.Status==="Respondeu").length;
 document.getElementById("mClients").textContent=leads.filter(x=>x.Status==="Cliente").length;
 document.getElementById("mSites").textContent=leads.filter(x=>x.Site).length;
 document.getElementById("settingsCount").textContent=leads.length;
 document.getElementById("recentTable").innerHTML=table(leads.slice(-10).reverse());
 renderLeads();
}
function renderLeads(){
 let q=(document.getElementById("leadSearch")?.value||"").toLowerCase(), st=document.getElementById("statusFilter")?.value||"Todos";
 let d=leads.filter(x=>!q||[x.Nome,x.Cidade,x.Telefone].join(" ").toLowerCase().includes(q)).filter(x=>st==="Todos"||x.Status===st);
 document.getElementById("allTable").innerHTML=table(d,true);
 document.querySelectorAll(".row-status").forEach(s=>s.onchange=()=>{leads[+s.dataset.index].Status=s.value;save();toast("Status atualizado")});
 document.querySelectorAll(".mini-delete").forEach(b=>b.onclick=()=>{if(confirm("Excluir este lead?")){leads.splice(+b.dataset.index,1);save();toast("Lead excluído")}})
}
function fillCategories(){
 for(const id of ["category","quickCategory"]){const s=document.getElementById(id);s.innerHTML=Object.keys(categories).map(x=>`<option>${x}</option>`).join("")}
}
function go(page){document.querySelectorAll(".page").forEach(p=>p.classList.toggle("active",p.id===page));document.querySelectorAll(".nav-item").forEach(n=>n.classList.toggle("active",n.dataset.page===page));window.scrollTo({top:0,behavior:"smooth"});if(page==="leads")renderLeads()}
document.addEventListener("click",e=>{const g=e.target.closest("[data-go]");if(g)go(g.dataset.go);const n=e.target.closest(".nav-item");if(n)go(n.dataset.page)});
document.getElementById("leadSearch").oninput=renderLeads;document.getElementById("statusFilter").onchange=renderLeads;
document.getElementById("globalSearch").oninput=e=>{const q=e.target.value.trim();if(q){go("leads");document.getElementById("leadSearch").value=q;renderLeads()}};
document.getElementById("clearSearch").onclick=()=>{document.getElementById("globalSearch").value="";document.getElementById("leadSearch").value="";renderLeads()};

async function nominatim(city){
 const r=await fetch("https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&countrycodes=br&q="+encodeURIComponent(city+", Brasil"));
 if(!r.ok)throw Error("Não foi possível localizar a cidade.");
 const a=await r.json();if(!a.length)throw Error(`Cidade não encontrada: ${city}`);
 return {south:+a[0].boundingbox[0],north:+a[0].boundingbox[1],west:+a[0].boundingbox[2],east:+a[0].boundingbox[3]};
}
function query(tags,b){return `[out:json][timeout:55];(${tags.map(t=>t[1]==="*" ? `nwr["${t[0]}"](${b.south},${b.west},${b.north},${b.east});`:`nwr["${t[0]}"="${t[1]}"](${b.south},${b.west},${b.north},${b.east});`).join("")});out center tags;`}
async function overpass(q){
 const servers=["https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter"];
 let last;
 for(const s of servers){try{const r=await fetch(s,{method:"POST",body:q});if(r.ok)return await r.json();last=r}catch(e){last=e}}
 throw last||Error("Falha na busca");
}
function parseElements(data,city){
 const out=[];for(const el of data.elements||[]){const t=el.tags||{};const name=(t.name||t.brand||t.operator||"").trim();if(!name)continue;
  let website=t.website||t["contact:website"]||t.url||"", insta=t["contact:instagram"]||"", wa=t["contact:whatsapp"]||"", tel=t.phone||t["contact:phone"]||t.telephone||"";
  out.push({Nome:name,Cidade:city,Telefone:phone(tel),WhatsApp:url(wa),Instagram:url(insta),Site:url(website),Status:"Novo lead",Fonte:"OpenStreetMap",Observações:""});
 }
 const m=new Map();out.forEach(x=>m.set(key(x),x));return [...m.values()]
}
async function searchBusinesses(category,cities,limit,onlyNew){
 const all=[];let done=0;const status=document.getElementById("searchStatus");status.innerHTML=`<div class="progress"><i id="prog"></i></div><p class="muted" id="progText">Preparando pesquisa...</p>`;
 for(const city of cities){try{const b=await nominatim(city);const data=await overpass(query(categories[category],b));let a=parseElements(data,city);if(onlyNew)a=a.filter(x=>!leads.some(l=>key(l)===key(x)));a=a.slice(0,limit);all.push(...a)}catch(e){console.warn(e)}done++;document.getElementById("prog").style.width=(done/cities.length*100)+"%";document.getElementById("progText").textContent=`Pesquisadas ${done} de ${cities.length} cidade(s)...` }
 const m=new Map();all.forEach(x=>m.set(key(x),x));return [...m.values()]
}
async function runSearch(){
 const category=document.getElementById("category").value,cities=document.getElementById("cities").value.split(",").map(x=>x.trim()).filter(Boolean),limit=Math.max(5,Math.min(100,+document.getElementById("limit").value||30)),only=document.getElementById("newOnly").checked;
 if(!cities.length){toast("Digite pelo menos uma cidade.");return}
 const btn=document.getElementById("searchBtn");btn.disabled=true;btn.textContent="⌛ Pesquisando...";
 try{lastResults=await searchBusinesses(category,cities,limit,only);document.getElementById("resultsPanel").hidden=false;document.getElementById("resultsInfo").textContent=`${lastResults.length} resultado(s) novo(s) encontrado(s).`;document.getElementById("resultsTable").innerHTML=table(lastResults);toast(lastResults.length?`${lastResults.length} novos negócios encontrados!`:"Nenhum negócio novo encontrado nessa busca.");if(document.getElementById("autoSave").checked&&lastResults.length){leads=[...leads,...lastResults];save();toast("Resultados salvos na sua base.")}}catch(e){toast("Erro na pesquisa. Tente novamente.");console.error(e)}finally{btn.disabled=false;btn.textContent="⌕  Procurar novos negócios";document.getElementById("searchStatus").innerHTML=""}
}
document.getElementById("searchBtn").onclick=runSearch;
document.getElementById("quickSearchBtn").onclick=()=>{go("search");document.getElementById("category").value=document.getElementById("quickCategory").value;document.getElementById("cities").value=document.getElementById("quickCity").value;document.getElementById("limit").value=document.getElementById("quickLimit").value;document.getElementById("newOnly").checked=document.getElementById("onlyNew").checked;runSearch()};
document.getElementById("saveResults").onclick=()=>{if(!lastResults.length)return;let n=0;lastResults.forEach(x=>{if(!leads.some(l=>key(l)===key(x))){leads.push(x);n++}});save();toast(`${n} lead(s) salvo(s).`)};
document.getElementById("exportBtn").onclick=()=>downloadCSV();
document.getElementById("exportQuick").onclick=()=>downloadCSV();
document.getElementById("backupBtn").onclick=()=>downloadCSV("nexxty-one-backup.csv");
document.getElementById("backupQuick").onclick=()=>downloadCSV("nexxty-one-backup.csv");
function csvEscape(v){return `"${String(v??"").replace(/"/g,'""')}"`}
function downloadCSV(name="nexxty-one-leads.csv"){const cols=["Nome","Cidade","Telefone","WhatsApp","Instagram","Site","Status","Fonte","Observações"];const text="\ufeff"+[cols,...leads.map(x=>cols.map(c=>x[c]||""))].map(r=>r.map(csvEscape).join(";")).join("\n");const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([text],{type:"text/csv;charset=utf-8"}));a.download=name;a.click();URL.revokeObjectURL(a.href)}
document.getElementById("importBtn").onclick=()=>{const f=document.getElementById("csvFile").files[0];if(!f){toast("Escolha um CSV primeiro.");return}const rd=new FileReader();rd.onload=()=>{const rows=parseCSV(rd.result);let n=0;rows.forEach(x=>{if(x.Nome&&!leads.some(l=>key(l)===key(x))){leads.push({...x,Status:x.Status||"Novo lead"});n++}});save();document.getElementById("importStatus").textContent=`${n} novos leads importados.`;toast(`${n} leads importados.`)};rd.readAsText(f,"UTF-8")}
function parseCSV(txt){const lines=txt.replace(/^\ufeff/,"").split(/\r?\n/).filter(Boolean),head=splitCSV(lines.shift()).map(x=>x.trim());return lines.map(l=>{const v=splitCSV(l),o={};head.forEach((h,i)=>o[h]=v[i]||"");return o})}
function splitCSV(line){const out=[];let cur="",q=false;for(let i=0;i<line.length;i++){const c=line[i];if(c==='"'&&line[i+1]==='"'){cur+='"';i++}else if(c==='"')q=!q;else if((c===";"||c===",")&&!q){out.push(cur);cur=""}else cur+=c}out.push(cur);return out}
document.getElementById("clearData").onclick=()=>{if(confirm("Isso apagará todos os leads salvos neste navegador. Continuar?")){leads=[];save();toast("Base apagada.")}};
fillCategories();renderAll();
