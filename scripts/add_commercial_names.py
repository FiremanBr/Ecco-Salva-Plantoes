from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = '// ── BUILD CARD FROM LOCAL DB (sem IA, dados 100% oficiais) ──'

# 1) Nomes comerciais: fonte local apenas como referência de marca; a apresentação/dose
# continua vindo integralmente da MEDS_DB.
if 'const NOMES_COMERCIAIS_PRINCIPAIS' not in s:
    mapa = '''// Principais nomes comerciais no Brasil — referência rápida.
// O nome comercial pode variar conforme fabricante e apresentação.
const NOMES_COMERCIAIS_PRINCIPAIS = {
  'AAS': ['Aspirina'],
  'Dipirona': ['Novalgina', 'Anador', 'Magnopyrol'],
  'Paracetamol': ['Tylenol'],
  'Captopril': ['Capoten'],
  'Losartana': ['Cozaar'],
  'Prednisona': ['Meticorten'],
  'Furosemida': ['Lasix'],
  'Amiodarona': ['Ancoron', 'Atlansil'],
  'Metoprolol': ['Lopressor', 'Seloken'],
  'Sustrate': ['Sustrate'],
  'Clonidina': ['Atensina'],
  'Toragesic': ['Toragesic'],
  'Adrenalina': ['Adren'],
  'Atropina': ['Atropion'],
  'Cetoprofeno EV': ['Profenid'],
  'Cetoprofeno IM': ['Profenid'],
  'Buscopan C.': ['Buscopan Composto'],
  'Buscopan S.': ['Buscopan'],
  'Metoclopramida': ['Plasil'],
  'Salbutamol': ['Aerolin'],
  'Adenosina': ['Adenocard'],
  'Ondansetrona': ['Vonau', 'Zofran'],
  'Prometazina': ['Fenergan'],
  'Dexametasona': ['Decadron'],
  'Terbutalina': ['Bricanyl'],
  'Fenitoína': ['Hidantal'],
  'Diazepam Inj.': ['Valium'],
  'Diazepam Comp.': ['Valium'],
  'Tramadol': ['Tramal'],
  'Haloperidol': ['Haldol'],
  'Biperideno': ['Akineton'],
  'Flumazenil': ['Lanexat'],
  'Clorpromazina': ['Amplictil'],
  'Morfina': ['Dimorf'],
  'Fentanila': ['Sublimaze'],
  'Deslanosídeo': ['Cedilanide'],
  'Dopamina': ['Revivan'],
  'Narcan': ['Narcan'],
};

function nomesComerciaisDoMedicamento(nome) {
  if (NOMES_COMERCIAIS_PRINCIPAIS[nome]) return NOMES_COMERCIAIS_PRINCIPAIS[nome];
  const base = nome.replace(/\\s+(EV|IM|Inj\\.|Comp\\.)$/i, '');
  return NOMES_COMERCIAIS_PRINCIPAIS[base] || [];
}

'''
    if marker not in s:
        raise SystemExit('Marcador do buildCardFromDB não encontrado')
    s = s.replace(marker, mapa + marker, 1)

# 2) Coloca o nome comercial dentro da ficha local.
if 'const nomesComerciais = nomesComerciaisDoMedicamento(nome);' not in s:
    old = '''  const m = MEDS_DB[nome];
  if (!m) return '';
  const interacoesHtml ='''
    new = '''  const m = MEDS_DB[nome];
  if (!m) return '';
  const nomesComerciais = nomesComerciaisDoMedicamento(nome);
  const comerciaisHtml = nomesComerciais.length
    ? `<div style="margin-top:6px"><div class="row-lbl">🏷️ Principais nomes comerciais</div><div class="row-val">${nomesComerciais.join(' · ')}</div></div>`
    : '';
  const interacoesHtml ='''
    if old not in s:
        raise SystemExit('Cabeçalho de buildCardFromDB não encontrado')
    s = s.replace(old, new, 1)

if '${comerciaisHtml}' not in s:
    old2 = '''        <div><div class="row-lbl">📦 Apresentação</div><div class="row-val">${m.apresentacao}${m.doseMax24h ? '<br><span style="color:var(--text);font-size:11px">⏱️ ' + m.doseMax24h + '</span>' : ''}</div></div>'''
    new2 = '''        <div><div class="row-lbl">📦 Apresentação</div><div class="row-val">${m.apresentacao}${m.doseMax24h ? '<br><span style="color:var(--text);font-size:11px">⏱️ ' + m.doseMax24h + '</span>' : ''}</div></div>
        ${comerciaisHtml}'''
    if old2 not in s:
        raise SystemExit('Linha de apresentação não encontrada')
    s = s.replace(old2, new2, 1)

