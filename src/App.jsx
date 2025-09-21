import React, {useState} from 'react';
import DeviceList from './components/DeviceList';
import { FaHome, FaDatabase, FaFilePdf, FaCog } from 'react-icons/fa';

function Reports(){
  return (
    <div className="card">
      <h2><FaFilePdf/> Reports</h2>
      <table className="table">
        <thead><tr><th>ID</th><th>Device</th><th>Method</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td>mock123</td><td>C:</td><td>NIST</td><td><a href="#">Download</a></td></tr>
        </tbody>
      </table>
    </div>
  )
}

export default function App(){
  const [step,setStep]=useState('devices');
  const [selected,setSelected]=useState([]);
  return (
    <div>
      <header><h1>🔒 Secure Data Wiper</h1></header>
      <main>
        {step==='devices' && <DeviceList onNext={(sel)=>{ setSelected(sel); setStep('options')}} />}
        {step==='options' && <div className="card"><h2><FaCog/> Options</h2><select><option>NIST</option><option>DoD</option></select><div><button onClick={()=>setStep('devices')}>← Back</button><button onClick={()=>setStep('progress')}>Start</button></div></div>}
        {step==='progress' && <div className="card"><h2>Progress</h2><progress value="40" max="100" style={{width:'100%'}}></progress><div><button onClick={()=>setStep('complete')}>Complete</button></div></div>}
        {step==='complete' && <div className="card"><h2>✅ Done</h2><button onClick={()=>setStep('reports')}>View Reports</button></div>}
        {step==='reports' && <Reports/>}
      </main>
    </div>
  )
}
