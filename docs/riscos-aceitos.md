# Riscos aceitos

## zlib1g na imagem base (python:3.13-slim)

| Campo | Valor |
|---|---|
| CVEs | CVE-2026-76844, CVE-2026-85091 |
| Severidade | HIGH |
| Componente | zlib1g 1:1.3.dfsg+really1.3.1-1+b1 (Debian 13.7) |
| Correcao existente | 1:1.3.dfsg+really1.3.1-1+deb13u1 |
| Decisao | Aceitar temporariamente; aguardar a imagem base |
| Vencimento | 2026-12-13 (arquivo .trivyignore) |
| Condicao de saida | A base incorporar a versao corrigida; remover a excecao |

## Observacoes

- A decisao nao afirma que a aplicacao esta imune: nao foi analisado se a
  aplicacao chega a usar as funcoes afetadas do zlib.
- Apos o vencimento, o scan volta a bloquear a publicacao assinada.
- Alternativa descartada por ora: apt-get --only-upgrade zlib1g no
  Dockerfile (reduz a reprodutibilidade do build).