# 3) A busca livre não pode mandar para a IA uma consulta que já existe na MEDS_DB.
# O print mostrado no teste ("Xmg/mL — ampola XmL") é justamente o fallback genérico
# da resposta externa. Forçamos primeiro a ficha local completa para nomes conhecidos.
runtime_marker = '<script id="sprint59-medicamento-fix">'
if runtime_marker not in s:
    runtime = r'''<script id="sprint59-medicamento-fix">
(function(){
  function norm(v){
    return String(v||'').trim().normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  }
  function acharLocalSeguro(q){
    if(typeof MEDS_DB === 'undefined') return null;
    var nq=norm(q);
    if(!nq) return null;
    var keys=Object.keys(MEDS_DB);
    var ex=keys.find(function(k){return norm(k)===nq;});
    if(ex) return ex;
    var alias={
      'losartana':'Losartana','cozaar':'Losartana',
      'dipirona':'Dipirona','novalgina':'Dipirona','anador':'Dipirona',
      'paracetamol':'Paracetamol','tylenol':'Paracetamol',
      'captopril':'Captopril','capoten':'Captopril',
      'prednisona':'Prednisona','meticorten':'Prednisona',
      'furosemida':'Furosemida','lasix':'Furosemida',
      'amiodarona':'Amiodarona','ancoron':'Amiodarona','atlansil':'Amiodarona',
      'metoprolol':'Metoprolol','lopressor':'Metoprolol','seloken':'Metoprolol',
      'adrenalina':'Adrenalina','adren':'Adrenalina',
      'atropina':'Atropina','atropion':'Atropina',
      'metoclopramida':'Metoclopramida','plasil':'Metoclopramida',
      'salbutamol':'Salbutamol','aerolin':'Salbutamol',
      'adenosina':'Adenosina','adenocard':'Adenosina',
      'ondansetrona':'Ondansetrona','vonau':'Ondansetrona','zofran':'Ondansetrona',
      'prometazina':'Prometazina','fenergan':'Prometazina',
      'dexametasona':'Dexametasona','decadron':'Dexametasona',
      'terbutalina':'Terbutalina','bricanyl':'Terbutalina',
      'fenitoina':'Fenitoína','hidantal':'Fenitoína',
      'tramadol':'Tramadol','tramal':'Tramadol',
      'haloperidol':'Haloperidol','haldol':'Haloperidol',
      'biperideno':'Biperideno','akineton':'Biperideno',
      'flumazenil':'Flumazenil','lanexat':'Flumazenil',
      'clorpromazina':'Clorpromazina','amplictil':'Clorpromazina',
      'morfina':'Morfina','dimorf':'Morfina',
      'fentanila':'Fentanila','sublimaze':'Fentanila',
      'deslanosideo':'Deslanosídeo','cedilanide':'Deslanosídeo',
      'dopamina':'Dopamina','revivan':'Dopamina'
    };
    if(alias[nq] && MEDS_DB[alias[nq]]) return alias[nq];
    var pref=keys.find(function(k){var nk=norm(k);return nk.indexOf(nq)===0 || nq.indexOf(nk)===0;});
    if(pref) return pref;
    return keys.find(function(k){return norm(k).indexOf(nq)>=0;}) || null;
  }
  var originalBuscar = window.buscarLivre;
  window.buscarLivre = async function(){
    var input=document.getElementById('buscaInput');
    var out=document.getElementById('buscaResult');
    var q=input && input.value ? input.value.trim() : '';
    if(!q || !out) return;
    var local=acharLocalSeguro(q);
    if(local && typeof buildCardFromDB==='function'){
      out.innerHTML='<button class="btn-voltar" onclick="limparBusca()">← Voltar</button>'+buildCardFromDB(local);
      return;
    }
    if(typeof originalBuscar==='function') return originalBuscar.apply(this,arguments);
    out.innerHTML='<div class="error-box">⚠️ Pesquisa temporariamente indisponível.</div>';
  };
})();
</script>
'''
    # Colocar no final evita que os patches antigos redefinam a função depois deste ajuste.
    s += '\n' + runtime

p.write_text(s, encoding='utf-8')
print('Correção de ficha completa + nomes comerciais + prioridade da MEDS_DB aplicada.')
