## Guia de Commits (Conventional Commits)

Para manter o histórico limpo e legível, use o padrão Conventional Commits.

### Formato
`tipo(escopo)!: descrição curta`

- tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- escopo (opcional): área afetada, ex.: `frontend/auth`, `backend/api`, `ml/model`, `database/migrations`
- `!` indica breaking change

### Regras
- Assunto (primeira linha) no imperativo e sem ponto final.
- Até ~72 caracteres recomendados (máximo 100 no validador).
- Linha em branco após o assunto; depois explique o “porquê”, não só o “o quê”.
- Referencie issues quando aplicável: `Refs #123` ou `Fixes #456`.
- Para breaking changes, inclua no corpo: `BREAKING CHANGE: descrição do impacto e migração`.

### Exemplos
- `feat(frontend/auth): adiciona fluxo de login com token`
- `fix(backend/api): trata 401 quando token expira`
- `refactor(ml/model): isola pipeline de features`
- `chore(ci): adiciona cache no workflow do npm`
- `perf(frontend/charts): reduz custo do re-render`

### Branches
- `feat/<area>-<descricao-curta>`
- `fix/<area>-<descricao-curta>`
- Exemplos: `feat/frontend-auth-login`, `fix/backend-churn-predict-null`

### Commits atômicos
- Quebre mudanças grandes em commits pequenos e coesos.
- Rode linters/tests localmente quando aplicável.

### Validação automática (hook local)
Há um script em `scripts/git-hooks/commit-msg` que valida o formato do assunto.

Para ativar manualmente:
1. Copie o hook: `cp scripts/git-hooks/commit-msg .git/hooks/commit-msg` (Windows Git Bash) ou `copy scripts\git-hooks\commit-msg .git\hooks\commit-msg` (PowerShell).
2. Opcional: configure o template de commit: `git config commit.template .gitmessage.txt`.

Se preferir, peça para o Codex aplicar isso automaticamente.

