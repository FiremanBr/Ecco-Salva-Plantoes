from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = '<script id="sprint59-medicamento-fix">'
if marker in s:
    print('Correção de medicamentos já presente; nada a fazer.')
    raise SystemExit(0)

runtime = r'''<script id="sprint59-medicamento-fix">
(function(){
  // SPRINT59: MEDS_DB tem prioridade sobre IA para medicamentos conhecidos.
  // Também exibe nomes comerciais como referência, sem alterar a ficha clínica local.
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

  function norm(v){
    return String(v||'').trim().normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  }

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
    cedilanide:'Deslanosídeo', revivan:'Dopamina'
  };

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

  function adicionarComerciais(out,nome){
    const arr=comerciais(nome); if(!arr.length) return;
    const card=out.querySelector('.med-card, .med-card-local, [class*="med-card"]') || out.firstElementChild;
    if(!card || card.querySelector('.sprint59-comerciais')) return;
    const box=document.createElement('div');
    box.className='sprint59-comerciais';
    box.style.cssText='margin:8px 0;padding:8px 10px;border-radius:8px;background:var(--surface-2,#f4f4f5);';
    box.innerHTML='<div class="row-lbl">🏷️ Principais nomes comerciais</div><div class="row-val">'+arr.join(' · ')+'</div>';
    card.prepend(box);
  }

  const originalBuscar = window.buscarLivre;
  window.buscarLivre = async function(){
    const input=document.getElementById('buscaInput');
    const out=document.getElementById('buscaResult');
    const q=input && input.value ? input.value.trim() : '';
    if(!q || !out) return;
    const local=acharLocal(q);
    if(local && typeof buildCardFromDB==='function'){
      out.innerHTML='<button class="btn-voltar" onclick="limparBusca()">← Voltar</button>'+buildCardFromDB(local);
      adicionarComerciais(out,local);
      return;
    }
    if(typeof originalBuscar==='function') return originalBuscar.apply(this,arguments);
    out.innerHTML='<div class="error-box">⚠️ Pesquisa temporariamente indisponível.</div>';
  };
})();
</script>
'''

s = s.rstrip() + '\n\n' + runtime
p.write_text(s, encoding='utf-8')
print('Correção SPRINT59 aplicada: MEDS_DB primeiro, aliases e nomes comerciais por runtime.')
