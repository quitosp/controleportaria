# Blueprint Python — FastAPI espelhando Portaria

Stack: Python 3.12, FastAPI, SQLAlchemy 2 + Alembic, Pydantic v2, dependency-injector, pytest.

## Camadas (espelha C# Portaria)

```
{projeto}/
├── compartilhados/                   # = compartilhados/Core
│   ├── __init__.py
│   ├── entidade_base.py              # Entity equivalente
│   ├── comando_base.py               # Comand
│   ├── resultado.py                  # ComandResult, PagedResult
│   ├── unidade_trabalho.py           # IUnitOfWork
│   ├── excecoes.py
│   └── util/
│       └── data_brasilia.py
├── dominios/                         # = dominios/Dominios
│   └── {plural}/
│       ├── entidades/
│       │   └── {singular}.py
│       ├── comandos/
│       │   ├── entradas.py           # SalvarXEntrada, AlterarXEntrada (Pydantic)
│       │   ├── handlers.py           # XHandler
│       │   └── saidas.py             # XSaida
│       └── i_repositorios.py
├── repositorios/                     # = repositorios/Repositorios
│   ├── contexto.py                   # SQLAlchemy session factory
│   ├── mapeamentos/
│   │   └── {singular}_map.py         # Table mapping
│   └── repositorio/
│       └── {singular}_repositorio.py
├── servicos/                         # = servicos/api/Api
│   └── api/
│       ├── main.py                   # FastAPI app
│       ├── controladores/
│       │   └── {singular}_controlador.py  # APIRouter
│       ├── configuracao/
│       │   ├── di.py                 # injector
│       │   ├── api_config.py
│       │   └── jwt_config.py
│       └── identidade/
│           └── auth.py
├── alembic/
├── pyproject.toml
└── .env
```

## Padrão por Agregado (espelha o C#)

Para `Veiculo`:

### 1. `dominios/veiculos/entidades/veiculo.py`
```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from compartilhados.entidade_base import Entity

class Veiculo(Entity):
    def __init__(self, nome: str):
        super().__init__()
        self.nome = nome

    def alterar(self, nome: str) -> None:
        self.nome = nome
```

### 2. `dominios/veiculos/comandos/entradas.py`
```python
from uuid import UUID
from pydantic import BaseModel, Field

class SalvarVeiculoEntrada(BaseModel):
    nome: str = Field(min_length=1)

class AlterarVeiculoEntrada(BaseModel):
    veiculo_id: UUID
    nome: str = Field(min_length=1)
```

### 3. `dominios/veiculos/comandos/saidas.py`
```python
from uuid import UUID
from pydantic import BaseModel

class VeiculoSaida(BaseModel):
    veiculo_id: UUID
    nome: str
```

### 4. `dominios/veiculos/comandos/handlers.py`
```python
from compartilhados.resultado import ComandResult
from dominios.veiculos.entidades.veiculo import Veiculo
from dominios.veiculos.i_repositorios import IVeiculoRepositorio
from .entradas import SalvarVeiculoEntrada, AlterarVeiculoEntrada

class VeiculoHandler:
    def __init__(self, repositorio: IVeiculoRepositorio):
        self._repositorio = repositorio

    async def salvar(self, msg: SalvarVeiculoEntrada) -> ComandResult:
        entidade = Veiculo(msg.nome)
        self._repositorio.salvar(entidade)
        ok = await self._repositorio.unidade_trabalho.commit()
        if not ok:
            return ComandResult(success=False, message="Erro ao persistir", code=400)
        return ComandResult(success=True, message="Veículo salvo com sucesso!")

    async def alterar(self, msg: AlterarVeiculoEntrada) -> ComandResult:
        existe = await self._repositorio.existe(msg.veiculo_id)
        if existe is None:
            return ComandResult(success=False, message="Veículo não encontrado", code=404)
        existe.alterar(msg.nome)
        self._repositorio.alterar(existe)
        ok = await self._repositorio.unidade_trabalho.commit()
        return ComandResult(success=ok, message="Veículo alterado com sucesso!" if ok else "Erro")
```

### 5. `dominios/veiculos/i_repositorios.py`
```python
from abc import ABC, abstractmethod
from uuid import UUID
from compartilhados.unidade_trabalho import IUnidadeTrabalho
from compartilhados.resultado import PagedResult
from .entidades.veiculo import Veiculo
from .comandos.saidas import VeiculoSaida

class IVeiculoRepositorio(ABC):
    @property
    @abstractmethod
    def unidade_trabalho(self) -> IUnidadeTrabalho: ...
    @abstractmethod
    def salvar(self, entidade: Veiculo) -> Veiculo: ...
    @abstractmethod
    def alterar(self, entidade: Veiculo) -> None: ...
    @abstractmethod
    async def existe(self, id: UUID) -> Veiculo | None: ...
    @abstractmethod
    async def listar(self, page_index: int, page_size: int, filter: str | None = None) -> PagedResult[VeiculoSaida]: ...
```

### 6. `repositorios/repositorio/veiculo_repositorio.py`
SQLAlchemy 2 async session, padrão repositório.

### 7. `servicos/api/controladores/veiculo_controlador.py`
```python
from fastapi import APIRouter, Depends
from compartilhados.resultado import ComandResult, PagedResult
from dominios.veiculos.comandos.entradas import SalvarVeiculoEntrada, AlterarVeiculoEntrada
from dominios.veiculos.comandos.saidas import VeiculoSaida
from dominios.veiculos.comandos.handlers import VeiculoHandler
from dominios.veiculos.i_repositorios import IVeiculoRepositorio

router = APIRouter(prefix="/api/veiculo", tags=["veiculo"])

@router.post("/v1/salvar", response_model=ComandResult)
async def salvar(cmd: SalvarVeiculoEntrada, handler: VeiculoHandler = Depends()):
    return await handler.salvar(cmd)

@router.put("/v1/alterar", response_model=ComandResult)
async def alterar(cmd: AlterarVeiculoEntrada, handler: VeiculoHandler = Depends()):
    return await handler.alterar(cmd)

@router.get("/v1/listar/{page_index}/{page_size}", response_model=PagedResult[VeiculoSaida])
async def listar(page_index: int, page_size: int, filter: str | None = None,
                 repo: IVeiculoRepositorio = Depends()):
    return await repo.listar(page_index, page_size, filter)
```

## Convenções

| Item | Padrão |
|------|--------|
| Idioma | PT-BR em domínio |
| Snake case | arquivos e funções |
| PascalCase | classes e Pydantic models |
| Async | tudo I/O async |
| Resposta | sempre `ComandResult` ou `PagedResult` |
| Validação | Pydantic v2 |
| Migração | Alembic |
