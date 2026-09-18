# Perguntas Preparatórias — Login/Logout (Sprint 1)

> Roteiro de estudo pra defender o incremento de login/logout (histórias #1 e #2
> do backlog) numa Sprint Review, apresentação ou arguição. Cada pergunta tem a
> resposta logo abaixo — leia a pergunta primeiro, tente responder sozinho, só
> depois confira.

---

## Autenticação (`core/models.py`, `core/decorators.py`)

> **Nota:** a partir de uma refatoração posterior à sprint 1, a autenticação
> deixou de ser feita "na mão" (sessão manual) e passou a usar o sistema
> nativo do Django (`AbstractBaseUser` + `authenticate()`/`login()`/`logout()`).
> As perguntas 1 a 5 abaixo foram atualizadas pra refletir o código atual; o
> *porquê* de cada decisão de segurança continua valendo, só o *como* mudou.
> Detalhes completos da migração estão na seção
> "[Migração para o sistema de autenticação nativo do Django](#migração-para-o-sistema-de-autenticação-nativo-do-django)".

### 1. Por que `authenticate()` retorna `None` tanto quando o e-mail não existe quanto quando a senha está errada, em vez de dois erros diferentes?

Segurança. Se o sistema respondesse "e-mail não encontrado" para um caso e
"senha incorreta" para outro, um atacante poderia usar o formulário de login
pra descobrir quais e-mails existem no banco (ataque de enumeração de
usuários), testando e-mails em massa e observando qual mensagem volta. O
critério de aceite da história #1 do backlog é explícito: *"Credenciais
inválidas exibem mensagem de erro sem revelar qual campo está errado"*. Hoje
quem resolve isso é o `ModelBackend` do Django (`django.contrib.auth.authenticate`,
chamado em `core/views.py`): se o e-mail não existe, ele mesmo assim roda um
hash de senha "de mentira" pra gastar o mesmo tempo de CPU (evita até
*timing attack*, não só a mensagem de erro) e retorna `None`; se a senha está
errada, `Usuario.check_password()` retorna `False` e o backend também
retorna `None`. A view (`core/views.py`) só sabe "certo" ou "errado" — nunca
o motivo.

### 2. Onde a senha é armazenada no banco? Ela fica em texto puro? O que é `check_password`?

Nunca em texto puro. O campo `senha_hash` do model `Usuario` guarda o
resultado de `django.contrib.auth.hashers.make_password()` (usado no comando
`seed` e no `UsuarioManager`), que aplica um algoritmo de hash com salt
(PBKDF2 por padrão no Django) — uma via de mão única, não dá pra
"descriptografar" de volta pra senha original. No login,
`usuario.check_password(senha_digitada)` (método de instância, sobrescrito em
`core/models.py` pra comparar contra `senha_hash`) recalcula o hash da senha
digitada com o mesmo salt e compara os hashes, não as senhas.

### 3. Por que existe `login_obrigatorio` como decorator em vez de colocar o `if` dentro de cada view?

DRY (Don't Repeat Yourself). Sem o decorator, toda view protegida (hoje
`painel_view`, `usuarios_view`, `usuario_alternar_status_view`, e
futuramente doadores, famílias, itens etc.) teria que repetir a checagem de
autenticação. Hoje `login_obrigatorio` (`core/decorators.py`) é um wrapper
fino em cima do `login_required` nativo do Django — centraliza a
configuração (`login_url="login"`) num único lugar, qualquer view nova só
precisa do decorator, sem copiar lógica nem repetir esses argumentos.

### 4. O que acontece se eu acessar `/painel/` direto pela URL, sem estar logado? Por quê?

O `login_required` (nativo do Django, usado por `login_obrigatorio`)
intercepta a chamada antes do corpo de `painel_view` rodar, checa
`request.user.is_authenticated` e, sendo `False`, devolve um redirect (HTTP
302) pra `/login/` — o código da view nunca chega a executar.
`request.user` é resolvido automaticamente pelo `AuthenticationMiddleware`
a partir da sessão em toda requisição, então mesmo que o usuário fique
inativo (`ativo=False`) no meio da sessão, a próxima requisição já reflete
isso — coberto pelo teste
`test_usuario_desativado_com_sessao_ativa_perde_acesso`. O caso de nunca
ter feito login é coberto por
`test_painel_sem_sessao_redireciona_para_login`.

