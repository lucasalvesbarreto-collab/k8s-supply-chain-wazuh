# Limitações assumidas

Este documento lista o que o projeto **não** garante, para ninguém ler mais
do que está provado.

## Do pipeline

- **SLSA Build Level 2, não 3.** A atestação sozinha dá o Level 2. O Level 3
  exigiria workflow reutilizável, que não foi implementado.
- **A imagem é publicada antes do scan.** Uma imagem reprovada fica no
  registro, sem assinatura. A proteção é a assinatura (e a admissão na Fase 2),
  não a ausência da imagem.
- **Branch `main` sem proteção configurada.** Quem consegue rodar o workflow
  em outra branch gera uma assinatura válida para aquela branch. A política
  da Fase 2 precisa fixar `refs/heads/main`.
- **Ações de terceiros têm dependências próprias.** A `attest-build-provenance`
  chama outra action por dentro (fixada por hash pelo autor, fora do nosso
  controle).
- **Atualizações do Dependabot** não são mescladas sem testar o build: o
  workflow "Validar" só confere sintaxe.

## Do scan

- **O scan do SBOM não enxerga o sistema operacional** (o Trivy não
  identificou a distro a partir do SPDX). Só o scan da imagem cobre o Debian.
- **`ignore-unfixed: true`** esconde falhas sem correção disponível.
- **Trivy 0.69.3** (versão que a action instala); havia versão mais nova.
- **Risco aceito: zlib1g** (CVE-2026-76844 e CVE-2026-85091), com vencimento
  em 2026-12-13. Não foi analisado se a aplicação usa as funções afetadas;
  a decisão é aguardar a imagem base, e não negar o risco.
- **Pacotes embutidos no `pip`** geravam 5 achados. Foram eliminados
  removendo o `pip` da imagem final, o que pressupõe que a aplicação não o
  usa em execução.

## Da verificação

- O binário do Cosign na VM foi conferido por soma SHA-256 vinda do mesmo
  local do arquivo: detecta corrupção, não uma release comprometida.
- O registro da assinatura no Rekor é **público** e expõe o nome do
  repositório e do workflow (aceitável para repositório público).
- **Pendente:** confirmar que a versão do Kyverno lê o formato de assinatura
  do Cosign 3 e as atestações guardadas pelo GitHub.

## Do ambiente

- Cluster de **um só nó**, na mesma VM do Wazuh, com 7,2 GiB de RAM.
- O cache de credenciais do Git expira (o token some da memória); o token é
  de escopo restrito ao repositório e tem validade.
- Fases 2, 3 e 4 ainda não foram implementadas.
