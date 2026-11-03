import React from 'react';

const P = ({ children, size = 18, ...r }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...r}>{children}</svg>
);
export const Shield = p => <P {...p}><path d="M12 3l8 3v6c0 5-3.4 8.6-8 10-4.6-1.4-8-5-8-10V6z" /></P>;
export const Plus = p => <P {...p}><path d="M12 5v14M5 12h14" /></P>;
export const Folder = p => <P {...p}><path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" /></P>;
export const Plug = p => <P {...p}><path d="M9 3v5M15 3v5M7 8h10v3a5 5 0 01-10 0zM12 16v5" /></P>;
export const Info = p => <P {...p}><circle cx="12" cy="12" r="9" /><path d="M12 11v5M12 8h.01" /></P>;
export const Sun = p => <P {...p}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></P>;
export const Moon = p => <P {...p}><path d="M21 13A9 9 0 1111 3a7 7 0 0010 10z" /></P>;
