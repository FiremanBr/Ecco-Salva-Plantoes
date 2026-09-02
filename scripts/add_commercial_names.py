from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

start_marker = '<script id="sprint59-medicamento-fix">'
end_marker = '</script>'

runtime = r'''<script id="sprint60-medicamento-fix">
(function(){
  // SPRINT60: busca local determinística para medicamentos conhecidos.
  // Impede que uma segunda implementação/IA sobrescreva a ficha local.
  // Nomes comerciais aparecem de forma explícita e destacada.
  const COMMERCIAIS = {
    'AAS':['Aspirina'], 'Dipirona':['Novalgina','Anador','Magnopyrol'],
    'Paracetamol':['Tylenol'], 'Captopril':['Capoten'], 'Losartana':['Cozaar'],
    'Prednisona':['Meticorten'], 'Furosemida':['Lasix'],
    'Amiodarona':['Ancoron','Atlansil'], 'Metoprolol':['Lopressor','Seloken'],
    'Sustrate':['Sustrate'], 'Clonidina':['Atensina'], 'Toragesic':['Toragesic'],
    'Adrenalina':['Adren'], 'Atropina':['Atropion'],
    'Cetoprofeno EV':['Profenid'], 'Cetoprofeno IM':['Profenid'],
    'Buscopan C.':['Buscopan Composto'], 'Buscopan S.':['Buscopan'],
    'Metoclopramida':['Plasil'], 'Salbutamol':['Aerolin'], 'Adenosina':['Adenocard'],
    'Ondansetrona':['Vonau','Zofran'], 'Prometazina':['Fenergan'],
    'Dexametasona':['Decadron'], 'Terbutalina':['Bricanyl'],
    'Fenitoína':['Hidantal'], 'Diazepam Inj.':['Valium'], 'Diazepam Comp.':['Valium'],
    'Tramadol':['Tramal'], 'Haloperidol':['Haldol'], 'Biperideno':['Akineton'],
    'Flumazenil':['Lanexat'], 'Clorpromazina':['Amplictil'], 'Morfina':['Dimorf'],
    'Fentanila':['Sublimaze'], 'Deslanosídeo':['Cedilanide'], 'Dopamina':['Revivan'],
    'Narcan':['Narcan']
  };

  const ALIAS = {
    cozaar:'Losartana', novalgina:'Dipirona', anador:'Dipirona', magnopyrol:'Dipirona',
    tylenol:'Paracetamol', capoten:'Captopril', meticorten:'Prednisona', lasix:'Furosemida',
    ancoron:'Amiodarona', atlansil:'Amiodarona', lopressor:'Metoprolol', seloken:'Metoprolol',
    atensina:'Clonidina', adren:'Adrenalina', atropion:'Atropina', profenid:'Cetoprofeno EV',
    'buscopan composto':'Buscopan C.', buscopan:'Buscopan S.', plasil:'Metoclopramida',
    aerolin:'Salbutamol', adenocard:'Adenosina', vonau:'Ondansetrona', zofran:'Ondansetrona',
    fenergan:'Prometazina', decadron:'Dexametasona', bricanyl:'Terbutalina', hidantal:'Fenitoína',
    valium:'Diazepam Inj.', tramal:'Tramadol', haldol:'Haloperidol', akineton:'Biperideno',
    lanexat:'Flumazenil', amplictil:'Clorpromazina', dimorf:'Morfina', sublimaze:'Fentanila',
    cedilanide:'Deslanosídeo', revivan:'Dopamina', aspirina:'AAS'
  };

  function norm(v){
    return String(v||'').trim().normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  }

  function acharLocal(q){
    if(typeof MEDS_DB === 'undefined') return null;
    const nq=norm(q); if(!nq) return null;
    const keys=Object.keys(MEDS_DB);
    const ex=keys.find(k=>norm(k)===nq);
    if(ex) return ex;
    const ali=ALIAS[nq];
    if(ali && MEDS_DB[ali]) return ali;
    const pref=keys.find(k=>{const nk=norm(k); return nk.indexOf(nq)===0 || nq.indexOf(nk)===0;});
    return pref || keys.find(k=>norm(k).indexOf(nq)>=0) || null;
  }

  function comerciais(nome){
    if(COMERCIAIS[nome]) return COMMERCIAIS[nome];
    const base=String(nome).replace(/\s+(EV|IM|Inj\.|Comp\.)$/i,'');
    return COMMERCIAIS[base] || [];
  }

  function destacarComerciais(out,nome){
    const arr=comerciais(nome); if(!arr.length) return;
    const card=out.querySelector('.med-card, .med-card-local, [class*="med-card"]') || out.firstElementChild;
    if(!card || card.querySelector('.sprint60-comerciais')) return;
    const box=document.createElement('div');
    box.className='sprint60-comerciais';
    box.style.cssText='margin:0 0 12px;padding:10px 12px;border:1px solid rgba(70,200,130,.35);border-radius:10px;background:rgba(25,150,90,.10);';
    box.innerHTML='<div style="font-weight:800;font-size:14px;color:#55d68b;margin-bottom:4px">🏷️ NOME COMERCIAL</div><div style="font-weight:800;font-size:17px">'+arr.join(' · ')+'</div>';
    const firstSection=card.querySelector('.med-title, h3, h4, .card-header, [class*="header"]');
    if(firstSection && firstSection.parentElement) firstSection.parentElement.insertBefore(box, firstSection.nextSibling);
    else card.prepend(box);
  }

  function renderLocal(q,out){
    const local=acharLocal(q);
    if(!local || typeof buildCardFromDB!=='function') return false;
    out.innerHTML='<button class="btn-voltar" onclick="limparBusca()">← Voltar</button>'+buildCardFromDB(local);
    destacarComerciais(out,local);
    return true;
  }

  // Guarda a função que existir agora e intercepta futuras atribuições a window.buscarLivre.
  // Assim, scripts posteriores não conseguem substituir a rota local para medicamentos conhecidos.
  let downstream = (typeof window.buscarLivre === 'function') ? window.buscarLivre : null;
  let installed = false;

  function buscarEstavel(){
    const input=document.getElementById('buscaInput');
    const out=document.getElementById('buscaResult');
    const q=input && input.value ? input.value.trim() : '';
    if(!q || !out) return;
    if(renderLocal(q,out)) return;
    if(typeof downstream==='function' && downstream!==buscarEstavel){
      return downstream.apply(this,arguments);
    }
    out.innerHTML='<div class="error-box">⚠️ Pesquisa temporariamente indisponível.</div>';
  }

  try{
    Object.defineProperty(window,'buscarLivre',{
      configurable:true,
      enumerable:true,
      get:function(){ return buscarEstavel; },
      set:function(fn){ if(typeof fn==='function' && fn!==buscarEstavel) downstream=fn; }
    });
    installed=true;
  }catch(e){
    window.buscarLivre=buscarEstavel;
  }

  // Alguns botões podem ter recebido uma referência antiga antes do interceptor.
  // Reforça o comportamento após o DOM estar pronto, sem criar polling contínuo.
  function reforcar(){
    if(installed) return;
    try{ window.buscarLivre=buscarEstavel; }catch(e){}
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',reforcar,{once:true});
  else reforcar();
})();
</script>
'''

if start_marker in s:
    start = s.index(start_marker)
    end = s.index(end_marker, start) + len(end_marker)
    s = s[:start] + runtime.rstrip() + s[end:]
elif '<script id="sprint60-medicamento-fix">' not in s:
    s = s.rstrip() + '\n\n' + runtime.rstrip() + '\n'

p.write_text(s, encoding='utf-8')
print('SPRINT60 aplicada: busca local determinística + interceptor contra sobrescrita + nome comercial destacado.')
