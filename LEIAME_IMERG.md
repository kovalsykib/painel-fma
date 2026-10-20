# Teste de acesso ao IMERG (NASA) - passo a passo

Este teste só verifica se o GitHub consegue acessar o IMERG e quanto tempo leva ler os dados. Ele não muda o painel.

## Parte 1: conta da NASA (uma vez)
1. Entre em https://urs.earthdata.nasa.gov e clique em **Register** para criar uma conta gratuita do Earthdata. Use uma senha que você não use em outros lugares (ela ficará guardada no GitHub como segredo).
2. Entre na sua conta e vá em **Applications > Authorized Apps** (aplicativos autorizados). Clique em **Approve More Applications**, procure **NASA GESDISC DATA ARCHIVE** e aprove. Sem isso o login funciona, mas o download é recusado. (Se o nome estiver um pouco diferente na tela, procure por "GES DISC".)

## Parte 2: guardar o login no GitHub (uma vez)
1. No seu repositório, vá em **Settings > Secrets and variables > Actions > New repository secret**.
2. Crie o segredo `EARTHDATA_USERNAME` com o seu usuário do Earthdata.
3. Crie o segredo `EARTHDATA_PASSWORD` com a sua senha do Earthdata.

## Parte 3: colocar os arquivos e rodar
1. Em **Add file > Upload files**, envie o arquivo `testar_imerg.py` (fica na raiz do repositório, junto com os outros .py).
2. Em **Add file > Create new file**, digite no nome `.github/workflows/testar-imerg.yml`, cole o conteúdo do arquivo `testar-imerg.yml` deste pacote e clique em **Commit changes**.
3. Vá em **Actions > Testar IMERG (NASA) > Run workflow**. Leva alguns minutos.
4. Quando terminar, abra o arquivo `imerg/teste_acesso.md` no repositório e **cole o conteúdo na conversa**. Se der erro, ele traz a mensagem do erro, e isso já ajuda.

## O que o teste responde
- O GitHub consegue listar os arquivos do IMERG (Early, Late e Final)?
- O login funciona?
- Dá para ler a chuva de um ponto (Seropédica) sem baixar o arquivo global? Quanto tempo leva por arquivo?
- Quantas horas depois da chuva o dado aparece? (decide se serve para o painel diário)
