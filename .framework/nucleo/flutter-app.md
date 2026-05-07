# Blueprint Flutter — App nativo (espelha Portaria)

Stack travada: Flutter 3.24+, Dart 3.5+, Riverpod 2.5 (state), Dio 5 (HTTP), freezed 2 (models), go_router 14 (rotas), flutter_secure_storage 9 (JWT), envied (env vars).

## Estrutura (mirror Portaria)

```
{nome}/
├── lib/
│   ├── compartilhados/                # = Core
│   │   ├── auth/
│   │   │   ├── sessao.dart            # singleton com JWT + claims
│   │   │   ├── auth_interceptor.dart  # Dio interceptor
│   │   │   └── guard.dart             # RoleGuard p/ go_router
│   │   ├── http/
│   │   │   ├── dio_client.dart        # factory Dio com baseUrl + interceptor
│   │   │   └── comand_result.dart     # mirror C# ComandResult
│   │   ├── modelos/
│   │   │   ├── paged_result.dart      # mirror PagedResult<T>
│   │   │   └── entity_base.dart       # id, dataCadastro, status
│   │   └── widgets/                   # botoes, inputs, dialogs reutilizaveis
│   ├── dominios/                      # = dominios/Dominios
│   │   └── {plural}/                  # ex: clientes
│   │       ├── modelos/
│   │       │   └── {singular}.dart    # @freezed Cliente, SalvarCliente, AlterarCliente, ClienteSaida
│   │       ├── repositorios/
│   │       │   ├── i_{singular}_repositorio.dart  # contrato
│   │       │   └── {singular}_repositorio.dart    # impl Dio
│   │       └── notifiers/
│   │           └── {plural}_notifier.dart  # Riverpod AsyncNotifier
│   ├── apresentacao/
│   │   └── {feature}/
│   │       ├── pagina_{feature}.dart      # tela principal
│   │       └── widgets/
│   │           └── formulario_{singular}.dart
│   ├── nucleo/
│   │   ├── env.dart                   # @Envied (API_URL, ...)
│   │   ├── tema.dart                  # ThemeData claro/escuro
│   │   └── rotas.dart                 # GoRouter config
│   └── main.dart
├── pubspec.yaml
└── .env
```

## Padrão por Feature (5 arquivos canônicos por agregado)

### 1. `lib/dominios/clientes/modelos/cliente.dart`
```dart
import 'package:freezed_annotation/freezed_annotation.dart';
part 'cliente.freezed.dart';
part 'cliente.g.dart';

@freezed
class Cliente with _$Cliente {
  const factory Cliente({
    required String clienteId,
    required String nome,
    required String cpf,
    required String telefone,
    String? email,
  }) = _Cliente;

  factory Cliente.fromJson(Map<String, dynamic> json) => _$ClienteFromJson(json);
}

@freezed
class SalvarCliente with _$SalvarCliente {
  const factory SalvarCliente({
    required String nome,
    required String cpf,
    required String telefone,
    String? email,
  }) = _SalvarCliente;

  factory SalvarCliente.fromJson(Map<String, dynamic> json) => _$SalvarClienteFromJson(json);
}
```

### 2. `lib/dominios/clientes/repositorios/i_cliente_repositorio.dart`
```dart
abstract interface class IClienteRepositorio {
  Future<PagedResult<Cliente>> listar({int pageIndex = 1, int pageSize = 20, String? filter});
  Future<ComandResult> salvar(SalvarCliente payload);
  Future<ComandResult> alterar(AlterarCliente payload);
}
```

### 3. `lib/dominios/clientes/repositorios/cliente_repositorio.dart`
```dart
class ClienteRepositorio implements IClienteRepositorio {
  final Dio _dio;
  static const _base = '/api/cliente/v1';
  ClienteRepositorio(this._dio);

  @override
  Future<PagedResult<Cliente>> listar({int pageIndex = 1, int pageSize = 20, String? filter}) async {
    final r = await _dio.get<Map<String, dynamic>>(
      '$_base/listar/$pageIndex/$pageSize',
      queryParameters: filter == null ? null : {'filter': filter},
    );
    return PagedResult.fromJson(r.data!, (j) => Cliente.fromJson(j as Map<String, dynamic>));
  }

  @override
  Future<ComandResult> salvar(SalvarCliente p) async {
    final r = await _dio.post<Map<String, dynamic>>('$_base/salvar', data: p.toJson());
    return ComandResult.fromJson(r.data!);
  }

  @override
  Future<ComandResult> alterar(AlterarCliente p) async {
    final r = await _dio.put<Map<String, dynamic>>('$_base/alterar', data: p.toJson());
    return ComandResult.fromJson(r.data!);
  }
}

final clienteRepositorioProvider = Provider<IClienteRepositorio>((ref) {
  return ClienteRepositorio(ref.watch(dioProvider));
});
```

### 4. `lib/dominios/clientes/notifiers/clientes_notifier.dart`
```dart
@riverpod
class ClientesNotifier extends _$ClientesNotifier {
  @override
  Future<PagedResult<Cliente>> build({int pageIndex = 1, String? filter}) {
    return ref.read(clienteRepositorioProvider).listar(pageIndex: pageIndex, filter: filter);
  }

  Future<ComandResult> salvar(SalvarCliente payload) async {
    final result = await ref.read(clienteRepositorioProvider).salvar(payload);
    if (result.success) ref.invalidateSelf();
    return result;
  }
}
```

### 5. `lib/apresentacao/clientes/pagina_clientes.dart`
Tela com lista + botão novo. 4 estados explícitos via `AsyncValue.when(loading:, error:, data:)` (vazio = data com lista vazia).

## Convenções

| Item | Padrão |
|------|--------|
| Idioma | PT-BR em domínio |
| snake_case | arquivos e variáveis |
| PascalCase | classes |
| camelCase | métodos e propriedades |
| Estado | Riverpod 2 com `@riverpod` codegen |
| HTTP | Dio com interceptor JWT |
| Models | freezed + json_serializable |
| Rotas | go_router |
| Token storage | flutter_secure_storage |
| Validação | client-side básica (formKey + validators), server-side e a verdade |
| Tema | Material 3, `ThemeMode.system` |
| Internacionalização | só PT-BR no MVP |

## Mapping API C# Portaria → Flutter

- C# `EmpresaController` `v1/salvar` → Dart `EmpresaRepositorio.salvar()`
- C# `EmpresaSaida` (PascalCase) → Dart `Empresa` (camelCase via `@JsonKey(name: 'EmpresaId')`)
- C# `ComandResult` → Dart `ComandResult` (mesma estrutura)
- C# `PagedResult<T>` → Dart `PagedResult<T>` com generic `fromJson`

## Comandos para gerar code

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Sempre rodar após editar `@freezed` ou `@riverpod`.

## Onde fica o quê
- **Models freezed** → `lib/dominios/{plural}/modelos/`
- **HTTP repositório** → `lib/dominios/{plural}/repositorios/`
- **Estado** → `lib/dominios/{plural}/notifiers/`
- **UI** → `lib/apresentacao/{feature}/`
- **Auth/sessão** → `lib/compartilhados/auth/`
- **Rotas** → `lib/nucleo/rotas.dart`
