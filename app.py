import streamlit as st
import pandas as pd
import requests
import re
import os
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="NEXXTY ONE", page_icon="✦", layout="wide")

ARQUIVO = "restaurantes.csv"
BACKUP = "restaurantes_backup.csv"

COLUNAS = [
    "Nome", "Cidade", "Telefone", "WhatsApp", "Instagram",
    "Site", "Tem site?", "Status", "Fonte", "Observações"
]

CATEGORIAS = {
    "Restaurantes": [("amenity", "restaurant"), ("amenity", "fast_food"), ("amenity", "food_court")],
    "Cafés": [("amenity", "cafe")],
    "Bares": [("amenity", "bar"), ("amenity", "pub")],
    "Hotéis": [("tourism", "hotel"), ("tourism", "hostel"), ("tourism", "guest_house")],
    "Lojas": [("shop", "*")],
    "Barbearias": [("shop", "hairdresser"), ("shop", "beauty")],
    "Farmácias": [("amenity", "pharmacy")],
    "Academias": [("leisure", "fitness_centre"), ("sport", "fitness")],
    "Imobiliárias": [("office", "estate_agent")],
    "Advogados": [("office", "lawyer")],
    "Fotógrafos": [("craft", "photographer")],
    "Oficinas": [("shop", "car_repair"), ("shop", "motorcycle")],
    "Pet shops": [("shop", "pet")],
    "Dentistas": [("amenity", "dentist")],
    "Clínicas": [("amenity", "clinic"), ("amenity", "doctors")],
    "Salões de beleza": [("shop", "beauty"), ("shop", "hairdresser")],
    "Padarias": [("shop", "bakery")],
    "Mercados": [("shop", "supermarket"), ("shop", "convenience")],
    "Concessionárias": [("shop", "car")],
    "Escolas": [("amenity", "school"), ("amenity", "college")],
    "Veterinários": [("amenity", "veterinary")],
    "Floriculturas": [("shop", "florist")],
    "Lojas de roupas": [("shop", "clothes"), ("shop", "fashion")],
    "Móveis": [("shop", "furniture")]
}

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at top right,#12364b 0%,#061321 40%,#04101c 100%); color:#e9ffff;}
[data-testid="stSidebar"] {background:#071a2b;border-right:1px solid #1d4d63;}
[data-testid="stSidebar"] * {color:#e9ffff !important;}
h1,h2,h3 {color:#b8f4ef !important;}
.nexxty-logo {font-size:38px;font-weight:900;letter-spacing:5px;color:#b8f4ef;}
.nexxty-subtitle {color:#7896a4;font-size:15px;margin-bottom:25px;}
.card {background:rgba(7,26,43,.88);border:1px solid #1d4d63;border-radius:18px;padding:22px;margin-bottom:18px;}
.metric {background:rgba(7,26,43,.9);border:1px solid #1d4d63;border-radius:18px;padding:20px;text-align:center;}
.metric-number {font-size:32px;font-weight:900;color:#b8f4ef;}
.metric-label {color:#7896a4;font-size:13px;margin-top:5px;}
.stButton button {background:#b8f4ef;color:#04101c;border:0;border-radius:10px;font-weight:800;min-height:44px;}
.stButton button:hover {background:#86d9d4;}
.stTextInput input,.stTextArea textarea,.stNumberInput input {background:#071a2b !important;color:#e9ffff !important;border:1px solid #1d4d63 !important;border-radius:10px !important;}
.small-muted {color:#7896a4;font-size:13px;}
</style>
""", unsafe_allow_html=True)

def headers():
    return {"User-Agent": "NEXXTY-ONE/2.0 public-data-research-app"}

def garantir_csv():
    if not os.path.exists(ARQUIVO):
        pd.DataFrame(columns=COLUNAS).to_csv(ARQUIVO, index=False, encoding="utf-8-sig")

def carregar_dados():
    garantir_csv()
    try:
        df = pd.read_csv(ARQUIVO, encoding="utf-8-sig")
    except Exception:
        df = pd.DataFrame(columns=COLUNAS)
    for c in COLUNAS:
        if c not in df.columns:
            df[c] = ""
    return df[COLUNAS].fillna("")

def salvar_dados(df):
    for c in COLUNAS:
        if c not in df.columns:
            df[c] = ""
    df[COLUNAS].fillna("").to_csv(ARQUIVO, index=False, encoding="utf-8-sig")

def get(url, **kwargs):
    kwargs.setdefault("headers", headers())
    kwargs.setdefault("timeout", 25)
    try:
        return requests.get(url, **kwargs)
    except requests.RequestException:
        return None

def post(url, **kwargs):
    kwargs.setdefault("headers", headers())
    kwargs.setdefault("timeout", 70)
    try:
        return requests.post(url, **kwargs)
    except requests.RequestException:
        return None

def normalizar_telefone(valor):
    if not valor:
        return ""
    n = re.sub(r"\D", "", str(valor))
    if n.startswith("55") and len(n) >= 12:
        n = n[2:]
    return n if len(n) in (10, 11) else ""

def formatar_telefone(valor):
    n = normalizar_telefone(valor)
    if len(n) == 11: return f"({n[:2]}) {n[2:7]}-{n[7:]}"
    if len(n) == 10: return f"({n[:2]}) {n[2:6]}-{n[6:]}"
    return str(valor or "")

def extrair_telefones(texto):
    if not texto: return []
    padroes = [
        r"\+55\s*\(?\s*\d{2}\s*\)?\s*\d{4,5}[-.\s]?\d{4}",
        r"\(?\s*\d{2}\s*\)?\s*\d{4,5}[-.\s]?\d{4}"
    ]
    out = []
    for p in padroes:
        for item in re.findall(p, texto):
            n = normalizar_telefone(item)
            if n and n not in out: out.append(n)
    return out

def limpar_url(url):
    if not url: return ""
    url = str(url).strip()
    if url.startswith("//"): url = "https:" + url
    if not url.startswith(("http://","https://")): url = "https://" + url
    return url.split("?")[0].rstrip("/")

def extrair_instagram(texto):
    if not texto: return ""
    p = r"(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)"
    ignorar = {"p","reel","reels","stories","explore","accounts"}
    for user in re.findall(p, texto, re.I):
        if user.lower() not in ignorar:
            return "https://instagram.com/" + user
    return ""

@st.cache_data(ttl=3600, show_spinner=False)
def localizar_cidade(cidade):
    for q in (f"{cidade}, Minas Gerais, Brasil", f"{cidade}, Brasil"):
        r = get("https://nominatim.openstreetmap.org/search",
                params={"q":q,"format":"jsonv2","limit":5,"countrycodes":"br"})
        if not r or r.status_code != 200: continue
        try: dados = r.json()
        except Exception: continue
        if not dados: continue
        item = dados[0]
        for x in dados:
            if x.get("type") in {"city","town","municipality","administrative"}:
                item = x; break
        bbox = item.get("boundingbox")
        if not bbox or len(bbox) != 4: continue
        try:
            return {"south":float(bbox[0]),"north":float(bbox[1]),"west":float(bbox[2]),"east":float(bbox[3])}
        except Exception: pass
    return None

def montar_consulta(tags, s,w,n,e):
    partes=[]
    for chave, valor in tags:
        if valor=="*":
            partes.append(f'nwr["{chave}"]({s},{w},{n},{e});')
        else:
            partes.append(f'nwr["{chave}"="{valor}"]({s},{w},{n},{e});')
    return f'[out:json][timeout:60];({"".join(partes)});out center tags;'

@st.cache_data(ttl=600, show_spinner=False)
def buscar_osm(categoria, cidade):
    local = localizar_cidade(cidade)
    if not local: return []
    s=local["south"]-.015; w=local["west"]-.015
    n=local["north"]+.015; e=local["east"]+.015
    consulta=montar_consulta(CATEGORIAS[categoria],s,w,n,e)
    servidores=[
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.private.coffee/api/interpreter"
    ]
    dados=None
    for servidor in servidores:
        for _ in range(2):
            r=post(servidor,data=consulta)
            if r and r.status_code==200:
                try:
                    dados=r.json()
                    if "elements" in dados: break
                except Exception: pass
        if dados is not None: break
    if not dados: return []
    out=[]
    for el in dados.get("elements",[]):
        t=el.get("tags",{})
        nome=(t.get("name") or t.get("brand") or t.get("operator") or "").strip()
        if not nome: continue
        site=t.get("website") or t.get("contact:website") or t.get("url") or ""
        insta=t.get("contact:instagram") or ""
        whats=t.get("contact:whatsapp") or ""
        tel=t.get("phone") or t.get("contact:phone") or t.get("telephone") or ""
        out.append({
            "Nome":nome,"Cidade":cidade,"Telefone":formatar_telefone(tel),
            "WhatsApp":limpar_url(whats),"Instagram":limpar_url(insta),
            "Site":limpar_url(site),"Tem site?":"Sim" if site else "Não",
            "Status":"Novo lead","Fonte":"OpenStreetMap","Observações":""
        })
    unicos={}
    for x in out:
        unicos[(x["Nome"].lower().strip(),x["Cidade"].lower().strip())]=x
    return list(unicos.values())

def buscar_web(nome,cidade):
    resultados=[]
    consultas=[f'"{nome}" "{cidade}"',f'"{nome}" "{cidade}" telefone',
               f'"{nome}" "{cidade}" instagram',f'"{nome}" "{cidade}" site']
    for q in consultas:
        try:
            r=get("https://html.duckduckgo.com/html/",params={"q":q},timeout=15)
            if not r or r.status_code!=200: continue
            soup=BeautifulSoup(r.text,"html.parser")
            for item in soup.select(".result")[:8]:
                link=item.select_one(".result__a"); sn=item.select_one(".result__snippet")
                if link:
                    resultados.append({"titulo":link.get_text(" ",strip=True),
                                       "url":link.get("href",""),
                                       "texto":sn.get_text(" ",strip=True) if sn else ""})
        except Exception: pass
    return resultados

def analisar_site(url):
    out={"telefone":"","whatsapp":"","instagram":""}
    if not url: return out
    try:
        r=get(url,timeout=12)
        if not r or r.status_code>=400: return out
        out["telefone"]=(extrair_telefones(r.text) or [""])[0]
        out["instagram"]=extrair_instagram(r.text)
        soup=BeautifulSoup(r.text,"html.parser")
        for a in soup.find_all("a",href=True):
            href=a.get("href","")
            if "instagram.com/" in href.lower(): out["instagram"]=limpar_url(href)
            if "wa.me/" in href.lower() or "whatsapp.com" in href.lower(): out["whatsapp"]=href
    except Exception: pass
    return out

def enriquecer_lead(lead):
    x=lead.copy()
    web=buscar_web(x["Nome"],x["Cidade"])
    texto=" ".join(i["titulo"]+" "+i["texto"]+" "+i["url"] for i in web)
    if not x["Telefone"]:
        ts=extrair_telefones(texto)
        if ts: x["Telefone"]=formatar_telefone(ts[0])
    if not x["Instagram"]:
        x["Instagram"]=extrair_instagram(texto)
    if not x["Site"]:
        bloqueados=("instagram.com","facebook.com","youtube.com","tiktok.com","google.com",
                    "googleusercontent.com","googleapis.com","waze.com","tripadvisor.com",
                    "yelp.com","cnpj.biz","econodata.com.br","solutudo.com.br")
        for i in web:
            u=limpar_url(i["url"])
            if u and not any(d in u.lower() for d in bloqueados):
                x["Site"]=u; x["Tem site?"]="Sim"; break
    if x["Site"]:
        s=analisar_site(x["Site"])
        if not x["Telefone"] and s["telefone"]: x["Telefone"]=formatar_telefone(s["telefone"])
        if not x["Instagram"] and s["instagram"]: x["Instagram"]=s["instagram"]
        if not x["WhatsApp"] and s["whatsapp"]: x["WhatsApp"]=s["whatsapp"]
    x["Tem site?"]="Sim" if x["Site"] else "Não localizado"
    return x

def adicionar_leads(leads):
    if not leads: return 0
    atual=carregar_dados()
    novos=pd.DataFrame(leads)
    for c in COLUNAS:
        if c not in novos.columns: novos[c]=""
    final=pd.concat([atual,novos[COLUNAS]],ignore_index=True).fillna("")
    final=final.drop_duplicates(subset=["Nome","Cidade"],keep="first")
    adicionados=max(0,len(final)-len(atual))
    salvar_dados(final)
    return adicionados

def pesquisar(categoria,cidades,quantidade):
    encontrados=[]
    for cidade in cidades:
        encontrados.extend(buscar_osm(categoria,cidade)[:quantidade])
    unicos={(x["Nome"].lower().strip(),x["Cidade"].lower().strip()):x for x in encontrados}
    encontrados=list(unicos.values())
    if not encontrados: return []
    resultados=[]
    bar=st.progress(0,text="Analisando negócios...")
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures=[ex.submit(enriquecer_lead,x) for x in encontrados]
        for i,f in enumerate(as_completed(futures),1):
            try: resultados.append(f.result())
            except Exception: pass
            bar.progress(i/len(futures),text=f"Analisando {i}/{len(futures)}...")
    bar.empty()
    return resultados

st.sidebar.markdown('<div class="nexxty-logo">NEXXTY</div>',unsafe_allow_html=True)
st.sidebar.markdown('<div class="small-muted">ONE • Lead Intelligence</div>',unsafe_allow_html=True)
st.sidebar.divider()
pagina=st.sidebar.radio("Navegação",["Dashboard","Buscar negócios","Meus leads","Importar","Exportar","Backup","Configurações"])
st.sidebar.divider()
if st.sidebar.button("♻️ Limpar cache",use_container_width=True):
    st.cache_data.clear()
    st.rerun()

df=carregar_dados()

if pagina=="Dashboard":
    st.markdown('<div class="nexxty-logo">NEXXTY ONE</div>',unsafe_allow_html=True)
    st.markdown('<div class="nexxty-subtitle">Central de prospecção de negócios</div>',unsafe_allow_html=True)
    vals=[len(df),len(df[df.Status=="Novo lead"]),len(df[df.Status=="Respondeu"]),len(df[df.Status=="Cliente"]),len(df[df["Tem site?"]=="Sim"])]
    cols=st.columns(5)
    for col,num,label in zip(cols,vals,["Total","Novos leads","Respostas","Clientes","Com site"]):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-number">{num}</div><div class="metric-label">{label}</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    if df.empty: st.info("Seu CRM ainda está vazio. Use 'Buscar negócios' para começar.")
    else:
        st.subheader("Leads recentes")
        st.dataframe(df.tail(20),use_container_width=True,hide_index=True)

elif pagina=="Buscar negócios":
    st.title("Buscar negócios")
    st.markdown('<div class="nexxty-subtitle">Encontre negócios por categoria e cidade.</div>',unsafe_allow_html=True)
    categoria=st.selectbox("Categoria",list(CATEGORIAS.keys()))
    cidades_texto=st.text_input("Cidade(s)","Poços de Caldas",placeholder="Ex.: Poços de Caldas, Pouso Alegre")
    quantidade=st.slider("Máximo por cidade",5,100,25,5)
    if st.button("🔎 INICIAR PROSPECÇÃO",use_container_width=True):
        cidades=[x.strip() for x in cidades_texto.split(",") if x.strip()]
        if not cidades: st.error("Digite pelo menos uma cidade.")
        else:
            with st.spinner("Localizando negócios..."):
                resultados=pesquisar(categoria,cidades,quantidade)
            if not resultados:
                st.error("Nenhum negócio encontrado. Tente outra categoria ou cidade.")
            else:
                adicionados=adicionar_leads(resultados)
                st.success(f"{len(resultados)} negócios encontrados • {adicionados} novos leads salvos.")
                st.dataframe(pd.DataFrame(resultados),use_container_width=True,hide_index=True,
                             column_config={"Site":st.column_config.LinkColumn("Site"),
                                            "Instagram":st.column_config.LinkColumn("Instagram"),
                                            "WhatsApp":st.column_config.LinkColumn("WhatsApp")})

elif pagina=="Meus leads":
    st.title("Meus leads")
    if df.empty: st.info("Nenhum lead cadastrado.")
    else:
        c1,c2=st.columns(2)
        with c1: status=st.selectbox("Status",["Todos","Novo lead","Contato feito","Respondeu","Cliente","Sem interesse"])
        with c2: busca=st.text_input("Pesquisar")
        f=df.copy()
        if status!="Todos": f=f[f.Status==status]
        if busca:
            m=(f.Nome.astype(str).str.contains(busca,case=False,na=False)|
               f.Cidade.astype(str).str.contains(busca,case=False,na=False)|
               f.Telefone.astype(str).str.contains(busca,case=False,na=False))
            f=f[m]
        st.dataframe(f,use_container_width=True,hide_index=True,
                     column_config={"Site":st.column_config.LinkColumn("Site"),
                                    "Instagram":st.column_config.LinkColumn("Instagram"),
                                    "WhatsApp":st.column_config.LinkColumn("WhatsApp")})

elif pagina=="Importar":
    st.title("Importar dados")
    arquivo=st.file_uploader("Envie um CSV",type=["csv"])
    if arquivo:
        try:
            novo=pd.read_csv(arquivo,encoding="utf-8-sig")
            for c in COLUNAS:
                if c not in novo.columns: novo[c]=""
            final=pd.concat([df,novo[COLUNAS]],ignore_index=True).drop_duplicates(["Nome","Cidade"],keep="first")
            salvar_dados(final)
            st.success(f"{len(novo)} registros processados.")
        except Exception as e: st.error(f"Erro: {e}")

elif pagina=="Exportar":
    st.title("Exportar dados")
    csv=df.to_csv(index=False,encoding="utf-8-sig")
    st.download_button("⬇️ Baixar CSV",csv,"nexxty_one_leads.csv","text/csv",use_container_width=True)

elif pagina=="Backup":
    st.title("Backup")
    if st.button("Criar backup",use_container_width=True):
        df.to_csv(BACKUP,index=False,encoding="utf-8-sig")
        st.success(f"Backup criado com {len(df)} leads.")
    if os.path.exists(BACKUP):
        with open(BACKUP,"rb") as f:
            st.download_button("⬇️ Baixar backup",f,file_name=BACKUP,mime="text/csv",use_container_width=True)

else:
    st.title("Configurações")
    st.markdown("""
    ### NEXXTY ONE
    Sistema de prospecção baseado em dados públicos.

    **Fontes:** OpenStreetMap, Overpass, Nominatim e pesquisa pública na web.

    O sistema não garante que todo negócio existente seja encontrado; os resultados dependem dos dados públicos disponíveis.
    """)
