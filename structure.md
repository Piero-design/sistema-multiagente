sistema-multiagente/
│
├── SKILL.md                           # Skill principal del sistema
├── main.py                            # Punto de entrada
├── orchestrator.py                    # Coordinador de los 8 agentes
├── requirements.txt                   # Dependencias
├── README.md                          # Documentación general
│
├── database/                           # Base de datos compartida
│   ├── sistema.db                      # SQLite general
│   ├── schema.sql                      # Estructura de tablas
│   └── seed.sql                        # Datos de prueba
│
├── agents/
│   │
│   ├── Agente_formacion_conciencia-Grupo1/
│   │   ├── SKILL.md
│   │   ├── agent.py
│   │   ├── config.yaml
│   │   ├── skills/
│   │   │   ├── gestionar_capacitaciones/
│   │   │   │   └── SKILL.md
│   │   │   ├── evaluar_conocimientos/
│   │   │   │   └── SKILL.md
│   │   │   └── generar_recomendaciones/
│   │   │       └── SKILL.md
│   │   └── knowledge/
│   │       ├── knowledge.db
│   │       └── documents/
│   │
│   ├── Agente_evaluacion_riesgos-Grupo2/
│   │   ├── SKILL.md
│   │   ├── agent.py
│   │   ├── config.yaml
│   │   ├── skills/
│   │   │   ├── identificar_riesgos/
│   │   │   │   └── SKILL.md
│   │   │   ├── evaluar_impacto/
│   │   │   │   └── SKILL.md
│   │   │   └── proponer_mitigaciones/
│   │   │       └── SKILL.md
│   │   └── knowledge/
│   │       ├── knowledge.db
│   │       └── documents/
│   │
│   ├── Agente_derechos_dsar-Grupo3/
│   │   ├── SKILL.md
│   │   ├── agent.py
│   │   ├── config.yaml
│   │   ├── skills/
│   │   │   ├── registrar_solicitudes/
│   │   │   │   └── SKILL.md
│   │   │   ├── gestionar_derechos/
│   │   │   │   └── SKILL.md
│   │   │   └── seguimiento_solicitudes/
│   │   │       └── SKILL.md
│   │   └── knowledge/
│   │       ├── knowledge.db
│   │       └── documents/
│   │
│   ├── Agente_evidencia_auditoria-Grupo4/
│   │   ├── SKILL.md
│   │   ├── agent.py
│   │   ├── config.yaml
│   │   ├── skills/
│   │   │   ├── recopilar_evidencias/
│   │   │   │   └── SKILL.md
│   │   │   ├── verificar_cumplimiento/
│   │   │   │   └── SKILL.md
│   │   │   └── generar_reportes/
│   │   │       └── SKILL.md
│   │   └── knowledge/
│   │       ├── knowledge.db
│   │       └── documents/
│   │
│   ├── Agente_terceros_dpa-Grupo5/
│   │   ├── SKILL.md
│   │   ├── agent.py
│   │   ├── config.yaml
│   │   ├── skills/
│   │   │   ├── evaluar_proveedores/
│   │   │   │   └── SKILL.md
│   │   │   ├── revisar_acuerdos_dpa/
│   │   │   │   └── SKILL.md
│   │   │   └── monitorear_terceros/
│   │   │       └── SKILL.md
│   │   └── knowledge/
│   │       ├── knowledge.db
│   │       └── documents/
│   │
│   ├── Agente_inventario_datos-Grupo6/
│   │   ├── SKILL.md
│   │   ├── agent.py
│   │   ├── config.yaml
│   │   ├── skills/
│   │   │   ├── registrar_activos/
│   │   │   │   └── SKILL.md
│   │   │   ├── clasificar_datos/
│   │   │   │   └── SKILL.md
│   │   │   └── mapear_tratamientos/
│   │   │       └── SKILL.md
│   │   └── knowledge/
│   │       ├── knowledge.db
│   │       └── documents/
│   │
│   ├── Agente_controles_soa-Grupo7/
│   │   ├── SKILL.md
│   │   ├── agent.py
│   │   ├── config.yaml
│   │   ├── skills/
│   │   │   ├── gestionar_controles/
│   │   │   │   └── SKILL.md
│   │   │   ├── evaluar_implementacion/
│   │   │   │   └── SKILL.md
│   │   │   └── generar_soa/
│   │   │       └── SKILL.md
│   │   └── knowledge/
│   │       ├── knowledge.db
│   │       └── documents/
│   │
│   └── Agente_incidentes_brechas-Grupo8/
│       ├── SKILL.md
│       ├── agent.py
│       ├── config.yaml
│       ├── skills/
│       │   ├── registrar_incidentes/
│       │   │   └── SKILL.md
│       │   ├── evaluar_brechas/
│       │   │   └── SKILL.md
│       │   └── gestionar_respuesta/
│       │       └── SKILL.md
│       └── knowledge/
│           ├── knowledge.db
│           └── documents/
│
├── shared/
│   ├── db_connection.py
│   ├── models.py
│   └── utils.py
│
└── tests/
    ├── test_agents.py
    ├── test_database.py
    └── test_orchestrator.py