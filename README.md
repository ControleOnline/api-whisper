
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
start.sh            # Script de inicialização
```

---

## Instalação

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
API_ENDPOINT=https://sua-api.com/api/transcription
API_TOKEN=seu_token
```

---

## Como Usar

Para iniciar o pipeline:

```bash
./start.sh
```

---

## Endpoint Disponível

**POST** `/transcrip`

Campos do formulário:

- `domain` (string)
- `id` (string)
- `audio` (arquivo)

---

## Fluxo de Funcionamento

1. A API recebe o arquivo de áudio via endpoint.
2. O áudio é salvo em `var/audio/in/{domain}`.
3. O worker processa a transcrição usando Whisper.
4. O resultado é salvo em `var/transcripted/{id}.json`.
5. O JSON é enviado para a API principal.
6. Em caso de sucesso, o áudio e o JSON são removidos.

---

## Contato para Desenvolvedores

<a href="https://chat.whatsapp.com/KtplmnuqcXK9nIETLcYBGt" target="_blank">
  <img src="https://static.whatsapp.net/rsrc.php/yZ/r/JvsnINJ2CZv.svg" width="32" /> Grupo WhatsApp
</a>

---

## Contribuidores

<a href="https://github.com/ControleOnline/api-community/graphs/contributors" target="_blank">
  <img src="https://contrib.rocks/image?repo=ControleOnline/api-community" />
</a>