### 5. Por que o logout usa `django.contrib.auth.logout()` e não só apagar uma chave da sessão?

`logout(request)` apaga os dados da sessão no backend **e** gera uma nova
session key para o navegador (por baixo dos panos, chama
`request.session.flush()`). Só apagar uma chave específica da sessão
manteria a mesma session key ativa — mais vulnerável a *session fixation*
(se alguém conseguiu a session key antes do logout, ela continuaria
válida). Usar a função pronta do framework garante essa prática de
segurança sem reimplementá-la, exatamente o que o critério de aceite da
história #2 pede.

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

**Nota histórica:** essa pergunta descreve uma decisão de quando a sessão
era gravada manualmente (`request.session["id_usuario"] = ...`). Depois da
migração pro auth nativo do Django (ver seção dedicada abaixo), quem decide
a chave usada na sessão é o próprio framework (`_auth_user_id`), então essa
convenção de nome não existe mais no código — a pergunta fica só como
registro de por que o padrão `id_<entidade>` importava. Resposta original:
não mudava **nenhum** comportamento, era puramente convenção de nome. Todo o
`core/models.py` usa o padrão `id_<entidade>` para chave primária
(`id_usuario`, `id_doador`, `id_familia`, `id_item`...); o código de sessão
tinha ficado com `usuario_id` (ordem invertida), quebrando esse padrão.

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

## Migração para o sistema de autenticação nativo do Django

> Essas perguntas cobrem uma refatoração feita depois da sprint 1: a troca da
> sessão manual (`request.session["id_usuario"] = ...`) pelo sistema de
> autenticação nativo do Django (`AbstractBaseUser`, `authenticate()`,
> `login()`, `logout()`, `request.user`, `@login_required`).

### 16. Por que a autenticação começou manual em vez de usar `django.contrib.auth` desde o início?

A tabela `usuario` foi desenhada num DER próprio do projeto (`docs/der.md`),
com colunas específicas (`id_usuario, nome, email, senha_hash, perfil,
ativo, criado_em`) — diferentes das colunas que o `User` padrão do Django
espera (`username, password, is_staff, is_superuser, ...`). Configurar
`AUTH_USER_MODEL` pra um model customizado precisa ser feito antes da
primeira migration da app; como a `0001_initial` já tinha sido aplicada com
`Usuario` como `models.Model` comum, a equipe optou por reimplementar
login/sessão/permissão na mão (reaproveitando só `check_password`/
`make_password`/`validate_password` do próprio Django) em vez de reestruturar
o schema logo cedo.

### 17. Se dava mais trabalho reimplementar, por que migrar pro nativo depois, em vez de deixar como estava?

A implementação manual tinha uma falha de segurança concreta: o login não
regenerava a *session key* (`request.session.cycle_key()`), o que deixa a
aplicação vulnerável a *session fixation* — se um atacante já soubesse a
session key de um navegador antes do login (ex.: setando um cookie via XSS
ou link malicioso), essa mesma key continuava válida depois do usuário se
autenticar. `django.contrib.auth.login()` resolve isso automaticamente. Além
disso, a versão manual reimplementava (e precisava manter testado) código
que o framework já mantém: verificação de usuário inativo, timing-safe
comparison, etc. — superfície de bugs desnecessária.

### 18. Como o `Usuario` continua batendo com o DER se agora ele herda de `AbstractBaseUser`?

`AbstractBaseUser` normalmente adiciona dois campos: `password` e
`last_login`. Em `core/models.py`, o model declara o próprio campo
`password` de novo — mas com `db_column="senha_hash"`:

```python
password = models.CharField(max_length=255, db_column="senha_hash")
```

Isso separa duas coisas que parecem uma só: o **nome Python** do campo
(`password`, o que o Django espera internamente em vários lugares — pergunta
19) e o **nome da coluna** no banco (`senha_hash`, o que está documentado no
DER). `db_column` deixa escolher os dois separadamente. Resultado: nenhuma
coluna nova foi criada nem renomeada de verdade — confirmado rodando
`python manage.py makemigrations` (Django detecta a troca de nome do campo e
pede confirmação de rename) e depois `python manage.py sqlmigrate core
0002`, que mostra `(no-op)` nas duas operações: é só o Django atualizando o
que ele *pensa* que o model se chama, sem tocar em SQL.

