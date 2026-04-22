# BoletoBuilderSystem

Sistema de geração de boletos bancários utilizando o padrão de projeto **Builder (GoF)**, implementado em Java 21 com Maven, seguindo as regras FEBRABAN 2023/2024.

## Bancos Suportados

| Banco           | Código FEBRABAN |
|-----------------|-----------------|
| Bradesco        | 237             |
| Nubank          | 260             |
| Unibanco / Itaú | 341             |

## Como Compilar e Executar

### Pré-requisitos

*   Java Development Kit (JDK) 21 ou superior
*   Apache Maven 3.x ou superior

### Compilação

Para compilar o projeto, navegue até o diretório `boleto-builder-system` e execute o seguinte comando Maven:

```bash
mvn clean package
```

Este comando irá compilar o código-fonte, executar os testes (se houver) e empacotar o projeto em um arquivo JAR executável (`boleto-builder-system-1.0.0.jar`) dentro do diretório `target/`.

### Execução

Após a compilação, você pode executar o sistema a partir do arquivo JAR gerado. Navegue até o diretório `boleto-builder-system` e execute:

```bash
java -jar target/boleto-builder-system-1.0.0.jar
```

O programa irá iniciar uma interface de console interativa, solicitando que você escolha o banco e insira os dados necessários para a geração do boleto.

## Justificativa Arquitetural

### Por que Builder foi a escolha correta:

1.  **Separação de complexidade**: Um boleto possui dados simples (valor, datas) e cálculos complexos específicos por banco (campo livre, DV FEBRABAN). O padrão Builder separa essas responsabilidades — o Director orquestra a ordem, e o Builder concreto implementa a lógica técnica de cada banco.

2.  **Open/Closed Principle**: Para adicionar um novo banco (ex: Banco Inter), basta criar uma nova implementação de `BoletoBuilder` (ex: `InterBoletoBuilder`) sem modificar nenhuma classe existente. O sistema é aberto para extensão e fechado para modificação.

3.  **Imutabilidade como contrato financeiro**: O objeto `Boleto` é imutável por design. Um boleto bancário emitido é um documento fiscal que não pode ser alterado após a geração. A imutabilidade garante essa propriedade em nível de código.

4.  **Fluent Interface**: O retorno `this` nos métodos do Builder permite um código expressivo e legível, como `builder.comCedente("X").comValor(100).build()`, tornando a intenção clara mesmo para quem lê o código sem conhecimento prévio do sistema.
