# Arquitetura da Fase 1

## Componentes

| Componente | Função | Versão fixada |
|---|---|---|
| GitHub Actions | Executa o pipeline | actions fixadas por hash |
| docker/build-push-action | Constrói e envia a imagem ao GHCR | v6 |
| anchore/sbom-action (Syft) | Gera o SBOM em SPDX | v0.24.3 |
| aquasecurity/trivy-action | Scan de vulnerabilidades | v0.35.0 |
| sigstore/cosign-installer + Cosign | Assinatura e verificação | installer v4.1.3, Cosign v3.1.4 |
| actions/attest-build-provenance | Proveniência SLSA | v4.2.2 |

## Dois jobs, permissões separadas

| Job | Permissões | Motivo |
|---|---|---|
| `build` | `contents: read`, `packages: write` | Constrói, escaneia e publica. Não pode assinar |
| `assinar` | `contents: read`, `packages: write`, `id-token: write`, `attestations: write` | Único com o direito de pedir identidade ao Sigstore |

`assinar` usa `needs: build`: se o scan bloquear, a imagem não é assinada.

## Decisões de confiança

- A imagem é identificada pelo **digest**, nunca pela tag.
- Assinatura **keyless**: não existe chave privada para vazar. A identidade
  é o caminho do workflow mais a referência da branch.
- A política de admissão (Fase 2) deve fixar `refs/heads/main`, para que uma
  imagem construída em branch de teste seja recusada.
- O scan decisivo é o da **imagem** (enxerga o sistema operacional). O scan
  do SBOM fica como relatório de inventário.
- Exceções de segurança ficam em `.trivyignore`, com data de vencimento, e
  são registradas em [riscos-aceitos.md](riscos-aceitos.md).

## Imagem de referência

- Digest do build da `main`: a preencher.
- Identidade esperada:
  `https://github.com/lucasalvesbarreto-collab/k8s-supply-chain-wazuh/.github/workflows/build.yml@refs/heads/main`
- Emissor: `https://token.actions.githubusercontent.com`
