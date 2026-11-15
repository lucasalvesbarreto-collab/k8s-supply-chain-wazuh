# k8s-supply-chain-wazuh

Cadeia de suprimento de software segura em Kubernetes (k3s), com detecção em
runtime integrada ao Wazuh e mapeada ao MITRE ATT&CK for Containers.

> Status: em andamento. Fases 0 e 1 concluídas. Próxima: Fase 2 (admissão
> com Kyverno).

## O que a Fase 1 já prova

| Controle | Como foi provado |
|---|---|
| Actions fixadas por hash de commit | Todas as linhas `uses:` têm 40 caracteres hexadecimais; Dependabot propõe atualizações |
| SBOM (SPDX) da imagem | Gerado pelo Syft a cada build; guardado como artefato |
| Scan que bloqueia | Teste negativo (exceção vencida: build vermelho) e positivo (exceção válida: verde) |
| Scan detecta falhas de verdade | `requests==2.19.0` em branch de teste elevou o resultado de 0 para 7 |
| Assinatura sem chave (Cosign keyless) | Verificada de fora do pipeline, na VM, com identidade do workflow |
| Assinatura presa à branch de origem | Imagem da branch de teste foi recusada ao exigir a identidade da `main` |
| Proveniência SLSA (Build Level 2) | `cosign verify-attestation` mostra imagem, workflow, referência e commit exato |

Detalhes dos problemas reais e das decisões: [docs/jornada.md](docs/jornada.md).
O que este projeto **não** garante: [docs/limitacoes.md](docs/limitacoes.md).

## Fluxo do pipeline