### 19. Por que não bastou marcar `password = None` e reimplementar `set_password`/`check_password` na mão? O que deu errado?

Foi a primeira tentativa, e pareceu funcionar — os testes automatizados
passavam. Só que ela reintroduzia exatamente o problema que a migração pra
auth nativo tinha acabado de resolver: código próprio reimplementando peças
do framework, e cada peça reimplementada é uma chance de esquecer alguma
outra peça que depende dela por baixo dos panos. Apareceram três bugs reais
depois de testar manualmente (não pelos testes automatizados — nenhum
cobria esses caminhos):

1. **`manage.py createsuperuser` criava conta com senha inutilizável, em
   silêncio.** O comando nativo do Django só coleta senha se
   `UserModel._meta.get_field("password")` existir. Como o campo tinha sido
   renomeado pra `senha_hash` (sem `password` nenhum), o comando pulava toda
   a lógica de senha — `user_data` nunca ganhava a chave `"password"` — e
   `UsuarioManager.create_superuser` acabava chamando `set_password(None)`.
   O comando dizia "Superuser created successfully" e a conta não conseguia
   fazer login.
2. **`has_usable_password()` sempre retornava `True`**, mesmo pra essa conta
   quebrada. `set_password`/`check_password`/`get_session_auth_hash` tinham
   sido sobrescritos, mas não `has_usable_password()`/
   `set_unusable_password()` — esses continuavam olhando pra `self.password`
   (o atributo de classe `None` que sobrou da remoção do campo), e
   `is_password_usable(None)` é `True` por definição no Django.
3. **`/admin/` quebrava com 500** pra qualquer usuário autenticado.
   `django.contrib.admin.sites.AdminSite.has_permission()` checa
   `request.user.is_staff` — atributo que não existia no model.

O padrão por trás dos três: o nome `password` não é só uma convenção de
estilo do Django, é um contrato implícito que várias partes do framework
assumem existir (o comando `createsuperuser`, os métodos herdados de
`AbstractBaseUser`, os forms de admin). Renomear o campo quebra esse
contrato em pontos que só aparecem ao usar cada funcionalidade — não ao
rodar a suíte de testes do projeto, que nunca exercitava `createsuperuser`
nem `/admin/`. A correção (pergunta 18, `db_column`) resolve isso na raiz:
em vez de quebrar o contrato e caçar cada lugar que dependia dele, o campo
continua se chamando `password` de verdade — só a coluna física é que tem
outro nome.

### 20. E o `last_login`? Removê-lo não quebra nada no Django?

Quebraria, se nada mais fosse feito: o Django conecta por padrão um
receptor do sinal `user_logged_in` (`update_last_login`) que tenta gravar a
hora do login nesse campo. Sem o campo, essa gravação geraria erro. Por
isso `core/apps.py` desconecta esse receptor especificamente
(`user_logged_in.disconnect(dispatch_uid="update_last_login")`) no
`ready()` da app — um "opt-out" explícito e documentado, não um
comportamento quebrado silenciosamente. Esse campo não tem um `db_column`
pra salvar (como `password` tem) porque, ao contrário de `password`, nada
crítico do framework quebra por ele simplesmente não existir — só esse um
sinal, que já é tratado.

### 21. Por que `Usuario` não usa `PermissionsMixin` (o sistema de `Group`/`Permission` do Django)?

Porque o controle de acesso do projeto é binário (`perfil`:
administrador/voluntário) e já é resolvido de forma simples pelo decorator
`admin_obrigatorio`. `PermissionsMixin` adicionaria um campo `is_superuser`
e duas tabelas de relação (`groups`, `user_permissions`) que não existem no
DER, pra resolver um problema (permissões granulares, múltiplos grupos)
que o projeto não tem hoje. Essa decisão ficou ainda mais clara depois do
bug do `/admin/` (pergunta 19, item 3): a tentação de "consertar" aquele 500
ligando `is_staff` ao `perfil` foi testada e só trocou um `AttributeError`
por outro (`has_module_perms`, que também vem do `PermissionsMixin`) — ver
pergunta 24.

### 22. `login_obrigatorio` e `admin_obrigatorio` ainda existem depois da migração? Por quê?

Sim, os dois continuam em `core/decorators.py`, mas com papéis diferentes
agora:
- `login_obrigatorio` virou um wrapper fino em cima do `login_required`
  nativo do Django — sem lógica própria, só centraliza os argumentos
  (`login_url="login"`, `redirect_field_name=None`) num lugar só, em vez de
  repeti-los em cada view.
