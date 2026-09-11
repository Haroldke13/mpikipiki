# syntax=docker/dockerfile:1
###############################################################################
# mpikipiki — Flask + MongoDB ride-hailing prototype
#
# Build:  docker build -t mpikipiki:latest .
# Run:    see DEPLOY.md
#
# Two things to know before you build:
#   * requirements.txt in this repo was GENERATED from the imports; it did not
#     exist before.
#   * `python app.py` does not work (relative import). The entrypoint is the
#     factory, reached here via deploy_wsgi.py.
###############################################################################

FROM python:3.12.3-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install -r requirements.txt

FROM python:3.12.3-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=5759

COPY --from=builder /opt/venv /opt/venv

RUN useradd --system --create-home --uid 10003 --shell /usr/sbin/nologin appuser

WORKDIR /app
COPY --chown=root:root . /app

USER appuser

EXPOSE 5759

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5759/healthz', timeout=4).status == 200 else 1)"

# Nothing is written to disk by this app; all state is in MongoDB.
# Safe to run with --read-only (plus a tmpfs on /tmp).
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5759", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "60", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "deploy_wsgi:app"]
