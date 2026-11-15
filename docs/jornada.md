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

### 14. Causa confirmada: Trivy nao identifica o SO pelo SBOM
- Log: "Detected OS family=none" e "Unsupported os family=none".
- Efeito: os 87 pacotes deb do SBOM foram ignorados; so o alvo Python
  foi escaneado.
- Decisao: adicionar scan da IMAGEM (le o /etc/os-release da propria
  imagem) e manter o SBOM como evidencia de inventario.

### 15. Scan da imagem cobre o Debian e acha mais que o scan do SBOM
- Scan da imagem: "Detected OS family=debian version=13.7", pkg_num=87
  (igual aos 87 pkg:deb do SBOM).
- Resultado no mesmo build: debian = 2 vulnerabilidades, Python = 5
  (HIGH/CRITICAL com correcao disponivel).
- Scan do SBOM no mesmo build: apenas Python, com 0.
- Conclusao: o scan do SBOM sozinho subestima o risco; o scan da imagem
  passa a ser o que decide o bloqueio. O SBOM continua como inventario.
- Pendente: identificar os 7 CVEs e a origem dos 5 do alvo Python.

### 16. Origem dos achados do scan da imagem
- Debian: 2 CVEs HIGH em zlib1g (heap buffer overflow). Correcao existe no
  Debian (1:1.3.dfsg+really1.3.1-1+deb13u1). Decisao: nao alterar o
  Dockerfile; reconstruir a imagem e esperar a base atualizada.
- Python: msgpack e urllib3 NAO estao instalados (pip list limpo); estao
  em pip/_vendor (copias embutidas no proprio pip). Nao pertencem ao
  codigo da aplicacao.
- setuptools 70.3.0: sem pasta encontrada por nome; hipotese de que vem
  de pip/_vendor/vendor.txt, ainda a confirmar.
- Licao: o pip list nao enxerga bibliotecas embutidas; o scan da imagem
  enxerga.

### 17. Achados do Python vem do vendor.txt do pip
- vendor.txt do pip 26.2.2 lista msgpack==1.1.2, setuptools==70.3.0 e
  urllib3==2.7.0: exatamente as 3 bibliotecas com os 5 CVEs.
- Origem: copias embutidas no proprio pip, nao no codigo da aplicacao.
- zlib1g: o rebuild nao trouxe correcao; a base ainda tem a versao
  vulneravel (debian 13.7).
- Decisao: remover o pip da imagem final (RUN pip uninstall -y pip), pois
  a aplicacao nao o usa em execucao. Efeito esperado: Python = 0.

### 18. Scan da imagem passa a bloquear, com excecao temporaria
- Politica: Trivy (scan da imagem) com exit-code 1 para HIGH/CRITICAL com
  correcao; excecao do zlib1g em .trivyignore com vencimento 2026-12-13.
- Teste negativo: excecao com data vencida (2026-11-01) deixou o build
  vermelho; o scan bloqueia e a excecao vencida nao esconde falha.
- Teste positivo: mesma excecao com data valida deixou o build verde
  (Debian: 0, suprimido; nao corrigido).
- Registro: docs/riscos-aceitos.md (motivo, vencimento, condicao de saida).
- Limite assumido: nao foi analisado se a aplicacao usa as funcoes
  afetadas do zlib; a decisao e de aguardar a base, nao de negar o risco.

### 19. Assinatura keyless com Cosign em job separado
- Job "assinar" (needs: build): so roda se o build e o scan bloqueante
  passarem; unico job com id-token: write (menor privilegio).
- Assinatura pelo digest, nao pela tag. Cosign fixado em v3.1.4 (acima de
  3.0.6, que corrige avisos conhecidos); cosign-installer v4.1.3 por hash,
  pois a v3.x do instalador nao instala o Cosign 3.
- Verificacao no proprio job com certificate-identity (workflow +
  referencia da branch) e certificate-oidc-issuer do GitHub: verde.
- Testado primeiro em branch (feat/assinatura) antes de ir para a main.

### 20. Verificacao externa da assinatura (VM)
- cosign v3.1.4 baixado na VM, com sha256 conferido (cosign-linux-amd64: OK).
  Limite: a soma vem do mesmo local do binario; detecta corrupcao, nao uma
  release comprometida.
- Teste 1 (main + identidade da main): sucesso, saida 0.
- Teste 2 (identidade errada): falha, saida 1.
- Teste 3 (imagem da branch feat/assinatura + identidade da main): falha,
  saida 1. O erro mostra SAN esperado vs. obtido: a assinatura fica presa
  a branch de origem.
- Pendente: confirmar se o Kyverno le o formato de assinatura do Cosign 3.

### 21. Proveniencia SLSA com attest-build-provenance
- Passo no job "assinar" (unico com id-token: write e attestations: write).
  Action v4.2.2 fixada por hash; internamente chama actions/attest, tambem
  fixada por hash pelo autor (fora do nosso controle).
- Atestacao do tipo Build Provenance, assinada com certificado do Sigstore
  Public Good, registrada no Rekor e guardada no repositorio e no GHCR.
- Verificacao externa (VM) com cosign verify-attestation: sucesso, saida 0.
  Conteudo: imagem (digest), workflow build.yml, ref da branch e commit
  exato; o gitCommit bate com o commit enviado pelo git push.
- Teste negativo (identidade da main contra imagem da branch): falha,
  saida 1, mostrando SAN esperado vs. obtido.
- Nivel afirmado: SLSA v1.0 Build Level 2 (so a atestacao). Level 3 exigiria
  workflow reutilizavel; nao e afirmado.
- Incidente: git pull falhou por autenticacao; o credential cache expira
  em 1 hora (timeout=3600), e o git voltou a pedir o token.
