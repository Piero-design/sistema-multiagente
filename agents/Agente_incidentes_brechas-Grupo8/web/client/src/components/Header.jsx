import React from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { Shield, Sun, Moon } from './Icons.jsx';

export default function Header({ oscuro, setTema, conectado, nExp }) {
  const { pathname } = useLocation();
  const cls = activo => (activo ? 'on' : '');
  return (
    <header className="hdr">
      <div className="hdr-in">
        <Link className="brand" to="/analizar" aria-label="Inicio">
          <span className="logo"><Shield size={20} /></span>
          <span><b>Agente de Incidentes y Brechas</b><small>Datos personales · UNSA · Auditoría de Sistemas</small></span>
        </Link>
        <nav className="tabs">
          <NavLink to="/analizar" className={cls(pathname.startsWith('/analizar') || pathname.startsWith('/analizando'))}>Analizar</NavLink>
          <NavLink to="/autonomia" className={({ isActive }) => cls(isActive)}>Autonomía</NavLink>
          <NavLink to="/contextos" className={({ isActive }) => cls(isActive)}>Contextos</NavLink>
          <NavLink to="/expedientes" className={({ isActive }) => cls(isActive)}>Expedientes{nExp ? <i className="cnt">{nExp}</i> : null}</NavLink>
          <NavLink to="/ajustes" className={({ isActive }) => cls(isActive)}>Ajustes<i className={'st' + (conectado ? '' : ' err')} title={conectado ? 'Conectado' : 'Falta conectar'} /></NavLink>
        </nav>
        <button className="icon-btn" aria-label="Cambiar tema" title="Cambiar tema" onClick={() => setTema(oscuro ? 'light' : 'dark')}>{oscuro ? <Sun /> : <Moon />}</button>
      </div>
    </header>
  );
}