- `admin_obrigatorio` continua com lógica própria de verdade — checa
  `request.user.perfil`, algo que o Django não resolve nativamente sem
  `PermissionsMixin` (pergunta 21).

### 23. O que muda, na prática, se a senha de um usuário for alterada enquanto ele está logado em outro navegador?

Com o sistema nativo, a sessão antiga é invalidada automaticamente na
próxima requisição: o Django guarda um hash da senha (via
`get_session_auth_hash()`, herdado de `AbstractBaseUser` sem nenhuma
sobrescrita — funciona porque `self.password` agora é um campo de verdade,
ver pergunta 18) dentro da própria sessão no momento do login, e o
`AuthenticationMiddleware` compara esse hash a cada requisição. Se a senha
mudou, o hash não bate mais, a sessão é descartada e o usuário vira
anônimo. Isso não existia na implementação manual — é um ganho de
segurança que veio "de graça" ao adotar o framework.

### 24. Por que `/admin/` fica sempre inacessível, mesmo pra quem roda `createsuperuser`?

`Usuario.is_staff` é uma property fixa em `False` (`core/models.py`), de
propósito. A primeira tentativa foi ligar `is_staff` a
`perfil == ADMINISTRADOR`, mas isso só adiou o problema: `/admin/` não tem
nenhum model do projeto registrado (não existe `core/admin.py`), só que
`django.contrib.auth` registra o model `Group` sozinho, sem pedir
permissão, assim que a app `django.contrib.admin` faz autodiscovery. A
página inicial do admin então tenta checar
`request.user.has_module_perms("auth")` pra decidir se mostra esse `Group`
— método que só existe com `PermissionsMixin` (pergunta 21), que
deliberadamente não foi adotado. Resultado: trocar `is_staff` fixo por
`perfil == ADMINISTRADOR` trocava um 500 (`is_staff` inexistente) por outro
(`has_module_perms` inexistente). Manter `is_staff` sempre `False` resolve
de vez: ninguém passa da primeira checagem (`has_permission`), `/admin/`
volta a ser uma rota morta e inofensiva pra qualquer usuário — exatamente o
comportamento de antes da migração, só que agora sem o 500. Por isso
`UsuarioManager.create_superuser` tem um comentário deixando explícito que
ele dá `perfil=ADMINISTRADOR` (acesso a `/usuarios/` dentro do próprio
sistema), não acesso ao `/admin/` do Django — o nome do comando
(`createsuperuser`) é do framework e sugere isso, mas não é o que acontece
neste projeto.

### 25. Como validar que essa migração não quebrou nada nem mudou o schema do banco?

Quatro evidências, nessa ordem: (1) `python manage.py makemigrations
--check` não detecta nenhuma migration pendente — prova de que o conjunto
de colunas da tabela `usuario` é idêntico ao de antes; (2) a suíte de
testes completa (`python manage.py test core`) passa (26/26), incluindo os
testes que cobrem usuário inativo perdendo acesso em sessão já aberta e
checagem de permissão de admin; (3) testes manuais via HTTP real (`curl`,
com cookies de sessão) percorrendo login → página protegida → área de admin
→ logout → bloqueio pós-logout, contra o banco com os dados reais do
comando `seed`; (4) reprodução manual e direcionada dos três bugs da
pergunta 19 — cada um só aparece rodando o comando/rota específico
(`createsuperuser --noinput`, `has_usable_password()`, uma visita
autenticada a `/admin/`), não a suíte de testes padrão. É um lembrete de
que "os testes passam" não é sinônimo de "nada quebrou": os testes cobrem o
que alguém pensou em testar.

---

## Rastreabilidade (a pergunta que fecha tudo)

### 26. Aponte, história por história, qual critério de aceite cada teste cobre.

**História #1 — Login com e-mail e senha**

| Critério de aceite (backlog) | Coberto por | Onde |
|---|---|---|
| Login com credenciais válidas redireciona para o painel | `test_login_valido_redireciona_para_painel` | `core/tests.py` |
| Credenciais inválidas exibem mensagem de erro sem revelar qual campo está errado | `test_login_invalido_mostra_erro_generico_e_nao_autentica` + `authenticate()` retornando `None` uniforme | `core/tests.py`, `core/views.py` |
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
