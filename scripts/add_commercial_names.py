from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

marker = '// ── BUILD CARD FROM LOCAL DB (sem IA, dados 100% oficiais) ──'
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

p.write_text(s, encoding='utf-8')
print('Patch de nomes comerciais aplicado.')
