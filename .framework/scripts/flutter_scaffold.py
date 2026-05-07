#!/usr/bin/env python3
"""Scaffold de feature Flutter (Riverpod + Dio + freezed) que consome API C# Portaria.
Gera 5 arquivos canonicos: model, irepo, repo, notifier, pagina.

Uso:
  python .framework/scripts/flutter_scaffold.py <feature> [--singular Sing] [--raiz .] [--campos "..."]

Exemplo:
  python .framework/scripts/flutter_scaffold.py clientes --singular Cliente \\
     --campos "nome:string,cpf:string,telefone:string,email:string:opcional"
"""
from __future__ import annotations
import argparse, sys
from dataclasses import dataclass
from pathlib import Path

TIPOS_DART = {
    "string": "String",
    "int": "int",
    "long": "int",
    "decimal": "double",
    "bool": "bool",
    "guid": "String",
    "datetime": "DateTime",
}

@dataclass
class Campo:
    nome: str
    tipo: str
    obrigatorio: bool = True

def parse_campos(spec: str) -> list[Campo]:
    if not spec: return [Campo("nome","string")]
    out = []
    for raw in spec.split(","):
        partes = raw.strip().split(":")
        if len(partes) < 2: continue
        nome, tipo = partes[0], partes[1].lower()
        if tipo not in TIPOS_DART: continue
        c = Campo(nome=nome, tipo=tipo)
        if "opcional" in partes[2:]: c.obrigatorio = False
        out.append(c)
    if not any(c.nome == "nome" for c in out):
        out.insert(0, Campo("nome","string"))
    return out

def snake(s: str) -> str:
    """PascalCase -> snake_case"""
    out = []
    for i, ch in enumerate(s):
        if ch.isupper() and i > 0: out.append("_")
        out.append(ch.lower())
    return "".join(out)

def pascal(s: str) -> str:
    return s[0].upper() + s[1:] if s else s

def gerar_model(singular: str, campos: list[Campo], plural_pascal: str) -> str:
    s = singular
    s_lower = s[0].lower() + s[1:]
    arquivo = snake(s)
    # campos para classe Cliente (com Id)
    fields_cliente = []
    fields_cliente.append(f"    required String {s_lower}Id,  // PascalCase no JSON")
    for c in campos:
        dt = TIPOS_DART[c.tipo]
        if c.obrigatorio:
            fields_cliente.append(f"    required {dt} {c.nome},")
        else:
            fields_cliente.append(f"    {dt}? {c.nome},")
    fields_str = "\n".join(fields_cliente)

    # Salvar (sem id)
    fields_salvar = []
    for c in campos:
        dt = TIPOS_DART[c.tipo]
        if c.obrigatorio:
            fields_salvar.append(f"    required {dt} {c.nome},")
        else:
            fields_salvar.append(f"    {dt}? {c.nome},")
    fields_salvar_str = "\n".join(fields_salvar)

    # Alterar (com id + campos)
    fields_alterar = [f"    required String {s_lower}Id,"] + fields_salvar
    fields_alterar_str = "\n".join(fields_alterar)

    # JsonKey para mapear PascalCase do C# -> camelCase no Dart
    json_keys = []
    for c in campos:
        json_keys.append(f"      '{pascal(c.nome)}': instance.{c.nome},")
    return f'''import 'package:freezed_annotation/freezed_annotation.dart';

part '{arquivo}.freezed.dart';
part '{arquivo}.g.dart';

@freezed
class {s} with _${s} {{
  const factory {s}({{
    @JsonKey(name: '{s}Id') required String {s_lower}Id,
{fields_str.replace("    required String " + s_lower + "Id,  // PascalCase no JSON", "")}
  }}) = _{s};

  factory {s}.fromJson(Map<String, dynamic> json) => _${s}FromJson(json);
}}

@freezed
class Salvar{s} with _$Salvar{s} {{
  const factory Salvar{s}({{
{fields_salvar_str}
  }}) = _Salvar{s};

  factory Salvar{s}.fromJson(Map<String, dynamic> json) => _$Salvar{s}FromJson(json);
}}

@freezed
class Alterar{s} with _$Alterar{s} {{
  const factory Alterar{s}({{
    @JsonKey(name: '{s}Id') required String {s_lower}Id,
{fields_salvar_str}
  }}) = _Alterar{s};

  factory Alterar{s}.fromJson(Map<String, dynamic> json) => _$Alterar{s}FromJson(json);
}}
'''

