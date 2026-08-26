'use client';

import { useEffect, useState } from 'react';

const CODES = {
  P0171: { description: 'System Too Lean (Bank 1)', severity: 'Medium', cost: '£50-£350', diy: true, symptoms: ['rough idle','check engine light','poor fuel economy','stalling'], causes: ['vacuum leak','dirty MAF sensor','weak fuel pump'], repairs: ['Inspect vacuum hoses','Clean or replace MAF sensor','Check fuel pressure'] },
  P0172: { description: 'System Too Rich (Bank 1)', severity: 'Medium', cost: '£40-£300', diy: true, symptoms: ['check engine light','poor fuel economy','black smoke'], causes: ['dirty air filter','failing O2 sensor','fuel pressure regulator'], repairs: ['Replace air filter','Test O2 sensor','Check fuel pressure regulator'] },
  P0300: { description: 'Random/Multiple Cylinder Misfire', severity: 'High', cost: '£80-£600', diy: true, symptoms: ['misfire','rough idle','check engine light','loss of power','vibration'], causes: ['worn spark plugs','bad ignition coils','low compression','vacuum leak'], repairs: ['Replace spark plugs','Test ignition coils','Compression test'] },
  P0301: { description: 'Cylinder 1 Misfire', severity: 'High', cost: '£50-£400', diy: true, symptoms: ['misfire','rough idle','check engine light','vibration'], causes: ['worn spark plug cylinder 1','ignition coil failure','low compression'], repairs: ['Replace spark plug cylinder 1','Test ignition coil','Compression test'] },
  P0302: { description: 'Cylinder 2 Misfire', severity: 'High', cost: '£50-£400', diy: true, symptoms: ['misfire','rough idle','check engine light','vibration'], causes: ['worn plug cylinder 2','ignition coil failure','low compression'], repairs: ['Replace spark plug cylinder 2','Test ignition coil','Compression test'] },
  P0303: { description: 'Cylinder 3 Misfire', severity: 'High', cost: '£50-£400', diy: true, symptoms: ['misfire','rough idle','check engine light','vibration'], causes: ['worn plug cylinder 3','ignition coil failure','low compression'], repairs: ['Replace spark plug cylinder 3','Test ignition coil','Compression test'] },
  P0304: { description: 'Cylinder 4 Misfire', severity: 'High', cost: '£50-£400', diy: true, symptoms: ['misfire','rough idle','check engine light','vibration'], causes: ['worn plug cylinder 4','ignition coil failure','low compression'], repairs: ['Replace spark plug cylinder 4','Test ignition coil','Compression test'] },
  P0420: { description: 'Catalyst Efficiency Below Threshold (Bank 1)', severity: 'High', cost: '£200-£1,200', diy: false, symptoms: ['check engine light','failed emissions','sulfur smell'], causes: ['failed catalytic converter','bad O2 sensor','exhaust leak'], repairs: ['Replace catalytic converter','Test/replace O2 sensors','Check exhaust leaks'] },
  P0430: { description: 'Catalyst Efficiency Below Threshold (Bank 2)', severity: 'High', cost: '£200-£1,200', diy: false, symptoms: ['check engine light','failed emissions'], causes: ['failed converter bank 2','bad O2 sensor bank 2','exhaust leak'], repairs: ['Replace catalytic converter bank 2','Test/replace O2 sensors'] },
  P0128: { description: 'Coolant Thermostat Below Regulating Temp', severity: 'Medium', cost: '£80-£350', diy: true, symptoms: ['engine running cold','poor heater','check engine light'], causes: ['stuck open thermostat','low coolant','failed temp sensor'], repairs: ['Replace thermostat','Check coolant level','Test temp sensor'] },
  P0135: { description: 'O2 Sensor Heater Circuit (Bank 1 Sensor 1)', severity: 'Medium', cost: '£60-£250', diy: true, symptoms: ['check engine light','poor cold idle'], causes: ['failed O2 heater','wiring damage','blown fuse'], repairs: ['Replace O2 sensor','Check wiring/fuse','Test ECM driver'] },
  P0141: { description: 'O2 Sensor Heater Circuit (Bank 1 Sensor 2)', severity: 'Medium', cost: '£60-£250', diy: true, symptoms: ['check engine light','catalyst damage risk'], causes: ['failed rear O2 heater','wiring damage','blown fuse'], repairs: ['Replace downstream O2 sensor','Check wiring','Test fuses'] },
  P0340: { description: 'Camshaft Position Sensor Circuit', severity: 'High', cost: '£70-£400', diy: true, symptoms: ['check engine light','hard start','stalling','poor performance','no start'], causes: ['failed CMP sensor','wiring damage','timing belt/chain stretch','oil contamination'], repairs: ['Replace camshaft position sensor','Check wiring harness','Inspect timing belt/chain'] },
  P0351: { description: 'Ignition Coil A Circuit Malfunction', severity: 'High', cost: '£60-£350', diy: true, symptoms: ['misfire','check engine light','hard start','rough idle','backfire'], causes: ['failed ignition coil','wiring damage','failing ICM'], repairs: ['Replace ignition coil','Test wiring/connectors','Check ICM'] },
  P0401: { description: 'EGR Flow Insufficient', severity: 'Medium', cost: '£80-£450', diy: true, symptoms: ['check engine light','rough idle','pinging','poor fuel economy'], causes: ['clogged EGR','faulty EGR solenoid','carbon buildup','vacuum leak'], repairs: ['Clean/replace EGR valve','Test solenoid','Clean intake manifold'] },
  P0505: { description: 'Idle Air Control System Malfunction', severity: 'Medium', cost: '£50-£300', diy: true, symptoms: ['rough idle','stalling','high idle','check engine light'], causes: ['dirty IAC valve','failing throttle body','vacuum leak'], repairs: ['Clean IAC valve','Clean throttle body','Check vacuum leaks'] },
  P0562: { description: 'System Voltage Low', severity: 'High', cost: '£80-£500', diy: true, symptoms: ['check engine light','dim lights','slow cranking','battery warning light'], causes: ['failing alternator','bad battery','corroded terminals','voltage regulator failure'], repairs: ['Test alternator output','Load test battery','Clean terminals'] },
  P0700: { description: 'Transmission Control System Malfunction', severity: 'High', cost: '£100-£1,500', diy: false, symptoms: ['check engine light','harsh shifting','slipping gears','limp mode'], causes: ['faulty TCM','wiring/connector issue','low transmission fluid','solenoid failure'], repairs: ['Scan for TCM-specific codes','Check transmission fluid','Test solenoids'] },
  C0035: { description: 'Left Front Wheel Speed Sensor Circuit', severity: 'Medium', cost: '£60-£300', diy: true, symptoms: ['ABS light','ESC light','speedometer inaccurate'], causes: ['failed wheel speed sensor','damaged sensor ring','wiring damage'], repairs: ['Replace wheel speed sensor','Inspect sensor ring','Check wiring harness'] },
  B0001: { description: 'Driver Frontal Stage Squib Circuit Open', severity: 'High', cost: '£150-£800', diy: false, symptoms: ['airbag warning light','SRS light'], causes: ['failed airbag squib','clockspring failure','wiring damage'], repairs: ['Replace squib/clockspring','Check wiring','Scan airbag module'] },
  U0100: { description: 'Lost Communication With ECM/PCM A', severity: 'High', cost: '£100-£1,000', diy: false, symptoms: ['check engine light','multiple warning lights','no-start','limp mode'], causes: ['CAN bus wiring damage','failed ECM/PCM','ground fault'], repairs: ['Inspect CAN bus wiring','Check grounds','Test ECM/PCM communication'] },
  P0010: { description: "'A' Camshaft Position Actuator Circuit (Bank 1)", severity: 'High', cost: '£100-£600', diy: false, symptoms: ['rough idle','check engine light','poor fuel economy','hard start'], causes: ['failed cam actuator solenoid','low oil pressure','timing chain stretch'], repairs: ['Replace cam actuator solenoid','Check oil pressure','Inspect timing chain'] },
  P0016: { description: 'CKP - CMP Correlation (Bank 1)', severity: 'High', cost: '£150-£900', diy: false, symptoms: ['check engine light','hard start','stalling','rough idle','no start'], causes: ['timing belt/chain jumped','failed CKP sensor','failed CMP sensor','low oil pressure'], repairs: ['Check valve timing','Replace CKP/CMP sensors','Verify oil pressure'] },
  P0120: { description: 'Throttle Position Sensor/Switch A Circuit', severity: 'Medium', cost: '£50-£250', diy: true, symptoms: ['check engine light','poor throttle response','rough idle','stalling'], causes: ['failed TPS','wiring damage','throttle body failure'], repairs: ['Replace TPS','Check throttle body wiring','Throttle body relearn'] },
  P0220: { description: 'Throttle/Pedal Position Sensor B Circuit', severity: 'Medium', cost: '£60-£300', diy: true, symptoms: ['poor throttle response','check engine light','limp mode'], causes: ['failed pedal position sensor','wiring damage','throttle body failure'], repairs: ['Replace pedal position sensor','Check wiring','Throttle body relearn'] },
  P0299: { description: 'Turbocharger Underboost', severity: 'High', cost: '£100-£1,000', diy: false, symptoms: ['loss of power','check engine light','poor acceleration','turbo whine'], causes: ['worn turbo','wastegate stuck','boost leak','clogged intake'], repairs: ['Inspect turbo/wastegate','Pressure test for boost leaks','Check intercooler'] },
  P0335: { description: 'Crankshaft Position Sensor Circuit', severity: 'High', cost: '£70-£400', diy: false, symptoms: ['no start','hard start','stalling','check engine light','loss of power'], causes: ['failed CKP sensor','wiring damage','missing reluctor wheel teeth'], repairs: ['Replace crankshaft position sensor','Check wiring harness','Inspect reluctor wheel'] },
  P0400: { description: 'EGR Flow Malfunction', severity: 'Medium', cost: '£80-£450', diy: true, symptoms: ['check engine light','rough idle','pinging','poor fuel economy'], causes: ['clogged EGR valve','faulty EGR solenoid','carbon buildup','vacuum leak'], repairs: ['Clean/replace EGR valve','Test EGR solenoid','Clean intake carbon'] },
  P0440: { description: 'EVAP System Malfunction', severity: 'Low', cost: '£30-£250', diy: true, symptoms: ['check engine light','fuel smell','emissions fail'], causes: ['leaking EVAP hose','failed purge valve','failed vent valve','loose gas cap'], repairs: ['Inspect EVAP hoses','Replace purge/vent valves','Tighten gas cap'] },
  P0442: { description: 'EVAP System Small Leak', severity: 'Low', cost: '£30-£200', diy: true, symptoms: ['check engine light','fuel smell'], causes: ['small EVAP leak','loose gas cap','cracked hose'], repairs: ['Tighten/replace gas cap','Inspect hoses','Smoke test EVAP'] },
  P0506: { description: 'Idle Speed Lower Than Expected', severity: 'Medium', cost: '£50-£250', diy: true, symptoms: ['low idle','stalling','rough idle'], causes: ['dirty IAC valve','vacuum leak','throttle body issue'], repairs: ['Clean IAC valve','Check for vacuum leaks','Throttle body relearn'] },
  P0507: { description: 'Idle Speed Higher Than Expected', severity: 'Medium', cost: '£50-£250', diy: true, symptoms: ['high idle','rough idle','check engine light'], causes: ['IAC valve stuck open','vacuum leak','throttle body sticking'], repairs: ['Clean/replace IAC valve','Check for vacuum leaks','Clean throttle body'] },
  P0520: { description: 'Engine Oil Pressure Sensor Circuit', severity: 'High', cost: '£50-£250', diy: true, symptoms: ['oil pressure warning','check engine light','low oil pressure reading'], causes: ['failed oil pressure sensor','wiring damage','low oil level'], repairs: ['Replace oil pressure sensor','Check oil level/condition'] },
};

