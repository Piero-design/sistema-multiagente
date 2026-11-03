import React from 'react';
import Conexion from './Conexion.jsx';
import Referencia from './Referencia.jsx';

export default function Ajustes({ tab, setTab, estado, recargaEstado }) {
  const T = [['conexion', 'Conexión con Claude'], ['acerca', 'Acerca del agente']];
  return (
    <>
      <div className="seg lg" role="tablist" style={{ marginBottom: 20 }}>
        {T.map(([id, l]) => <button key={id} role="tab" aria-pressed={tab === id} onClick={() => setTab(id)}>{l}</button>)}
      </div>
      {tab === 'conexion' ? <Conexion estado={estado} recarga={recargaEstado} /> : <Referencia />}
    </>
  );
}
