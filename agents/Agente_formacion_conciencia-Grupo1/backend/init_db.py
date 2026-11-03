import uuid
from datetime import datetime, timedelta
from db import init_schema, get_db_connection
from auth import hash_password

def inicializar_base_de_datos():
    print("Iniciando creación de tablas SQLite...")
    init_schema()

    now = datetime.now()
    fecha_antigua = (now - timedelta(days=120)).strftime("%Y-%m-%d %H:%M:%S")
    fecha_reciente = (now - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")

    # Fechas de vencimiento
    vencido_fecha = (now - timedelta(days=15)).strftime("%Y-%m-%d")
    futuro_fecha = (now + timedelta(days=45)).strftime("%Y-%m-%d")
    hace_un_mes = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    # Contraseñas con bcrypt
    pass_admin = hash_password("admin")
    pass_maria = hash_password("maria123")
    pass_juan = hash_password("juan123")
    pass_ana = hash_password("ana123")
    pass_lucia = hash_password("lucia123")
    pass_roberto = hash_password("roberto123")
    pass_carlos = hash_password("carlos123")
    pass_pedro = hash_password("pedro123")
    pass_sofia = hash_password("sofia123")
    pass_elena = hash_password("elena123")

    pass_n1 = hash_password("nuevo1")
    pass_n2 = hash_password("nuevo2")
    pass_n3 = hash_password("nuevo3")
    pass_n4 = hash_password("nuevo4")
    pass_n5 = hash_password("nuevo5")

    # 15 Usuarios (10 antiguos + 5 nuevos)
    usuarios = [
        # Antiguos (> 90 días)
        ("admin", "admin@unsa.edu.pe", pass_admin, "Administrador del Sistema", "admin", "Rectorado", "Sistemas", 1, fecha_antigua),
        ("maria.lopez", "maria.lopez@unsa.edu.pe", pass_maria, "María López", "jefe", "Ingeniería", "Sistemas", 1, fecha_antigua),
        ("juan.perez", "juan.perez@unsa.edu.pe", pass_juan, "Juan Pérez", "docente", "Ingeniería", "Sistemas", 1, fecha_antigua),
        ("ana.gomez", "ana.gomez@unsa.edu.pe", pass_ana, "Ana Gómez", "docente", "Medicina", "Clínicas", 1, fecha_antigua),
        ("lucia.torres", "lucia.torres@unsa.edu.pe", pass_lucia, "Lucía Torres", "docente", "Derecho", "Privado", 1, fecha_antigua),
        ("roberto.diaz", "roberto.diaz@unsa.edu.pe", pass_roberto, "Roberto Díaz", "docente", "Sociales", "Sociología", 1, fecha_antigua),
        ("carlos.ruiz", "carlos.ruiz@unsa.edu.pe", pass_carlos, "Carlos Ruiz", "administrativo", "Administración Central", "RRHH", 1, fecha_antigua),
        ("pedro.silva", "pedro.silva@unsa.edu.pe", pass_pedro, "Pedro Silva", "administrativo", "Administración Central", "Registros", 1, fecha_antigua),
        ("sofia.castro", "sofia.castro@unsa.edu.pe", pass_sofia, "Sofía Castro", "administrativo", "Biblioteca Central", "Biblioteca", 1, fecha_antigua),
        ("elena.vargas", "elena.vargas@unsa.edu.pe", pass_elena, "Elena Vargas", "auditor", "Control Interno", "Auditoría", 1, fecha_antigua),

        # Nuevos (< 30 días)
        ("nuevo1", "nuevo1@unsa.edu.pe", pass_n1, "Luis Mendoza", "docente", "Ingeniería", "Sistemas", 1, fecha_reciente),
        ("nuevo2", "nuevo2@unsa.edu.pe", pass_n2, "Carla Ríos", "docente", "Medicina", "Biomédicas", 1, fecha_reciente),
        ("nuevo3", "nuevo3@unsa.edu.pe", pass_n3, "Diego Paredes", "administrativo", "Administración Central", "RRHH", 1, fecha_reciente),
        ("nuevo4", "nuevo4@unsa.edu.pe", pass_n4, "Valeria Núñez", "administrativo", "Biblioteca Central", "Biblioteca", 1, fecha_reciente),
        ("nuevo5", "nuevo5@unsa.edu.pe", pass_n5, "Andrés Quispe", "docente", "Derecho", "Público", 1, fecha_reciente),
        ("juliochura68", "juliochura68@gmail.com", pass_admin, "Julio Chura", "admin", "Ingeniería", "Sistemas", 1, fecha_reciente),
        ("churajulio68", "churajulio68@gmail.com", pass_admin, "Julio Chura Acero", "docente", "Ingeniería", "Sistemas", 1, fecha_reciente)
    ]

    # 5 Formaciones
    formaciones = [
        ("f001", "Protección de Datos Personales - Ley 29733", "Aspectos fundamentales de la ley peruana y tratamiento legítimo de datos personales en el entorno universitario.", "docentes y administrativos", 90, "A.3.17", fecha_antigua),
        ("f002", "ISO 27701:2025 - Fundamentos de Privacidad", "Gestión del Sistema PIMS institucional, roles de privacidad y gobierno de la información.", "jefes y admin", 120, "A.3.17", fecha_antigua),
        ("f003", "Cultura y Concienciación en Privacidad de Datos", "Taller de sensibilización para la prevención del phishing, manejo seguro de contraseñas y custodia de expedientes universitarios.", "todos", 60, "A.3.17", fecha_antigua),
        ("f004", "Cómo reportar una brecha de datos", "Protocolo ante incidentes de fuga de información y notificación inmediata a la Autoridad Nacional.", "todos", 60, "A.3.11", fecha_antigua),
        ("f005", "Derechos de los titulares de datos", "Atención y gestión de derechos ARCO (Acceso, Rectificación, Cancelación y Oposición) para personal de ventanilla.", "administrativos", 60, "A.3.17", fecha_antigua)
    ]

    # Asignaciones de formación
    asignaciones = [
        # Juan Pérez (docente antiguo): 2 pendientes, 1 vencido
        ("fu_001", "juan.perez", "f001", "pendiente", hace_un_mes, None, futuro_fecha, None),
        ("fu_002", "juan.perez", "f003", "pendiente", hace_un_mes, None, futuro_fecha, None),
        ("fu_003", "juan.perez", "f004", "vencido", fecha_antigua, None, vencido_fecha, None),

        # María López (jefe antigua): completado y pendiente
        ("fu_004", "maria.lopez", "f002", "completado", fecha_antigua, hace_un_mes, futuro_fecha, "https://pims.unsa.edu.pe/certificados/Cert_f002_maria.pdf"),
        ("fu_005", "maria.lopez", "f003", "completado", fecha_antigua, hace_un_mes, futuro_fecha, "https://pims.unsa.edu.pe/certificados/Cert_f003_maria.pdf"),

        # Carlos Ruiz (administrativo):
        ("fu_006", "carlos.ruiz", "f001", "completado", fecha_antigua, hace_un_mes, futuro_fecha, "https://pims.unsa.edu.pe/certificados/Cert_f001_carlos.pdf"),
        ("fu_007", "carlos.ruiz", "f005", "pendiente", hace_un_mes, None, futuro_fecha, None),

        # 5 Nuevos: TODOS en estado PENDIENTE
        ("fu_n01", "nuevo1", "f001", "pendiente", fecha_reciente, None, futuro_fecha, None),
        ("fu_n02", "nuevo1", "f003", "pendiente", fecha_reciente, None, futuro_fecha, None),
        ("fu_n03", "nuevo2", "f001", "pendiente", fecha_reciente, None, futuro_fecha, None),
        ("fu_n04", "nuevo3", "f005", "pendiente", fecha_reciente, None, futuro_fecha, None),
        ("fu_n05", "nuevo4", "f005", "pendiente", fecha_reciente, None, futuro_fecha, None),
        ("fu_n06", "nuevo5", "f001", "pendiente", fecha_reciente, None, futuro_fecha, None),
    ]

    # 3 Conversaciones de ejemplo
    conv1_id = "c1111111-1111-1111-1111-111111111111"
    conv2_id = "c2222222-2222-2222-2222-222222222222"
    conv3_id = "c3333333-3333-3333-3333-333333333333"

    conversaciones = [
        (conv1_id, "admin", "Consulta sobre estado de personal nuevo", fecha_reciente, fecha_reciente),
        (conv2_id, "juan.perez", "Mis cursos obligatorios pendientes", hace_un_mes, hace_un_mes),
        (conv3_id, "maria.lopez", "Cumplimiento de formación del equipo de Ingeniería", hace_un_mes, hace_un_mes)
    ]

    mensajes = [
        (conv1_id, "user", "¿Quiénes son los usuarios nuevos?", fecha_reciente),
        (conv1_id, "assistant", "Estimado Administrador, se identifican 5 usuarios registrados recientemente: Luis Mendoza (Docente Ingeniería), Carla Ríos (Docente Medicina), Diego Paredes (Administrativo RRHH), Valeria Núñez (Administrativo Biblioteca) y Andrés Quispe (Docente Derecho). Todos tienen asignaciones formativas pendientes.", fecha_reciente),
        (conv2_id, "user", "¿Qué me falta completar este semestre?", hace_un_mes),
        (conv2_id, "assistant", "Profesor Juan Pérez, según el control A.3.17 de ISO 27701:2025 y la Ley N° 29733, registra 2 formaciones pendientes: 'Protección de Datos Personales' y 'Cultura y Concienciación en Privacidad de Datos'. Asimismo, la formación 'Cómo reportar una brecha de datos' se encuentra vencida.", hace_un_mes),
        (conv3_id, "user", "¿Cómo va el cumplimiento de formación en mi facultad?", hace_un_mes),
        (conv3_id, "assistant", "Ing. María López, en la Facultad de Ingeniería el 65% de los docentes han completado sus cursos de formación obligatorios bajo el control A.3.17. ¿Desea que preparemos una convocatoria para los docentes pendientes?", hace_un_mes)
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Limpiar datos previos si existen
        cursor.execute("DELETE FROM mensajes")
        cursor.execute("DELETE FROM conversaciones")
        cursor.execute("DELETE FROM formacion_usuario")
        cursor.execute("DELETE FROM formaciones")
        cursor.execute("DELETE FROM usuarios")
        cursor.execute("DELETE FROM correos_enviados")
        cursor.execute("DELETE FROM matriculas_lms_mock")
        cursor.execute("DELETE FROM acciones_pendientes")
        cursor.execute("DELETE FROM evidencias")
        cursor.execute("DELETE FROM audit_log")

        # Insertar usuarios
        cursor.executemany(
            """
            INSERT INTO usuarios (id, email, password_hash, nombre, rol, facultad, departamento, activo, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            usuarios
        )

        # Insertar formaciones
        cursor.executemany(
            """
            INSERT INTO formaciones (id, titulo, descripcion, obligatoria_para, duracion_minutos, control_iso, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            formaciones
        )

        # Insertar asignaciones
        cursor.executemany(
            """
            INSERT INTO formacion_usuario (id, user_id, formacion_id, estado, fecha_asignacion, fecha_completado, fecha_vencimiento, certificado_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            asignaciones
        )

        # Insertar conversaciones
        cursor.executemany(
            """
            INSERT INTO conversaciones (id, user_id, titulo, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            conversaciones
        )

        # Insertar mensajes
        cursor.executemany(
            """
            INSERT INTO mensajes (conversacion_id, rol, contenido, created_at)
            VALUES (?, ?, ?, ?)
            """,
            mensajes
        )

        conn.commit()

    print("[OK] Base de datos SQLite inicializada exitosamente:")
    print("   - 15 usuarios precargados (10 antiguos + 5 nuevos).")
    print("   - 5 formaciones ISO 27701 y Ley 29733.")
    print("   - Asignaciones de formación sintéticas (Control A.3.17).")
    print("   - 3 conversaciones y 6 mensajes de ejemplo.")
    print("   - 0 correos enviados inicialmente (listo para flujo de envío masivo).")

if __name__ == "__main__":
    inicializar_base_de_datos()