const ALL_SYMPTOMS = Array.from(new Set(Object.values(CODES).flatMap(c => c.symptoms))).sort();

const MAINTENANCE = [
  { item: 'Oil & Filter', interval: 'Every 12 months / 12,000 miles', cost: '£60-£120', note: 'DIY if under vehicle easily' },
  { item: 'Air Filter', interval: 'Every 24 months / 24,000 miles', cost: '£20-£50', note: 'DIY' },
  { item: 'Cabin Filter', interval: 'Every 12 months', cost: '£25-£60', note: 'DIY' },
  { item: 'Brake Fluid', interval: 'Every 24 months', cost: '£40-£80', note: 'DIY bleed possible' },
  { item: 'Coolant', interval: 'Every 60 months', cost: '£60-£120', note: 'Garage' },
  { item: 'Spark Plugs', interval: 'Every 30,000-60,000 miles', cost: '£40-£160', note: 'DIY for most' },
  { item: 'Timing Belt', interval: 'Every 60,000-100,000 miles', cost: '£300-£800', note: 'Garage' },
  { item: 'Tyres', interval: 'Every 5-10 years or 3mm tread', cost: '£60-£120/tyre', note: 'Garage fit' },
  { item: 'Brake Pads', interval: 'Every 30,000-70,000 miles', cost: '£80-£250', note: 'DIY possible' },
  { item: 'Brake Discs', interval: 'As needed with pads', cost: '£150-£400', note: 'Garage' },
  { item: 'Battery', interval: 'Every 3-5 years', cost: '£100-£220', note: 'DIY' },
  { item: 'Wiper Blades', interval: 'Every 12 months', cost: '£15-£40', note: 'DIY' },
];

