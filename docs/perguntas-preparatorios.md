# Perguntas Preparatórias — Login/Logout (Sprint 1)

> Roteiro de estudo pra defender o incremento de login/logout (histórias #1 e #2
> do backlog) numa Sprint Review, apresentação ou arguição. Cada pergunta tem a
> resposta logo abaixo — leia a pergunta primeiro, tente responder sozinho, só
> depois confira.

---

## Autenticação (`core/auth.py`, `core/decorators.py`)

### 1. Por que `autenticar()` retorna `None` tanto quando o e-mail não existe quanto quando a senha está errada, em vez de dois erros diferentes?

Segurança. Se o sistema respondesse "e-mail não encontrado" para um caso e
"senha incorreta" para outro, um atacante poderia usar o formulário de login
pra descobrir quais e-mails existem no banco (ataque de enumeração de
usuários), testando e-mails em massa e observando qual mensagem volta. O
critério de aceite da história #1 do backlog é explícito: *"Credenciais
inválidas exibem mensagem de erro sem revelar qual campo está errado"*. Por
isso `core/auth.py` tem dois caminhos de falha (`Usuario.DoesNotExist` e
`check_password` retornando `False`) que convergem pro mesmo `return None`, e
a view (`core/views.py`) só sabe "certo" ou "errado" — nunca o motivo.

### 2. Onde a senha é armazenada no banco? Ela fica em texto puro? O que é `check_password`?

Nunca em texto puro. O campo `senha_hash` do model `Usuario` guarda o
resultado de `django.contrib.auth.hashers.make_password()` (usado no comando
`seed`), que aplica um algoritmo de hash com salt (PBKDF2 por padrão no
Django) — uma via de mão única, não dá pra "descriptografar" de volta pra
senha original. No login, `check_password(senha_digitada, usuario.senha_hash)`
recalcula o hash da senha digitada com o mesmo salt e compara os hashes, não
as senhas.

### 3. Por que existe `login_obrigatorio` como decorator em vez de colocar o `if` dentro de cada view?

DRY (Don't Repeat Yourself). Sem o decorator, toda view protegida (hoje só
`painel_view`, mas futuramente doadores, famílias, itens etc.) teria que
repetir `if not request.session.get("id_usuario"): return redirect("login")`.
Com `@login_obrigatorio` em `core/decorators.py`, essa regra vive em um único
lugar — qualquer view nova só precisa do decorator, sem copiar lógica.

### 4. O que acontece se eu acessar `/painel/` direto pela URL, sem estar logado? Por quê?

O decorator intercepta a chamada antes do corpo de `painel_view` rodar, checa
`request.session.get("id_usuario")`, não encontra nada, e devolve um redirect
(HTTP 302) pra `/login/` — o código da view nunca chega a executar. Isso é
coberto pelo teste `test_painel_sem_sessao_redireciona_para_login`.

### 5. Por que o logout usa `request.session.flush()` e não `del request.session["id_usuario"]`?

`flush()` apaga os dados da sessão no backend **e** gera uma nova session key
para o navegador. `del request.session["id_usuario"]` só removeria essa
chave, mantendo a mesma session key ativa — mais vulnerável a *session
fixation* (se alguém conseguiu a session key antes do logout, ela continuaria
válida). `flush()` é a prática correta pra encerrar sessão com segurança,
exatamente o que o critério de aceite da história #2 pede.

---

## Sessão e expiração (`conecta/settings.py`)

### 6. O que faz `SESSION_SAVE_EVERY_REQUEST = True`? Se essa linha fosse removida, o que mudaria no comportamento de "expira por inatividade"?

Por padrão, o Django só regrava a sessão no backend quando ela é modificada.
`SESSION_COOKIE_AGE = 1800` define expiração de 30 minutos — mas sem
`SESSION_SAVE_EVERY_REQUEST = True`, esse contador não seria renovado a cada
requisição, ou seja, contaria 30 min a partir do **login**, não da **última
atividade**. Com a flag ligada, cada requisição HTTP regrava a sessão e
"reseta o relógio", fazendo a expiração ser de fato por inatividade, como
pede o critério de aceite da história #1.

---

## Formulários e templates

### 7. Por que usar `django.forms.Form` em vez de ler `request.POST["email"]` direto na view?

Validação centralizada (o `EmailField` já valida formato de e-mail antes de
qualquer lógica de negócio rodar), e nunca confiar em input cru vindo do
cliente. Também dá reuso: a mesma estrutura de campo (widget + label + regras)
fica disponível pra qualquer view que precise desse form.

### 8. Qual a diferença entre `base.html` e `auth_base.html`? Por que dois arquivos?

`base.html` tem a navbar pública (logo + link de entrar/sair), usada nas
páginas "dentro" do produto (home, painel). O layout aprovado no Figma para o
login é uma tela cheia dividida em dois painéis (marca + formulário), **sem**
essa navbar — decisão de design, a tela de entrada é diferente da tela de
uso. Por isso existe um segundo shell (`auth_base.html`) em vez de forçar o
login a caber dentro do `base.html`.

### 9. O que o `_campo_formulario.html` evita, comparado a escrever cada campo na mão?

Duplicação. Sem o partial, cada campo (e-mail, senha, e qualquer campo futuro
em qualquer formulário — cadastro de doador, família, item etc.) repetiria a
mesma estrutura de label + input + exibição de erro em HTML puro. Qualquer
mudança visual (ex: cor do texto de erro) teria que ser replicada em N
lugares, com risco real de esquecer um e deixar a UI inconsistente.

---

## O bug de cor (a pergunta mais reveladora — só quem acompanhou o debug responde bem)

