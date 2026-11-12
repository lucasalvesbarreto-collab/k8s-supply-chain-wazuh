# k8s-supply-chain-wazuh

Cadeia de suprimento de software segura em Kubernetes, com detecção em
runtime integrada ao Wazuh e mapeada ao MITRE ATT&CK for Containers.

> Status: em andamento. Fase 0 (ambiente) concluída.

## Arquitetura planejada

Código -> GitHub Actions -> build da imagem
  -> SBOM (Syft), scan (Trivy/Grype), assinatura (Cosign)
  -> registry (GHCR) + proveniência SLSA
  -> cluster k3s com Kyverno (só imagem assinada, sem root, sem tag latest),
     NetworkPolicy default deny e Falco (runtime)
  -> alertas no Wazuh, com regras locais 1002xx

## Fases

| Fase | Tema | Status |
|---|---|---|
| 0 | Ambiente: k3s ao lado do Wazuh | Concluída |
| 1 | Pipeline com SBOM, assinatura e proveniência | Pendente |
| 2 | Admissão com Kyverno (teste positivo e negativo) | Pendente |
| 3 | IaC segura (Checkov/Trivy config no CI) | Pendente |
| 4 | Runtime: Falco + Wazuh, regras e playbook N1 | Pendente |

## Ambiente

- VM Ubuntu Server com 4 vCPUs e 7,2 GiB de RAM, rodando Wazuh (manager,
  indexer, dashboard) e k3s na mesma máquina.
- Tudo local e com ferramentas de código aberto, sem custo.

## Projeto anterior

Detecção mapeada ao ATT&CK: [wazuh-mitre-attack-lab](https://github.com/lucasalvesbarreto-collab/wazuh-mitre-attack-lab)

## Documentação

- [Jornada e problemas reais](docs/jornada.md)
