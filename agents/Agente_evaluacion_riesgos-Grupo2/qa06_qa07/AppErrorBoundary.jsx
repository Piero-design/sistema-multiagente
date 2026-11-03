import React, {useEffect,useState} from 'react';
import {AlertTriangle, X, RotateCcw} from 'lucide-react';

// QA-07: los errores de render de React no deben destruir visualmente la página.
export class AppErrorBoundary extends React.Component {
  constructor(props){super(props);this.state={failed:false};}
  static getDerivedStateFromError(){return {failed:true};}
  componentDidCatch(error,info){console.error('[ISO Studio] React render error',error,info);}
  render(){
    if(!this.state.failed) return this.props.children;
    return <div className="iso-error-boundary" role="alert">
      <AlertTriangle size={22}/>
      <div><strong>No se pudo mostrar esta sección.</strong><p>El contenido presentó un problema. Puedes recargar la aplicación sin modificar tus documentos.</p></div>
      <button type="button" onClick={()=>window.location.reload()}><RotateCcw size={15}/> Recargar</button>
    </div>;
  }
}

export function RuntimeErrorNotice(){
  const [visible,setVisible]=useState(false);
  useEffect(()=>{
    let last=0;
    const report=(event)=>{
      const now=Date.now();
      // Evita advertencias repetidas y conserva detalles solamente en la consola.
      if(now-last>2000){last=now;setVisible(true);}
      console.error('[ISO Studio] Error no controlado',event?.reason||event?.error||event?.message||'Error desconocido');
    };
    window.addEventListener('error',report);
    window.addEventListener('unhandledrejection',report);
    return ()=>{window.removeEventListener('error',report);window.removeEventListener('unhandledrejection',report);};
  },[]);
  if(!visible)return null;
  return <div className="iso-runtime-notice" role="alert">
    <AlertTriangle size={17}/><span>Se produjo un error de interfaz. Puedes continuar o recargar la página.</span>
    <button type="button" onClick={()=>setVisible(false)} aria-label="Cerrar aviso"><X size={16}/></button>
  </div>;
}