### 10. Por que os botões e o painel verde ficaram transparentes na primeira versão, mesmo com o CSS "certo"?

O daisyUI 4.x resolve cada cor do tema como `oklch(var(--p)/1)` — ou seja,
espera que `--p` seja um **triplet OKLCH bruto** (`"L% C H"`, ex.:
`48.97% 0.08 176.52`). O tema `conecta` original tinha `--p: 161 56% 28%` no
formato **HSL** (herdado de uma versão anterior do daisyUI, que usava HSL).
`oklch(161 56% 28% / 1)` é sintaxe inválida — os números não fazem sentido
como lightness/chroma/hue — então o navegador simplesmente descarta a
declaração inteira e o elemento fica com o valor inicial: transparente. A
correção foi converter o hex de cada cor da marca (`#1f6f5f` etc.) pra OKLCH
de verdade.

### 11. Por que `.bg-primary` funcionou com um fallback em hex, mas `.btn-primary` não?

`.bg-primary` é uma regra de um nível só:
`background-color: var(--fallback-p, oklch(var(--p)/1))`. Se `--fallback-p`
for um hex válido, o navegador aceita direto — hex é um valor de cor completo.
Já `.btn-primary` passa por uma variável intermediária:
`--btn-color: var(--fallback-p)`, que depois é **reembrulhada** dentro de
outro `oklch(...)` na regra base do `.btn`:
`background-color: oklch(var(--btn-color, var(--b2)) / opacity)`. Se
`--fallback-p` for um hex (`#1f6f5f`), o resultado vira
`oklch(#1f6f5f / 1)` — inválido, porque não se pode meter um hex dentro da
função `oklch()`. É um bug real da build `full.min.css` standalone do
daisyUI 4 (pensada pra ser resolvida via build Tailwind/PostCSS, não via CDN
puro). A correção foi um override direto: `.btn-primary { --btn-color: var(--p); }`
em `static/css/app.css`, usando `--p` (já em OKLCH válido) em vez do fallback
quebrado.

---

## Nomenclatura

### 12. Por que trocamos `usuario_id` por `id_usuario` na sessão? Isso muda algum comportamento do sistema?

Não muda **nenhum** comportamento — é puramente convenção de nome. Todo o
`core/models.py` usa o padrão `id_<entidade>` para chave primária
(`id_usuario`, `id_doador`, `id_familia`, `id_item`...). O código de sessão
tinha ficado com `usuario_id` (ordem invertida), quebrando esse padrão e
potencialmente confundindo quem lê o código depois. É código limpo /
consistência, não correção de bug funcional.

---

## Testes

### 13. Qual a diferença entre `AutenticarTests` e `LoginLogoutViewTests`? Por que não bastava um dos dois?

`AutenticarTests` testa a função `autenticar()` isolada — chama a função
Python direto, sem HTTP, sessão ou template: é um teste **unitário** da regra
de negócio pura. `LoginLogoutViewTests` usa `self.client` (simula
requisições HTTP reais) e testa a **view inteira**: formulário,
redirecionamento, gravação de sessão, template renderizado — é um teste de
**integração**. Um não substitui o outro: o unitário pega erros na lógica
isolada mais rápido; o de integração pega erros que só aparecem quando tudo
está conectado (ex.: a view esquecer de chamar `autenticar()`, ou o redirect
ir pro lugar errado).

### 14. Por que existe um teste específico pra "usuário inativo"? Isso está em algum critério de aceite desta sprint?

O campo `ativo` no model `Usuario` existe pra suportar a história **#4** do
backlog ("desativar um usuário sem excluí-lo... usuário desativado não
consegue fazer login"), que **não é desta sprint**. Mesmo assim,
`autenticar()` já filtra por `ativo=True` desde já — então o teste garante
que essa trava funciona antes mesmo da história #4 ser implementada de
verdade, evitando que alguém quebre essa regra sem perceber no futuro.

---

## Rastreabilidade (a pergunta que fecha tudo)

### 15. Aponte, história por história, qual critério de aceite cada teste cobre.

**História #1 — Login com e-mail e senha**

| Critério de aceite (backlog) | Coberto por | Onde |
|---|---|---|
| Login com credenciais válidas redireciona para o painel | `test_login_valido_redireciona_para_painel` | `core/tests.py` |
| Credenciais inválidas exibem mensagem de erro sem revelar qual campo está errado | `test_login_invalido_mostra_erro_generico_e_nao_autentica` + `autenticar()` retornando `None` uniforme | `core/tests.py`, `core/auth.py` |
| Sessão expira após inatividade | `SESSION_COOKIE_AGE` + `SESSION_SAVE_EVERY_REQUEST` | `conecta/settings.py` — **sem teste automatizado ainda** |

**História #2 — Logout**

| Critério de aceite (backlog) | Coberto por | Onde |
|---|---|---|
| Botão de logout visível no menu | navbar condicional (`usuario_logado`) | `templates/base.html` |
| Após logout, redireciona para a tela de login | `test_logout_limpa_sessao_e_bloqueia_painel` | `core/tests.py` |
| Acesso a URL protegida após logout redireciona para login | mesmo teste acima (verifica `/painel/` depois do logout) | `core/tests.py` |

**Gap honesto pra levar pra retrospectiva:** a expiração por inatividade tem
a configuração certa, mas nenhum teste automatizado comprova de verdade que a
sessão expira depois de 30 minutos parada (precisaria simular passagem de
tempo, ex. com `freezegun` ou manipulando `SESSION_COOKIE_AGE` num teste
isolado). Vale registrar como pendência no plano de testes ou numa próxima
sprint.
