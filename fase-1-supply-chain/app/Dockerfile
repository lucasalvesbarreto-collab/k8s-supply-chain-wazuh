# ---------- Estágio 1: instala dependências ----------
FROM python:3.13-slim AS build
WORKDIR /build
COPY requirements.txt .
# --prefix=/install isola os pacotes instalados em uma pasta,
# que copiaremos para a imagem final.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Estágio 2: imagem final, enxuta ----------
FROM python:3.13-slim
# UID numérico fixo: o Kyverno (runAsNonRoot) consegue verificar um número,
# mas não consegue verificar um nome de usuário.
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
# Remove o pip da imagem final: a aplicacao nao o usa em execucao, e as
# bibliotecas embutidas nele (msgpack, urllib3, setuptools) geravam 5 CVEs.
RUN pip uninstall -y pip
COPY --from=build /install /usr/local
WORKDIR /app
COPY app.py .
USER 10001
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
