# Promo Groups

Base para uma operacao de promocoes de parceiros e afiliados. O sistema organiza
produtos promocionais, links afiliados, grupos de distribuicao e lotes de publicacao
para canais como WhatsApp e Telegram.

O objetivo inicial e oferecer um fluxo manual, rastreavel e revisavel: a equipe
prepara a promocao, confere seus dados e gera o material para distribuicao. As
integracoes de envio e APIs oficiais serao adicionadas em etapas posteriores.

## O que ja esta disponivel

- Cadastro de parceiros, incluindo dominios permitidos e um modelo opcional para
  URL afiliada.
- Cadastro de promocoes com URL original, URL afiliada, imagem, precos, descricao,
  origem e status.
- Modelos de mensagem para WhatsApp e Telegram, gerais ou especificos por parceiro.
- Cadastro de grupos de distribuicao para WhatsApp e Telegram.
- Lotes de distribuicao com varios destinos e estado individual por grupo, preparados
  para futuras tentativas, falhas e automacao de entrega.
- Interface operacional web autenticada com dashboard, CRUD de promocoes, grupos,
  lotes/mensagens enviadas, modelos de mensagem e fluxo de criacao rapida.
- Validacoes para impedir que uma promocao sem URL afiliada seja marcada como revisada
  ou agendada, e que um lote seja agendado sem uma promocao revisada e uma mensagem
  congelada.
- Execucao em containers com Django, MySQL, Gunicorn, Nginx, TLS e Certbot.

## Fluxo operacional inicial

A interface web principal agora fica na raiz (`/`) e exige autenticacao. Depois de
criar um superusuario, acesse `/login/` e siga este fluxo:

1. Consulte o dashboard para acompanhar status de promocoes, lotes e destinos com
	falha.
2. Use `Promocoes` para cadastrar/revisar ofertas e controlar status.
3. Use `Grupos` para manter canais de destino por plataforma.
4. Use `Mensagens/Lotes` para acompanhar historico de envios por destino
	(`BatchTarget`), com status individual.
5. Use `Modelos de mensagem` para manter textos por parceiro/canal.
6. Use `Criacao rapida` para abrir promocao e lote inicial em um unico fluxo.

O Admin Django segue disponivel em `/admin/` como apoio administrativo. Se preferir o
fluxo original por Admin, voce pode continuar com:

1. Cadastre um parceiro, por exemplo Amazon, AliExpress, Mercado Livre ou Shopee,
	informando os dominios que ele aceita.
2. Cadastre uma promocao com o link original, titulo, preco e imagem. Informe a URL
	afiliada que foi gerada pelo programa de afiliados ou use uma regra configurada
	para o parceiro quando ela existir.
3. Revise os dados e altere o status da promocao para `Revisada`. Uma promocao nesse
	estado precisa possuir URL afiliada.
4. Crie modelos de mensagem para WhatsApp ou Telegram com os campos disponiveis:
	`{title}`, `{current_price}`, `{previous_price}`, `{description}` e
	`{affiliate_url}`.
5. Cadastre os grupos de destino e crie um lote de distribuicao. Adicione um destino
	ao lote para cada grupo selecionado e guarde a mensagem final em `mensagem
	congelada` antes de agendar.

Cada destino possui seu proprio status. Essa separacao permite que a automacao futura
registre entregas e retentativas sem alterar a estrutura central do sistema.

## Arquitetura

| Componente | Responsabilidade |
| --- | --- |
| Django 4.2 | Aplicacao, Admin e regras de dominio |
| MySQL 8 | Persistencia de parceiros, promocoes e distribuicao |
| Gunicorn | Servidor WSGI da aplicacao |
| Nginx | Proxy reverso, arquivos estaticos/media e terminacao TLS |
| Certbot | Emissao e renovacao de certificados Let's Encrypt |
| Docker Compose | Orquestracao dos servicos |

Os apps de dominio sao:

- `promotions`: parceiros, promocoes e modelos de mensagem.
- `distribution`: grupos, lotes e destinos individuais de distribuicao.

## Inicio rapido

Copie as variaveis de ambiente e ajuste os valores apropriados para seu ambiente:

```bash
copy .env.example .env
```

Para desenvolvimento local, defina `DEBUG=True` e ajuste `ALLOWED_HOSTS` no `.env`.
Em producao, mantenha `DEBUG=False`, use um `SECRET_KEY` forte e informe o dominio
publico em `DOMAIN`, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`.

Inicie os containers:

```bash
docker compose up -d --build
```

Crie o usuario administrador:

```bash
docker compose exec web python manage.py createsuperuser
```

As migracoes e a coleta de arquivos estaticos sao executadas automaticamente durante
o inicio do servico `web`. Para instrucoes de HTTPS, Certbot, renovacao de certificados
e configuracao detalhada, consulte [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md).

## Comandos frequentes

```bash
# Logs da aplicacao
docker compose logs -f web

# Aplicar migracoes manualmente
docker compose exec web python manage.py migrate

# Executar validacoes do Django
docker compose exec web python manage.py check

# Parar os servicos
docker compose down
```

## Limites atuais

Esta base ainda nao realiza envio automatico nem possui integracoes com APIs de
Amazon, AliExpress, Mercado Livre, Shopee, WhatsApp ou Telegram. Ela tambem nao gera
um link afiliado valido de forma universal: a URL afiliada deve ser informada pela
equipe ou criada a partir de uma regra conhecida e configurada para o parceiro.

Extracao de dados por URL, pre-visualizacao de mensagens, encurtamento de links,
rastreio de cliques, conciliacao de comissoes, painel operacional customizado e
automacao de publicacao ainda nao foram implementados.

## Proximos incrementos

1. Validar dominios e gerar URLs afiliadas por regras especificas de cada parceiro.
2. Pre-preencher promocoes a partir de metadados publicos de URL, sempre com revisao
	humana obrigatoria.
3. Compor e pre-visualizar mensagens para WhatsApp e Telegram, armazenando o texto
	definitivo no lote.
4. Adicionar testes para regras de links, transicoes de status, mensagens e lotes.
5. Integrar canais de distribuicao por APIs oficiais ou provedores homologados.

## Seguranca

Em producao, exponha somente as portas 80 e 443 pelo Nginx. O Gunicorn e o MySQL
devem permanecer na rede interna do Docker. O Nginx aceita TLS 1.2 e 1.3 com cifras
modernas, enquanto o Django aplica redirecionamento HTTPS e cookies seguros quando
`DEBUG=False`.
