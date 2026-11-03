# 03 · Aviso al Centro Nacional de Seguridad Digital (CNSD) — BORRADOR (no enviado)

> Base: art. 34.5 del D.S. 016-2024-JUS y D.U. 007-2020 (Registro Nacional de Incidentes de Seguridad Digital). Canal: `https://reporte.cnsd.gob.pe/home/minjus` `[VERIFICAR vigencia]`. Los campos del formulario real no constan en `knowledge/`: `[VERIFICAR]`. ESCENARIO SIMULADO.

| Campo | Contenido propuesto |
|---|---|
| Entidad | Universidad Nacional de San Agustín (UNSA) |
| Contacto | Dra. Mariela Quispe Huamaní, odp@unsa.example, 054-555-0301. Contacto técnico: Ing. Rodrigo Mamani Cáceres, oti@unsa.example |
| Tipo | Código malicioso (ransomware) con acceso no autorizado y probable exfiltración |
| Inicio / detección | 2026-10-10 20:50 / 2026-10-11 06:40 |
| Sistemas | Sistema de Registro Académico (SRV-SRA-APP, SRV-SRA-DB), SRV-ARCH, NAS-BKP-01 |
| Impacto | Indisponibilidad total del SRA y de sus respaldos; hasta 89 000 titulares; unos 900 menores |
| Vector | VPN sin MFA ni bloqueo, cuenta docente comprometida, escalamiento a administrador |
| Indicadores (IoC) | IP origen 203.0.113.50; destino de salida 198.51.100.200:443; cuenta `svc_mant`; extensión `.lck`; firma `Ransom.Lock.A` |
| Estado | Contención parcial (servidor aislado). Investigación en curso |
| Notificación a la ANPD | `[Indicar fecha y hora en que se envíe]` |
| Demora | Plazo de 48 h excedido. Se adjunta justificación |
