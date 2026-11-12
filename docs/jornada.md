# Jornada: problemas reais e decisões

## Fase 0: ambiente

### 1. Dimensionamento de memória: a primeira medição enganou
- Sintoma: o `top` mostrava o `wazuh-manager` com 194% de CPU.
- Causa: a captura foi feita 4 minutos após o boot, com o Wazuh ainda subindo.
- Correção: medir de novo com os serviços estáveis (~9 min).
- Resultado: Wazuh completo usa 2,7 GiB (estimativa inicial: 3 a 4 GiB).
- Lição: medir em regime estável antes de decidir arquitetura.

### 2. Decisão: k3s em vez de kind
- kind roda cada nó como container Docker (mais uma camada de memória).
- k3s usa o containerd embutido e consome menos.
- Custo medido do k3s: cerca de 0,6 GiB (used 2,7 -> 3,3 GiB).

### 3. Decisão preventiva: desligar Traefik e servicelb
- O Traefik padrão do k3s expõe as portas 80 e 443 no host.
- O dashboard do Wazuh já usa a 443, o que causaria conflito de portas.
- Instalação com `--disable traefik --disable servicelb`.
- Verificado: nenhum pod do Traefik em `kube-system`.

### 4. O kubectl do k3s ignorou o ~/.kube/config
- Sintoma: `permission denied` em /etc/rancher/k3s/k3s.yaml, mesmo após
  copiar o arquivo para ~/.kube/config.
- Causa: o atalho `kubectl` do k3s usa por padrão o arquivo do root; só
  respeita outro caminho se a variável KUBECONFIG apontar para ele.
- Correção: `export KUBECONFIG=$HOME/.kube/config`, gravada no ~/.bashrc.
- Segurança: arquivo com permissão 600 e dono do usuário (é uma chave de
  administrador do cluster); o .gitignore bloqueia o envio ao Git.

### 5. Pod helm-install-gateway-api-crd com status Completed
- Não é erro: é um Job que instala os CRDs da Gateway API e termina.

### 6. Pastas das fases fora do primeiro commit
- Sintoma: o commit inicial tinha 5 arquivos e só um .gitkeep.
- Causa: `touch fase-*/.gitkeep` usa um curinga, que só casa com arquivos
  que já existem. Como nenhum existia, o shell passou o texto literal ao
  touch, que falhou. O Git não registra pastas vazias.
- Correção: listar os quatro caminhos por extenso.
- Lição: curinga serve para encontrar, não para criar.

### 7. Workflow invalido: dois-pontos dentro do run
- Sintoma: "Invalid workflow file ... error in your yaml syntax on line 22".
- Causa: `run: yamllint -d "{extends: relaxed, ...}"` contem `: ` no meio do
  texto; o YAML interpreta isso como chave/valor e quebra a linha.
- Correcao: configuracao movida para o arquivo .yamllint, e o run ficou
  `yamllint .`, sem dois-pontos.
- Licao: validar o workflow localmente antes do push (yamllint no proprio
  arquivo) teria pego o erro.

### 8. Build falhou: pasta da aplicacao inexistente
- Sintoma: "unable to prepare context: path ./fase-1-supply-chain/app not found".
- Causa: os arquivos da aplicacao (app.py, Dockerfile, requirements.txt)
  nunca foram criados no repositorio; o workflow foi escrito antes de
  confirmar o resultado do passo anterior.
- Diagnostico: ls -la e git ls-files mostraram so o .gitkeep na fase-1.
- Licao: confirmar a saida de cada etapa antes de construir a seguinte.

### 9. Actions fixadas por hash de commit
- Motivo: tags (@v4) podem ser movidas pelo autor da action; o hash de
  commit nao. Risco real de cadeia de suprimento.
- Metodo: hash obtido com `git ls-remote` na tag (com ^{} para tags
  anotadas), gravado por script, com comentario `# vN`.
- Captura de tela cortada na borda esquerda truncou os hashes; por isso o
  script substitui a copia manual.
- Majors mais novos existem; foram mantidos os que ja passaram, e o
  Dependabot propoe as atualizacoes em PRs separados.

### 10. Ataque real a uma action: trivy-action
- A pagina de release do aquasecurity/trivy-action informa um ataque de
  cadeia de suprimento; as tags foram migradas para o prefixo "v".
- A release v0.35.0 e declarada duplicata nao comprometida e imutavel.
- Decisao: fixar v0.35.0 por hash (57a97c7...), conferido contra a pagina
  da release. A v0.36.0 existe, mas nao foi avaliada; fica para PR do
  Dependabot com revisao.
- Licao: e o ataque que o hash fixo previne; tag movel seria risco real.

### 11. Ordenacao de tags no git ls-remote
- Sintoma: tail mostrou versoes antigas (v0.9.2) como se fossem as novas.
- Causa: ls-remote ordena alfabeticamente (v0.10 antes de v0.4).
- Correcao: --sort=-v:refname ordena por versao.

### 13. Scan do SBOM so enxerga o alvo Python
- Sintoma: Trivy (scan-type sbom) mostrou apenas "Python / python-pkg: 0",
  embora o SBOM tenha 87 pacotes pkg:deb, 9 pkg:pypi, 1 pkg:oci.
- Conclusao parcial: o "0" vale para bibliotecas Python; o sistema
  operacional (Debian) NAO foi escaneado (legenda: '-' = Not scanned).
- Causa: ainda nao confirmada.
- Teste positivo: requests==2.19.0 em branch separada elevou o resultado
  de 0 para 7 vulnerabilidades, provando que o scan Python detecta falhas.
- Proximo passo: escanear o Debian (scan-type image) e medir a diferenca.