def gerar_irepo(singular: str) -> str:
    s = singular
    arquivo = snake(s)
    return f'''import 'package:{{NOME_PROJETO}}/compartilhados/http/comand_result.dart';
import 'package:{{NOME_PROJETO}}/compartilhados/modelos/paged_result.dart';
import 'package:{{NOME_PROJETO}}/dominios/{snake(s)}s/modelos/{arquivo}.dart';

abstract interface class I{s}Repositorio {{
  Future<PagedResult<{s}>> listar({{int pageIndex = 1, int pageSize = 20, String? filter}});
  Future<ComandResult> salvar(Salvar{s} payload);
  Future<ComandResult> alterar(Alterar{s} payload);
}}
'''

def gerar_repo(singular: str, feature: str) -> str:
    s = singular
    s_lower = s.lower()
    arquivo = snake(s)
    return f'''import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:{{NOME_PROJETO}}/compartilhados/http/comand_result.dart';
import 'package:{{NOME_PROJETO}}/compartilhados/http/dio_client.dart';
import 'package:{{NOME_PROJETO}}/compartilhados/modelos/paged_result.dart';
import 'package:{{NOME_PROJETO}}/dominios/{feature}/modelos/{arquivo}.dart';
import 'package:{{NOME_PROJETO}}/dominios/{feature}/repositorios/i_{arquivo}_repositorio.dart';

class {s}Repositorio implements I{s}Repositorio {{
  final Dio _dio;
  static const _base = '/api/{s_lower}/v1';
  {s}Repositorio(this._dio);

  @override
  Future<PagedResult<{s}>> listar({{int pageIndex = 1, int pageSize = 20, String? filter}}) async {{
    final r = await _dio.get<Map<String, dynamic>>(
      '$_base/listar/$pageIndex/$pageSize',
      queryParameters: filter == null ? null : {{'filter': filter}},
    );
    return PagedResult.fromJson(r.data!, (j) => {s}.fromJson(j as Map<String, dynamic>));
  }}

  @override
  Future<ComandResult> salvar(Salvar{s} p) async {{
    final r = await _dio.post<Map<String, dynamic>>('$_base/salvar', data: p.toJson());
    return ComandResult.fromJson(r.data!);
  }}

  @override
  Future<ComandResult> alterar(Alterar{s} p) async {{
    final r = await _dio.put<Map<String, dynamic>>('$_base/alterar', data: p.toJson());
    return ComandResult.fromJson(r.data!);
  }}
}}

final {s_lower}RepositorioProvider = Provider<I{s}Repositorio>((ref) {{
  return {s}Repositorio(ref.watch(dioProvider));
}});
'''

def gerar_notifier(singular: str, feature: str) -> str:
    s = singular
    s_lower = s.lower()
    arquivo = snake(s)
    return f'''import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:{{NOME_PROJETO}}/compartilhados/http/comand_result.dart';
import 'package:{{NOME_PROJETO}}/compartilhados/modelos/paged_result.dart';
import 'package:{{NOME_PROJETO}}/dominios/{feature}/modelos/{arquivo}.dart';
import 'package:{{NOME_PROJETO}}/dominios/{feature}/repositorios/{arquivo}_repositorio.dart';

part '{feature}_notifier.g.dart';

@riverpod
class {s}sNotifier extends _${s}sNotifier {{
  @override
  Future<PagedResult<{s}>> build({{int pageIndex = 1, String? filter}}) {{
    return ref.read({s_lower}RepositorioProvider).listar(pageIndex: pageIndex, filter: filter);
  }}

  Future<ComandResult> salvar(Salvar{s} payload) async {{
    final result = await ref.read({s_lower}RepositorioProvider).salvar(payload);
    if (result.success) ref.invalidateSelf();
    return result;
  }}

  Future<ComandResult> alterar(Alterar{s} payload) async {{
    final result = await ref.read({s_lower}RepositorioProvider).alterar(payload);
    if (result.success) ref.invalidateSelf();
    return result;
  }}
}}
'''

