
# Whisper Worker + API

Pipeline assíncrono de transcrição de áudio utilizando Whisper.

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Como Usar](#como-usar)
- [Fluxo de Funcionamento](#fluxo-de-funcionamento)
- [Contato para Desenvolvedores](#contato-para-desenvolvedores)
- [Contribuidores](#contribuidores)

---

## Sobre o Projeto

Este projeto implementa um pipeline assíncrono para transcrição de áudios usando o modelo Whisper. Ele recebe arquivos de áudio, processa a transcrição e envia o resultado para uma API principal.

---

## Estrutura do Projeto

```
python/
  api.py           # API para recebimento dos áudios
  worker.py        # Worker responsável pela transcrição
var/
  audio/{domain}/{id}.ext   # Áudios recebidos
  transcripted/{id}.json    # Transcrições geradas
.env                # Variáveis de ambiente
requirements.txt    # Dependências Python
deploy/             # systemd + nginx (w.controleonline.com)
start.sh            # Script de inicialização
```

---

## Instalação

```bash
python3 -m venv venv
venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # CPU only
venv/bin/pip install -r requirements.txt
sudo apt-get install -y ffmpeg
cp .env.sample .env && chmod 600 .env   # edite os segredos
```

### Produção (w.controleonline.com)

- Usuário próprio `whisper` (home `/home/whisper`, `chmod 700`); código em `/home/whisper/api-whisper`, link em `/var/www/api-whisper`.
- `deploy/whisper-api.service` e `deploy/whisper-worker.service` → `/etc/systemd/system/` (rodam só como `whisper`, com limite de memória/CPU).
- `deploy/w.controleonline.com.conf` → nginx (proxy para `127.0.0.1:8090`) + `certbot --nginx -d w.controleonline.com`.

---

## Configuração

Veja `.env.sample`:

| Variável | Uso |
|---|---|
| `WHISPER_TOKEN` | segredo exigido no header `X-Whisper-Token` do `POST /transcrip` |
| `API_ENDPOINT` | endpoint da API principal que recebe `{id, domain, text}` |
| `API_TOKEN` | segredo enviado no header `X-Whisper-Token` do callback |
| `WHISPER_MODEL` | modelo (`tiny`, `base`, `small`…) — padrão `base` |
| `WHISPER_IDLE_UNLOAD` | segundos ociosos até liberar o modelo da memória |
| `MAX_UPLOAD_MB` | tamanho máximo do áudio |

---

## Como Usar

```bash
./start.sh   # desenvolvimento; em produção use os serviços systemd
```

**POST** `/transcrip` (multipart) — header `X-Whisper-Token` obrigatório.

- `domain`: domínio do app (letras, números, `.`, `:`, `-`)
- `id`: identificador (letras, números, `_`, `-`)
- `audio`: arquivo (`webm`, `ogg`, `opus`, `mp3`, `m4a`, `mp4`, `aac`, `wav`, `amr`, `3gp`)

**GET** `/health` → `{"status": "ok"}`

---

## Fluxo de Funcionamento

1. A API valida o token e grava o áudio em `var/audio/{domain}/{id}.{ext}` (gravação atômica).
2. O worker carrega o modelo só quando há trabalho e transcreve.
3. O resultado vai para `var/transcripted/{id}.json`.
4. O JSON é enviado para `API_ENDPOINT` com `X-Whisper-Token` e `App-Domain`; se falhar, é reenviado depois.
5. Em caso de sucesso, o áudio e o JSON são removidos. O modelo é liberado após o período ocioso.

---

## Contato para Desenvolvedores

<a href="https://chat.whatsapp.com/KtplmnuqcXK9nIETLcYBGt" target="_blank">
  <img src="https://static.whatsapp.net/rsrc.php/yZ/r/JvsnINJ2CZv.svg" width="32" /> Grupo WhatsApp
</a>

---

## Contribuidores

<a href="https://github.com/ControleOnline/api-whisper/graphs/contributors" target="_blank">
  <img src="https://contrib.rocks/image?repo=ControleOnline/api-whisper" />
</a>
