# 📉 B3 Short Prospector

Dashboard para prospectar operações de Short (Venda a Descoberto) na B3.

---

## ✅ GUIA DE INSTALAÇÃO — PASSO A PASSO (sem precisar saber programar)

### PASSO 1 — Criar conta no GitHub (grátis)

1. Abra o site: https://github.com
2. Clique em **"Sign up"** (canto superior direito)
3. Digite seu e-mail, crie uma senha e um nome de usuário
4. Confirme seu e-mail (vai chegar uma mensagem)
5. Pronto, conta criada!

---

### PASSO 2 — Criar um repositório no GitHub

1. Após fazer login no GitHub, clique no botão verde **"New"** (canto superior esquerdo)
2. Em **"Repository name"** digite: `b3-short-dashboard`
3. Deixe marcado como **"Public"**
4. Clique em **"Create repository"**

---

### PASSO 3 — Fazer upload dos arquivos

1. Na página do repositório que acabou de criar, clique em **"uploading an existing file"**
2. Arraste os 2 arquivos desta pasta para a área indicada:
   - `app.py`
   - `requirements.txt`
3. Clique em **"Commit changes"** (botão verde no final da página)

---

### PASSO 4 — Criar conta no Streamlit Cloud (grátis)

1. Abra o site: https://share.streamlit.io
2. Clique em **"Sign up"**
3. Clique em **"Continue with GitHub"** (mais fácil — usa a conta que você acabou de criar)
4. Autorize a conexão

---

### PASSO 5 — Publicar o app

1. No Streamlit Cloud, clique em **"New app"**
2. Em **"Repository"**, selecione `b3-short-dashboard`
3. Em **"Branch"**, deixe `main`
4. Em **"Main file path"**, digite: `app.py`
5. Clique em **"Deploy!"**
6. Aguarde ~2 minutos enquanto o app é instalado automaticamente

---

### PASSO 6 — Acessar seu app

Após o deploy, você receberá um link no formato:
```
https://seu-usuario-b3-short-dashboard-app-xxxx.streamlit.app
```

**Salve esse link!** É o endereço permanente do seu dashboard.
Você pode abrir no celular, computador, em qualquer lugar.

---

## 🔄 Como atualizar os dados

Os dados se atualizam automaticamente a cada 15 minutos enquanto o app estiver aberto.
Para forçar uma atualização completa do ranking, clique no botão **"🔄 Atualizar Ranking"** na barra lateral.

---

## 📊 Como usar o Dashboard

### Aba "Análise do Ativo"
- Digite o código do ativo na barra lateral (ex: PETR4, VALE3, MGLU3)
- Escolha o período de análise
- Leia os sinais coloridos:
  - 🔴 **SHORT FORTE** = ativo muito sobrecomprado, bom candidato para short
  - 🟠 **SHORT MODERADO** = sinais de atenção, monitorar
  - ⚪ **AGUARDAR** = sem sinais claros no momento

### Aba "Ranking de Shorts"
- Lista automática dos 25 melhores candidatos para short da B3
- Ordenados pelo **Score Short** (quanto maior, melhor a oportunidade)
- Os 3 primeiros aparecem em destaque

---

## ⚠️ Aviso Legal

Este dashboard é apenas para fins informativos e educacionais.
Não constitui recomendação de investimento.
Dados fornecidos pelo Yahoo Finance com delay de ~15 minutos.
Operações de short envolvem risco elevado — consulte sempre um assessor financeiro.