function loadJSON(key, fallback) {
  if (typeof window === 'undefined') return fallback;
  try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; } catch { return fallback; }
}
function saveJSON(key, value) { if (typeof window !== 'undefined') localStorage.setItem(key, JSON.stringify(value)); }

export default function App() {
  const [tab, setTab] = useState('diagnose');
  const [vehicle, setVehicle] = useState({ make: '', model: '', year: '', engine: '', mileage: '', vin: '' });
  const [symptoms, setSymptoms] = useState([]);
  const [customSymptom, setCustomSymptom] = useState('');
  const [results, setResults] = useState([]);
  const [codeSearch, setCodeSearch] = useState('');
  const [history, setHistory] = useState([]);
  const [service, setService] = useState([]);
  const [motTax, setMotTax] = useState([]);
  const [svcForm, setSvcForm] = useState({ date: '', mileage: '', item: '', garage: '', cost: '' });
  const [motForm, setMotForm] = useState({ type: 'MOT', expiry: '' });

  useEffect(() => {
    const savedVehicle = loadJSON('cd_vehicle', vehicle);
    setVehicle(savedVehicle);
    const savedHistory = loadJSON('cd_history', []);
    setHistory(savedHistory);
    const savedService = loadJSON('cd_service', []);
    setService(savedService);
    const savedMotTax = loadJSON('cd_mot_tax', []);
    setMotTax(savedMotTax);
  }, []);

  useEffect(() => { saveJSON('cd_vehicle', vehicle); }, [vehicle]);
  useEffect(() => { saveJSON('cd_history', history); }, [history]);
  useEffect(() => { saveJSON('cd_service', service); }, [service]);
  useEffect(() => { saveJSON('cd_mot_tax', motTax); }, [motTax]);

  function diagnose() {
    const text = (customSymptom || symptoms.join(' ')).trim().toLowerCase();
    if (!text) { alert('Pick symptoms or type a description'); return; }
    const words = text.split(/[^a-z]+/).filter(w => w.length > 2);
    const scored = Object.entries(CODES).map(([code, data]) => {
      let score = 0;
      for (const s of data.symptoms) if (text.includes(s) || s.includes(text)) score += 3;
      for (const word of words) for (const s of data.symptoms) if (s.includes(word)) score += 1;
      return { code, ...data, score };
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score || (a.diy ? 0 : 1) - (b.diy ? 0 : 1) || a.code.localeCompare(b.code));
    const entry = { timestamp: new Date().toISOString(), vehicle: formatVehicle(), symptom: customSymptom || symptoms.join(', '), result: scored.map(x => x.code).join(',') || 'no_match' };
    setHistory(h => [entry, ...h]);
    setResults(scored);
  }

  function formatVehicle() {
    return [vehicle.year, vehicle.make, vehicle.model, vehicle.engine, vehicle.mileage ? `${vehicle.mileage} miles` : ''].filter(Boolean).join(' | ');
  }

  function addService() {
    if (!svcForm.date || !svcForm.item) { alert('Date and item are required'); return; }
    setService(s => [{ id: Date.now(), ...svcForm }, ...s]);
    setSvcForm({ date: '', mileage: '', item: '', garage: '', cost: '' });
  }

  function addMotTax() {
    if (!motForm.expiry) { alert('Expiry date is required'); return; }
    setMotTax(m => [{ id: Date.now(), ...motForm }, ...m]);
    setMotForm({ ...motForm, expiry: '' });
  }

  function exportReport() {
    if (!results.length) { alert('Run a diagnosis first'); return; }
    const text = results.map(r => `${r.code}: ${r.description}\nSeverity: ${r.severity}\nCost: ${r.cost}\nType: ${r.diy ? 'DIY possible' : 'Garage recommended'}\nSymptoms: ${r.symptoms.join(', ')}\nCauses: ${r.causes.join(', ')}\nRepairs: ${r.repairs.join('; ')}\n`).join('\n');
    const blob = new Blob([`Vehicle: ${formatVehicle()}\n\n${text}`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'diagnosis_report.txt'; a.click(); URL.revokeObjectURL(url);
  }

  const filteredCodes = Object.entries(CODES).filter(([code, data]) => !codeSearch || code.toLowerCase().includes(codeSearch.toLowerCase()) || data.description.toLowerCase().includes(codeSearch.toLowerCase()));

  return (
    <div style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif', background: '#0f172a', color: '#e2e8f0', minHeight: '100vh' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 28 }}>Car Diagnosis Assistant</h1>
            <p style={{ margin: 4, opacity: 0.8 }}>Web version — data saved in your browser</p>
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {['diagnose','codes','service','mot','maintenance','history'].map(t => (
              <button key={t} onClick={() => setTab(t)} style={{ background: tab===t ? '#38bdf8' : '#1e293b', color: tab===t ? '#0f172a' : '#e2e8f0', border: '1px solid #334155', padding: '8px 12px', borderRadius: 8, cursor: 'pointer', textTransform: 'capitalize' }}>{t}</button>
            ))}
          </div>
        </div>

        {tab === 'diagnose' && (
          <div style={{ background: '#111827', border: '1px solid #334155', borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 12 }}>
              {['make','model','year','engine','mileage','vin'].map(field => (
                <div key={field}>
                  <label style={{ fontSize: 12, opacity: 0.8, textTransform: 'capitalize' }}>{field}</label>
                  <input value={vehicle[field]} onChange={e => setVehicle({ ...vehicle, [field]: e.target.value })} style={{ width: '100%', background: '#0f172a', color: '#e2e8f0', border: '1px solid #334155', borderRadius: 6, padding: 8, marginTop: 4 }} />
                </div>
              ))}
            </div>
            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 12, opacity: 0.8 }}>Symptoms</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
                {ALL_SYMPTOMS.map(sym => (
                  <button key={sym} onClick={() => setSymptoms(prev => prev.includes(sym) ? prev.filter(x => x !== sym) : [...prev, sym])} style={{ background: symptoms.includes(sym) ? '#38bdf8' : '#1e293b', color: symptoms.includes(sym) ? '#0f172a' : '#e2e8f0', border: '1px solid #334155', padding: '6px 10px', borderRadius: 999, cursor: 'pointer' }}>{sym}</button>
                ))}
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <input value={customSymptom} onChange={e => setCustomSymptom(e.target.value)} placeholder="Or describe it yourself..." style={{ flex: 1, background: '#0f172a', color: '#e2e8f0', border: '1px solid #334155', borderRadius: 6, padding: 10 }} />
              <button onClick={diagnose} style={{ background: '#38bdf8', color: '#0f172a', border: 'none', padding: '10px 16px', borderRadius: 6, cursor: 'pointer', fontWeight: 600 }}>Diagnose</button>
            </div>
            {!!results.length && (
              <div style={{ marginTop: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h2 style={{ margin: '12px 0 8px', fontSize: 18 }}>Possible causes — start from the top</h2>
                  <button onClick={exportReport} style={{ background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155', padding: '8px 12px', borderRadius: 6, cursor: 'pointer' }}>Export Report</button>
                </div>
                {results.map(r => (
                  <div key={r.code} style={{ background: '#0b1220', border: '1px solid #223', borderRadius: 10, padding: 12, marginBottom: 10 }}>
                    <div style={{ fontWeight: 700, color: '#7dd3fc' }}>{r.code}: {r.description}</div>
                    <div style={{ opacity: 0.9 }}>Severity: {r.severity} | Cost: {r.cost} | {r.diy ? 'DIY possible' : 'Garage recommended'}</div>
                    <div style={{ opacity: 0.85 }}>Symptoms: {r.symptoms.join(', ')}</div>
                    <div style={{ opacity: 0.85 }}>Causes: {r.causes.join(', ')}</div>
                    <div style={{ opacity: 0.85 }}>Repairs: {r.repairs.join('; ')}</div>
                    <div style={{ opacity: 0.9, marginTop: 6 }}>Next step: {r.repairs[0]}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === 'codes' && (
          <div style={{ background: '#111827', border: '1px solid #334155', borderRadius: 12, padding: 16 }}>
            <input value={codeSearch} onChange={e => setCodeSearch(e.target.value)} placeholder="Search codes..." style={{ width: '100%', background: '#0f172a', color: '#e2e8f0', border: '1px solid #334155', borderRadius: 6, padding: 10, marginBottom: 12 }} />
            <div style={{ overflow: 'auto' }}>
              {filteredCodes.map(([code, data]) => (
                <div key={code} style={{ background: '#0b1220', border: '1px solid #223', borderRadius: 10, padding: 10, marginBottom: 8 }}>
                  <div style={{ fontWeight: 700, color: '#7dd3fc' }}>{code}: {data.description}</div>
                  <div style={{ opacity: 0.85 }}>Severity: {data.severity} | Cost: {data.cost} | {data.diy ? 'DIY possible' : 'Garage recommended'}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'service' && (
          <div style={{ background: '#111827', border: '1px solid #334155', borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10, marginBottom: 12 }}>
              {['date','mileage','item','garage','cost'].map(field => (
                <input key={field} value={svcForm[field] || ''} onChange={e => setSvcForm({ ...svcForm, [field]: e.target.value })} placeholder={field} maxLength={120} style={{ background: '#0f172a', color: '#e2e8f0', border: '1px solid #334155', borderRadius: 6, padding: 8 }} />
              ))}
              <button onClick={addService} style={{ background: '#38bdf8', color: '#0f172a', border: 'none', padding: 10, borderRadius: 6, cursor: 'pointer', fontWeight: 600 }}>Save</button>
            </div>
            {service.map(s => (
              <div key={s.id} style={{ background: '#0b1220', border: '1px solid #223', borderRadius: 10, padding: 10, marginBottom: 8 }}>
                <div style={{ fontWeight: 700 }}>{s.item}</div>
                <div style={{ opacity: 0.85 }}>{s.date} | {s.mileage} miles | {s.garage} | {s.cost}</div>
              </div>
            ))}
          </div>
        )}

        {tab === 'mot' && (
          <div style={{ background: '#111827', border: '1px solid #334155', borderRadius: 12, padding: 16 }}>
            <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
              <select value={motForm.type} onChange={e => setMotForm({ ...motForm, type: e.target.value })} style={{ background: '#0f172a', color: '#e2e8f0', border: '1px solid #334155', borderRadius: 6, padding: 8 }}>
                <option>MOT</option>
                <option>Tax</option>
              </select>
              <input value={motForm.expiry} onChange={e => setMotForm({ ...motForm, expiry: e.target.value })} placeholder="YYYY-MM-DD" style={{ background: '#0f172a', color: '#e2e8f0', border: '1px solid #334155', borderRadius: 6, padding: 8 }} />
              <button onClick={addMotTax} style={{ background: '#38bdf8', color: '#0f172a', border: 'none', padding: 10, borderRadius: 6, cursor: 'pointer', fontWeight: 600 }}>Save</button>
            </div>
            {motTax.map(m => {
              const today = new Date().toISOString().slice(0,10);
              const status = m.expiry < today ? 'EXPIRED' : (new Date(m.expiry) - new Date(today))/86400000 <= 30 ? 'DUE SOON' : 'OK';
              return (
                <div key={m.id} style={{ background: '#0b1220', border: '1px solid #223', borderRadius: 10, padding: 10, marginBottom: 8 }}>
                  <div style={{ fontWeight: 700 }}>{m.type}</div>
                  <div style={{ opacity: 0.85 }}>{m.expiry} | {status}</div>
                </div>
              );
            })}
          </div>
        )}

        {tab === 'maintenance' && (
          <div style={{ background: '#111827', border: '1px solid #334155', borderRadius: 12, padding: 16 }}>
            {MAINTENANCE.map(m => (
              <div key={m.item} style={{ background: '#0b1220', border: '1px solid #223', borderRadius: 10, padding: 10, marginBottom: 8 }}>
                <div style={{ fontWeight: 700 }}>{m.item}</div>
                <div style={{ opacity: 0.85 }}>{m.interval} | {m.cost} | {m.note}</div>
              </div>
            ))}
          </div>
        )}

        {tab === 'history' && (
          <div style={{ background: '#111827', border: '1px solid #334155', borderRadius: 12, padding: 16 }}>
            {history.map((h, idx) => (
              <div key={idx} style={{ background: '#0b1220', border: '1px solid #223', borderRadius: 10, padding: 10, marginBottom: 8 }}>
                <div style={{ opacity: 0.7 }}>{new Date(h.timestamp).toLocaleString()}</div>
                <div style={{ opacity: 0.9 }}>{`${h.vehicle || 'Unknown vehicle'} | ${h.symptom} -> ${h.result}`}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
