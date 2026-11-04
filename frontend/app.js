import { h } from './components/ui.js';
import { api } from './services/api.js';
import { ORDER } from './services/agents-config.js';
import { dashboard } from './pages/dashboard.js';
import { agentPage, inventarioPage } from './pages/agent.js';
import { actividad, configuracion } from './pages/system.js';

const app = document.getElementById('app');

async function shell(path) {
  let status = {};
  try { (await api.agents()).forEach((a) => { status[a.route] = a.status; }); } catch { /* sidebar still renders */ }
  const nav = h('nav', { class: 'nav' });
  ORDER.forEach(([to, label], i) => {
    if (i === 1) nav.append(h('h6', {}, 'Agentes'));
    if (to === '/actividad') nav.append(h('h6', {}, 'Sistema'));
    nav.append(h('a', { href: to, class: to === path ? 'on' : '', 'data-link': '' }, label, status[to] ? h('span', { class: `dot ${status[to]}` }) : null));
  });
  const main = h('main');
  app.replaceChildren(h('div', { class: 'shell' }, h('aside', { class: 'side' }, h('div', { class: 'brand' }, h('i'), 'PIMS multiagente'), nav), main));
  return main;
}

async function route() {
  const path = location.pathname.replace(/\/$/, '') || '/';
  const main = await shell(path);
  try {
    const m = path.match(/^\/agentes\/(\w+)$/);
    if (path === '/') await dashboard(main);
    else if (m && m[1] === 'inventario') inventarioPage(main);
    else if (m) await agentPage(main, m[1]);
    else if (path === '/actividad') await actividad(main);
    else if (path === '/configuracion') await configuracion(main);
    else main.append(h('h1', {}, 'Página no encontrada'));
  } catch (e) {
    main.append(h('div', { class: 'alert bad' }, 'Error al cargar: ' + e.message));
  }
}

document.addEventListener('click', (ev) => {
  const a = ev.target.closest('a[data-link]');
  if (a && a.origin === location.origin) { ev.preventDefault(); history.pushState({}, '', a.pathname); route(); }
});
addEventListener('popstate', route);
route();