def gerar_pagina(singular: str, feature: str) -> str:
    s = singular
    s_lower = s.lower()
    return f'''import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:{{NOME_PROJETO}}/dominios/{feature}/notifiers/{feature}_notifier.dart';

class Pagina{s}s extends ConsumerWidget {{
  const Pagina{s}s({{super.key}});

  @override
  Widget build(BuildContext context, WidgetRef ref) {{
    final state = ref.watch({s_lower}sNotifierProvider());

    return Scaffold(
      appBar: AppBar(title: const Text('{s}s')),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erro: $e')),
        data: (paged) {{
          if (paged.list.isEmpty) {{
            return const Center(child: Text('Nenhum {s_lower} cadastrado ainda.'));
          }}
          return ListView.builder(
            itemCount: paged.list.length,
            itemBuilder: (_, i) => ListTile(title: Text(paged.list[i].nome)),
          );
        }},
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {{
          // TODO: abrir formulario novo
        }},
        child: const Icon(Icons.add),
      ),
    );
  }}
}}
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--singular", default=None)
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--campos", default="")
    args = ap.parse_args()

    feature = args.feature
    singular = args.singular or (feature.rstrip("s").capitalize() if feature.endswith("s") else feature.capitalize())
    raiz = Path(args.raiz).resolve()
    campos = parse_campos(args.campos)

    # detecta nome do projeto via pubspec.yaml
    pubspec = raiz / "pubspec.yaml"
    nome_projeto = "app"
    if pubspec.exists():
        for ln in pubspec.read_text(encoding="utf-8").splitlines():
            if ln.startswith("name:"):
                nome_projeto = ln.split(":", 1)[1].strip()
                break

    arquivo_singular = snake(singular)

    arquivos = [
        (raiz / f"lib/dominios/{feature}/modelos/{arquivo_singular}.dart",
         gerar_model(singular, campos, feature.capitalize())),
        (raiz / f"lib/dominios/{feature}/repositorios/i_{arquivo_singular}_repositorio.dart",
         gerar_irepo(singular).replace("{NOME_PROJETO}", nome_projeto)),
        (raiz / f"lib/dominios/{feature}/repositorios/{arquivo_singular}_repositorio.dart",
         gerar_repo(singular, feature).replace("{NOME_PROJETO}", nome_projeto)),
        (raiz / f"lib/dominios/{feature}/notifiers/{feature}_notifier.dart",
         gerar_notifier(singular, feature).replace("{NOME_PROJETO}", nome_projeto)),
        (raiz / f"lib/apresentacao/{feature}/pagina_{feature}.dart",
         gerar_pagina(singular, feature).replace("{NOME_PROJETO}", nome_projeto)),
    ]

    criados, existentes = [], []
    for caminho, conteudo in arquivos:
        if caminho.exists():
            existentes.append(str(caminho.relative_to(raiz))); continue
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(conteudo, encoding="utf-8")
        criados.append(str(caminho.relative_to(raiz)))

    print(f"Feature {feature} (singular: {singular}, campos: {len(campos)}):")
    for c in criados: print(f"  + {c}")
    for e in existentes: print(f"  = {e} (ja existia)")
    print(f"\nProximo: flutter pub run build_runner build --delete-conflicting-outputs")
    print(f"Depois: registrar Pagina{singular}s em lib/nucleo/rotas.dart")

if __name__ == "__main__":
    main()
