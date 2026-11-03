"""Contrato propio del Grupo 6, sin sustituir un protocolo común inexistente."""
from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=300)]
Label = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=120)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Contexto(Model):
    finalidad: Text | None = None
    base_juridica: Text | None = None
    titulares: list[Text] = Field(default_factory=list, max_length=30)
    responsable: Text | None = None
    accesos: list[Text] = Field(default_factory=list, max_length=30)
    almacenamiento: Text | None = None
    transferencias: list[Text] = Field(default_factory=list, max_length=30)
    retencion: Text | None = None


class Fuente(Model):
    id: Label
    nombre: Text
    sistema: Text
    formato: Literal["texto", "csv", "json", "campos"] = "texto"
    contenido: Annotated[str, StringConstraints(strict=True, max_length=200000)] | None = None
    campos: list[Label] = Field(default_factory=list, max_length=200)
    contexto: Contexto = Field(default_factory=Contexto)

    @model_validator(mode="after")
    def contenido_segun_formato(self):
        if self.formato == "campos":
            if not self.campos or self.contenido is not None:
                raise ValueError("El formato campos requiere campos y no admite contenido.")
        elif self.campos or self.contenido is None or not self.contenido.strip():
            raise ValueError("Este formato requiere contenido no vacío y no admite campos.")
        return self


Action = Literal["analizar", "registrar_activos", "clasificar_datos", "consultar_inventario", "mapear_tratamientos", "confirmar_cobertura", "exportar_evidencia"]


class Solicitud(Model):
    accion: Action
    organizacion: Label
    request_id: Label | None = None
    fuentes: list[Fuente] = Field(default_factory=list, max_length=20)
    campos: list[Label] = Field(default_factory=list, max_length=200)
    sistema: Text | None = None
    missing_systems: list[Text] = Field(default_factory=list, max_length=100)
    found_systems: list[Text] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def argumentos_segun_accion(self):
        if self.accion in {"analizar", "registrar_activos"}:
            if not self.fuentes:
                raise ValueError("Se requiere al menos una fuente.")
            ids = [f.id for f in self.fuentes]
            if len(ids) != len(set(ids)):
                raise ValueError("Los ID de fuente no pueden repetirse en una solicitud.")
            if sum(len(f.contenido or "") for f in self.fuentes) > 1000000:
                raise ValueError("El total de contenido no puede superar 1 000 000 caracteres.")
        elif self.fuentes:
            raise ValueError("Esta acción no admite fuentes.")
        if self.accion == "clasificar_datos":
            if not self.campos:
                raise ValueError("Se requiere al menos un campo.")
        elif self.campos:
            raise ValueError("Esta acción no admite campos.")
        if self.accion != "confirmar_cobertura" and (self.missing_systems or self.found_systems):
            raise ValueError("Las listas de cobertura solo se admiten en confirmar_cobertura.")
        if self.accion == "confirmar_cobertura" and not self.missing_systems:
            raise ValueError("Indica los sistemas cuya cobertura se desea revisar.")
        if self.sistema and self.accion not in {"consultar_inventario", "mapear_tratamientos", "exportar_evidencia"}:
            raise ValueError("El filtro sistema no se admite para esta acción.")
        return self


class HandoffPayload(Model):
    missing_systems: list[Text] = Field(min_length=1, max_length=100)
    found_systems: list[Text] = Field(default_factory=list, max_length=100)


class Handoff(Model):
    from_agent: Literal["dsar"]
    to_agent: Literal["inventario"]
    case_ref: Label
    control_ref: Label
    action: Literal["confirmar_cobertura"]
    payload: HandoffPayload
    requires_hitl: bool
    created_at: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=100)]
    sha256: Annotated[str, StringConstraints(strict=True, pattern=r"^[0-9a-f]{64}$")]
