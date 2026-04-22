# ESPECIFICAÇÃO TÉCNICA — BoletoBuilderSystem
> Documento gerado com Auxílio do Claude
> Destino: Agente de execução (Manus)  
> Padrão: Builder (GoF) · Java 21 · Maven · Regras FEBRABAN 2023/2024

---

## 1. VISÃO GERAL DO SISTEMA

Sistema de geração de boletos bancários utilizando o padrão de projeto **Builder (GoF)**.  
O objeto `Boleto` é complexo (envolve cálculos específicos por banco + algoritmos FEBRABAN), portanto o Builder separa **a construção** da **representação final**.

**Bancos suportados:**
| Banco | Código FEBRABAN | Campo Livre |
|---|---|---|
| Bradesco | 237 | Agência + Carteira + Nosso Número (formato específico) |
| Nubank (Nu Pagamentos) | 260 | Convênio + Nosso Número (padrão correspondente) |
| Unibanco / Itaú | 341 | Agência + Conta + Carteira + Nosso Número |

---

## 2. ESTRUTURA DE PASTAS (Maven)

```
boleto-builder-system/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── br/com/projeto/boleto/
                ├── model/
                │   ├── Boleto.java
                │   └── DadosBoleto.java
                ├── builder/
                │   ├── BoletoBuilder.java
                │   ├── BradescoBoletoBuilder.java
                │   ├── NubankBoletoBuilder.java
                │   └── UnibancoBoletoBuilder.java
                ├── director/
                │   └── BoletoDirector.java
                ├── service/
                │   └── GeradorBoletoService.java
                ├── util/
                │   └── CalculadoraFebraban.java
                └── Main.java
```

---

## 3. ALGORITMOS FEBRABAN (OBRIGATÓRIO IMPLEMENTAR COM PRECISÃO)

### 3.1 Módulo 10 — usado nos blocos da Linha Digitável

```
Regra:
1. Percorrer os dígitos da direita para a esquerda
2. Multiplicar alternadamente por 2 e 1 (começando pelo último dígito × 2)
3. Se o resultado de uma multiplicação for >= 10, somar os dígitos do resultado (ex: 16 → 1+6 = 7)
4. Somar todos os resultados
5. resto = soma % 10
6. DV = (resto == 0) ? 0 : (10 - resto)

Exemplo: campo "34191.09008" → DV = ?
Aplica-se Módulo 10 sobre os 9 dígitos numéricos → DV é o 10º dígito do bloco.
```

### 3.2 Módulo 11 — usado no Dígito Verificador Geral (posição 5 do código de barras)

```
ATENÇÃO: Esta é a regra onde IAs frequentemente erram. Implemente com cuidado.

Regra:
1. Usar os 43 dígitos do código de barras (ignorar a posição 5, que é o DV)
2. Multiplicar da direita para a esquerda por pesos 2, 3, 4, 5, 6, 7, 8, 9 (cicla de 2 a 9)
3. Somar todos os produtos
4. resto = soma % 11
5. Calcular DV:
   - Se resto == 0 → DV = 1
   - Se resto == 1 → DV = 1   ← REGRA CRÍTICA
   - Se resto >= 2 → DV = 11 - resto

RESUMO DA REGRA CRÍTICA: se (resto == 0 || resto == 1) então DV = 1
```

### 3.3 Fator de Vencimento

```
O fator de vencimento é um número de 4 dígitos = dias decorridos desde 07/10/1997.

Fórmula:
fatorVencimento = ChronoUnit.DAYS.between(LocalDate.of(1997, 10, 7), dataVencimento)

Exemplo: vencimento 30/04/2026 → fator = 10432 (aproximado)

ATENÇÃO: Se fator > 9999, reinicia a contagem a partir de 03/07/2025 (bloco B).
Para este projeto acadêmico, use a fórmula simples sem reprocessamento de bloco.
```

---

## 4. ESTRUTURA DO CÓDIGO DE BARRAS (44 posições)

```
Posição  1- 3 : Código do banco (ex: 237 Bradesco)
Posição  4    : Código da moeda (sempre "9" para Real)
Posição  5    : Dígito Verificador Geral (calculado por Módulo 11)
Posição  6- 9 : Fator de vencimento (4 dígitos)
Posição 10-19 : Valor do documento (10 dígitos, zeros à esquerda, sem vírgula)
               Ex: R$ 150,75 → "0000015075"
Posição 20-44 : Campo livre (25 dígitos, específico por banco)
```

---

## 5. ESTRUTURA DA LINHA DIGITÁVEL (47 posições + formatação)

```
Formato final: AAAAA.AAAAAB BBBBB.BBBBBB C DEEEE.FFFFFFFFF
Onde:
  Bloco 1 (10 dígitos + ponto): posições  1- 4 do CB + posições 20-24 do CB + DV10
  Bloco 2 (11 dígitos + ponto): posições 25-34 do CB + DV10
  Bloco 3 (11 dígitos       ): posições 35-44 do CB + DV10
  Bloco 4 (1 dígito          ): DV Geral (posição 5 do CB)
  Bloco 5 (14 dígitos        ): Fator de vencimento + Valor

Cada bloco 1, 2 e 3 tem seu próprio DV calculado por Módulo 10.
```

---

## 6. CAMPO LIVRE POR BANCO (25 dígitos — posições 20 a 44)

### Bradesco (237)
```
Posição 20-22 : Agência (3 dígitos, zeros à esquerda)
Posição 23    : Carteira (1 dígito) — use "0" para o projeto
Posição 24-31 : Nosso Número (8 dígitos, zeros à esquerda)
Posição 32-38 : Conta do Cedente (7 dígitos, zeros à esquerda)
Posição 39    : Zero (fixo)
Posição 40-44 : DV do Campo Livre (calculado por Módulo 11 sobre as posições 20-39)

Observação: O DV do campo livre Bradesco é calculado separadamente.
```

### Nubank / Nu Pagamentos (260)
```
Para fins acadêmicos, simular como convênio via correspondente:
Posição 20-25 : Código do convênio (6 dígitos) — use "000001" como padrão
Posição 26-44 : Nosso Número (19 dígitos, zeros à esquerda)

Observação: Nubank não opera boleto clássico diretamente. Este modelo é 
uma simplificação acadêmica válida para demonstrar o padrão Builder.
```

### Unibanco / Itaú (341)
```
Posição 20-22 : Agência (3 dígitos)
Posição 23-29 : Conta do Cedente (7 dígitos, zeros à esquerda)  
Posição 30    : DV Agência/Conta (Módulo 10)
Posição 31-41 : Nosso Número (11 dígitos, zeros à esquerda)
Posição 42-44 : Carteira (3 dígitos) — use "110" como padrão
```

---

## 7. SKELETON CODE — CLASSES PRINCIPAIS

### 7.1 DadosBoleto.java (DTO)
```java
package br.com.projeto.boleto.model;

import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Data Transfer Object com os dados de entrada do usuário.
 * Não realiza nenhum cálculo — apenas transporta dados.
 */
public class DadosBoleto {
    private String cedente;
    private String sacado;
    private String cpfCnpjSacado;
    private BigDecimal valor;
    private LocalDate dataVencimento;
    private String nossoNumero;
    private String agencia;
    private String conta;
    private String numeroDocumento;

    // Construtor completo + getters (sem setters — use Builder próprio se quiser)
    // Gerar todos os getters
}
```

### 7.2 Boleto.java (Produto Final — IMUTÁVEL)
```java
package br.com.projeto.boleto.model;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

/**
 * Produto final do padrão Builder.
 * TODOS os campos são final — objeto imutável após construção.
 * Uma vez gerado, um boleto não pode ser alterado (segurança financeira).
 */
public final class Boleto {
    private final String banco;
    private final String cedente;
    private final String sacado;
    private final BigDecimal valor;
    private final LocalDate dataVencimento;
    private final String nossoNumero;
    private final String codigoBarras;      // 44 dígitos
    private final String linhaDigitavel;    // 47 dígitos formatados
    private final String campoLivre;        // 25 dígitos

    // Construtor package-private (só os builders constroem)
    Boleto(String banco, String cedente, String sacado, BigDecimal valor,
           LocalDate dataVencimento, String nossoNumero,
           String codigoBarras, String linhaDigitavel, String campoLivre) {
        this.banco = banco;
        this.cedente = cedente;
        this.sacado = sacado;
        this.valor = valor;
        this.dataVencimento = dataVencimento;
        this.nossoNumero = nossoNumero;
        this.codigoBarras = codigoBarras;
        this.linhaDigitavel = linhaDigitavel;
        this.campoLivre = campoLivre;
    }

    // Apenas getters — NENHUM setter
    public String getCodigoBarras() { return codigoBarras; }
    public String getLinhaDigitavel() { return linhaDigitavel; }
    public String getBanco() { return banco; }
    public BigDecimal getValor() { return valor; }
    public LocalDate getDataVencimento() { return dataVencimento; }

    /**
     * Impressão formatada do boleto no console.
     */
    public void imprimir() {
        System.out.println("=".repeat(60));
        System.out.println("BOLETO BANCÁRIO — " + banco.toUpperCase());
        System.out.println("=".repeat(60));
        System.out.printf("Cedente       : %s%n", cedente);
        System.out.printf("Sacado        : %s%n", sacado);
        System.out.printf("Valor         : R$ %,.2f%n", valor);
        System.out.printf("Vencimento    : %s%n",
            dataVencimento.format(DateTimeFormatter.ofPattern("dd/MM/yyyy")));
        System.out.printf("Nosso Número  : %s%n", nossoNumero);
        System.out.println("-".repeat(60));
        System.out.printf("Linha Digitável: %s%n", linhaDigitavel);
        System.out.printf("Código Barras  : %s%n", codigoBarras);
        System.out.println("=".repeat(60));
    }

    @Override
    public String toString() {
        return String.format("Boleto[banco=%s, valor=R$%.2f, vencimento=%s, linhaDigitavel=%s]",
            banco, valor, dataVencimento, linhaDigitavel);
    }
}
```

### 7.3 BoletoBuilder.java (Interface — Contrato)
```java
package br.com.projeto.boleto.builder;

import br.com.projeto.boleto.model.Boleto;
import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Interface Builder — define o contrato fluente de construção.
 * Cada método retorna 'this' para permitir encadeamento (Fluent Interface).
 * O método build() é onde a lógica pesada FEBRABAN acontece.
 */
public interface BoletoBuilder {
    BoletoBuilder comCedente(String cedente);
    BoletoBuilder comSacado(String sacado, String cpfCnpj);
    BoletoBuilder comValor(BigDecimal valor);
    BoletoBuilder comDataVencimento(LocalDate vencimento);
    BoletoBuilder comNossoNumero(String nossoNumero);
    BoletoBuilder comAgencia(String agencia);
    BoletoBuilder comConta(String conta);
    BoletoBuilder comNumeroDocumento(String numeroDocumento);

    /**
     * Constrói e retorna o Boleto final.
     * É aqui que cada builder concreto executa:
     * 1. Monta o campo livre específico do banco
     * 2. Calcula o código de barras (44 dígitos)
     * 3. Calcula o DV geral (Módulo 11 FEBRABAN)
     * 4. Gera a linha digitável (47 dígitos)
     */
    Boleto build();
}
```

### 7.4 CalculadoraFebraban.java (Utilitário — isolar aqui toda a matemática)
```java
package br.com.projeto.boleto.util;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

/**
 * Classe utilitária com os algoritmos oficiais FEBRABAN.
 * Todos os métodos são static — sem estado.
 * ISOLADA para facilitar auditoria e testes unitários.
 *
 * REFERÊNCIA: Manual de Integração FEBRABAN — Subgrupo Técnico de Compensação.
 */
public class CalculadoraFebraban {

    private static final LocalDate DATA_BASE_FEBRABAN = LocalDate.of(1997, 10, 7);

    /**
     * Calcula o Dígito Verificador pelo Módulo 10.
     * Usado nos blocos 1, 2 e 3 da Linha Digitável.
     *
     * REGRA CRÍTICA: se resto == 0, DV = 0
     */
    public static int calcularModulo10(String numero) {
        int soma = 0;
        int peso = 2;
        for (int i = numero.length() - 1; i >= 0; i--) {
            int resultado = Character.getNumericValue(numero.charAt(i)) * peso;
            if (resultado >= 10) {
                resultado = (resultado / 10) + (resultado % 10);
            }
            soma += resultado;
            peso = (peso == 2) ? 1 : 2;
        }
        int resto = soma % 10;
        return (resto == 0) ? 0 : (10 - resto);
    }

    /**
     * Calcula o Dígito Verificador Geral pelo Módulo 11.
     * Usado na posição 5 do Código de Barras.
     *
     * REGRA CRÍTICA (onde IAs erram): se resto == 0 OU resto == 1, DV = 1
     * Para qualquer outro resto: DV = 11 - resto
     */
    public static int calcularModulo11(String numero) {
        int soma = 0;
        int peso = 2;
        for (int i = numero.length() - 1; i >= 0; i--) {
            soma += Character.getNumericValue(numero.charAt(i)) * peso;
            peso = (peso == 9) ? 2 : peso + 1;
        }
        int resto = soma % 11;
        // REGRA CRÍTICA FEBRABAN — não simplificar
        if (resto == 0 || resto == 1) {
            return 1;
        }
        return 11 - resto;
    }

    /**
     * Calcula o Fator de Vencimento (número de dias desde 07/10/1997).
     * Resulta em um número de 4 dígitos (com zeros à esquerda).
     */
    public static String calcularFatorVencimento(LocalDate dataVencimento) {
        long dias = ChronoUnit.DAYS.between(DATA_BASE_FEBRABAN, dataVencimento);
        return String.format("%04d", dias);
    }

    /**
     * Formata o valor para 10 dígitos sem separador decimal.
     * Ex: R$ 150,75 → "0000015075"
     */
    public static String formatarValor(java.math.BigDecimal valor) {
        // Remove vírgula/ponto, garante 10 dígitos
        String valorStr = valor.multiply(new java.math.BigDecimal("100"))
                               .toBigInteger()
                               .toString();
        return String.format("%010d", Long.parseLong(valorStr));
    }

    /**
     * Formata a Linha Digitável com pontos e espaços conforme FEBRABAN.
     * Entrada: 47 dígitos sem formatação
     * Saída: "AAAAA.AAAAAB BBBBB.BBBBBB C DEEEE.FFFFFFFFF"
     */
    public static String formatarLinhaDigitavel(String bloco1, String bloco2,
                                                 String bloco3, String dvGeral,
                                                 String fatorValor) {
        return String.format("%s %s %s %s %s",
            bloco1.substring(0, 5) + "." + bloco1.substring(5),
            bloco2.substring(0, 5) + "." + bloco2.substring(5),
            bloco3.substring(0, 5) + "." + bloco3.substring(5),
            dvGeral,
            fatorValor);
    }
}
```

### 7.5 BradescoBoletoBuilder.java (Builder Concreto — implementar completamente)
```java
package br.com.projeto.boleto.builder;

import br.com.projeto.boleto.model.Boleto;
import br.com.projeto.boleto.util.CalculadoraFebraban;
import java.math.BigDecimal;
import java.time.LocalDate;

/**
 * Builder concreto para boletos do Bradesco.
 * Código do banco: 237
 * Moeda: 9 (Real)
 *
 * Estrutura do Campo Livre (25 dígitos):
 * [agencia 3][carteira 1][nossoNumero 8][conta 7][zero 1][dvCampoLivre 1] = 21 dígitos
 * + 4 zeros de padding para completar 25 posições
 *
 * REFERÊNCIA: Manual Técnico do Bradesco — Subgrupo de Cobrança.
 */
public class BradescoBoletoBuilder implements BoletoBuilder {

    private static final String CODIGO_BANCO = "237";
    private static final String MOEDA = "9";
    private static final String CARTEIRA_PADRAO = "0";

    // Campos internos
    private String cedente;
    private String sacado;
    private String cpfCnpj;
    private BigDecimal valor;
    private LocalDate dataVencimento;
    private String nossoNumero;
    private String agencia;
    private String conta;
    private String numeroDocumento;

    @Override
    public BoletoBuilder comCedente(String cedente) {
        this.cedente = cedente;
        return this;
    }

    @Override
    public BoletoBuilder comSacado(String sacado, String cpfCnpj) {
        this.sacado = sacado;
        this.cpfCnpj = cpfCnpj;
        return this;
    }

    @Override
    public BoletoBuilder comValor(BigDecimal valor) {
        this.valor = valor;
        return this;
    }

    @Override
    public BoletoBuilder comDataVencimento(LocalDate vencimento) {
        this.dataVencimento = vencimento;
        return this;
    }

    @Override
    public BoletoBuilder comNossoNumero(String nossoNumero) {
        this.nossoNumero = String.format("%08d", Long.parseLong(nossoNumero));
        return this;
    }

    @Override
    public BoletoBuilder comAgencia(String agencia) {
        this.agencia = String.format("%03d", Integer.parseInt(agencia));
        return this;
    }

    @Override
    public BoletoBuilder comConta(String conta) {
        this.conta = String.format("%07d", Long.parseLong(conta));
        return this;
    }

    @Override
    public BoletoBuilder comNumeroDocumento(String numeroDocumento) {
        this.numeroDocumento = numeroDocumento;
        return this;
    }

    /**
     * Monta o boleto completo:
     * 1. Constrói o campo livre (25 dígitos)
     * 2. Monta o código de barras sem DV (43 dígitos)
     * 3. Calcula o DV geral (Módulo 11)
     * 4. Insere o DV na posição 5
     * 5. Gera os 3 blocos da linha digitável com Módulo 10
     * 6. Formata a linha digitável final
     */
    @Override
    public Boleto build() {
        validarCamposObrigatorios();

        // Passo 1: Campo Livre Bradesco (25 dígitos)
        String campoLivreSemDV = agencia + CARTEIRA_PADRAO + nossoNumero + conta + "0";
        int dvCampoLivre = CalculadoraFebraban.calcularModulo11(campoLivreSemDV);
        // Padding para 25 posições (campo livre + DV + completar com zeros se necessário)
        String campoLivre = String.format("%-25s",
            campoLivreSemDV + dvCampoLivre).replace(' ', '0');

        // Passo 2: Código de barras sem DV (43 dígitos)
        String fatorVencimento = CalculadoraFebraban.calcularFatorVencimento(dataVencimento);
        String valorFormatado = CalculadoraFebraban.formatarValor(valor);

        String codigoSemDV = CODIGO_BANCO + MOEDA
            + fatorVencimento
            + valorFormatado
            + campoLivre;

        // Passo 3: DV Geral (Módulo 11 sobre os 43 dígitos)
        int dvGeral = CalculadoraFebraban.calcularModulo11(codigoSemDV);

        // Passo 4: Código de barras final (44 dígitos, DV na posição 5)
        String codigoBarras = CODIGO_BANCO + MOEDA + dvGeral
            + fatorVencimento + valorFormatado + campoLivre;

        // Passo 5: Linha Digitável — 3 blocos + DV + fator+valor
        // Bloco 1: banco(3) + moeda(1) + campoLivre[0..4](5) + DV10
        String bloco1Base = CODIGO_BANCO + MOEDA + campoLivre.substring(0, 5);
        String bloco1 = bloco1Base + CalculadoraFebraban.calcularModulo10(bloco1Base);

        // Bloco 2: campoLivre[5..14](10) + DV10
        String bloco2Base = campoLivre.substring(5, 15);
        String bloco2 = bloco2Base + CalculadoraFebraban.calcularModulo10(bloco2Base);

        // Bloco 3: campoLivre[15..24](10) + DV10
        String bloco3Base = campoLivre.substring(15, 25);
        String bloco3 = bloco3Base + CalculadoraFebraban.calcularModulo10(bloco3Base);

        // Passo 6: Linha digitável formatada
        String linhaDigitavel = CalculadoraFebraban.formatarLinhaDigitavel(
            bloco1, bloco2, bloco3,
            String.valueOf(dvGeral),
            fatorVencimento + valorFormatado
        );

        return new Boleto("Bradesco", cedente, sacado, valor,
                          dataVencimento, nossoNumero,
                          codigoBarras, linhaDigitavel, campoLivre);
    }

    private void validarCamposObrigatorios() {
        if (cedente == null || sacado == null || valor == null
            || dataVencimento == null || nossoNumero == null
            || agencia == null || conta == null) {
            throw new IllegalStateException(
                "Todos os campos obrigatórios devem ser preenchidos antes de build()");
        }
        if (valor.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Valor do boleto deve ser maior que zero.");
        }
    }
}
```

### 7.6 BoletoDirector.java
```java
package br.com.projeto.boleto.director;

import br.com.projeto.boleto.builder.BoletoBuilder;
import br.com.projeto.boleto.model.Boleto;
import br.com.projeto.boleto.model.DadosBoleto;

/**
 * Director — orquestra a sequência de chamadas ao Builder.
 * Garante que o boleto seja construído na ordem correta.
 * O cliente (Main) não precisa conhecer a ordem dos passos.
 */
public class BoletoDirector {

    public Boleto construirBoleto(BoletoBuilder builder, DadosBoleto dados) {
        return builder
            .comCedente(dados.getCedente())
            .comSacado(dados.getSacado(), dados.getCpfCnpjSacado())
            .comValor(dados.getValor())
            .comDataVencimento(dados.getDataVencimento())
            .comNossoNumero(dados.getNossoNumero())
            .comAgencia(dados.getAgencia())
            .comConta(dados.getConta())
            .comNumeroDocumento(dados.getNumeroDocumento())
            .build();
    }
}
```

### 7.7 GeradorBoletoService.java (Fachada)
```java
package br.com.projeto.boleto.service;

import br.com.projeto.boleto.builder.*;
import br.com.projeto.boleto.director.BoletoDirector;
import br.com.projeto.boleto.model.Boleto;
import br.com.projeto.boleto.model.DadosBoleto;

/**
 * Fachada (Facade) que o cliente usa.
 * Encapsula a escolha do builder e a orquestração do director.
 */
public class GeradorBoletoService {

    private final BoletoDirector director = new BoletoDirector();

    public enum Banco { BRADESCO, NUBANK, UNIBANCO }

    public Boleto gerar(Banco banco, DadosBoleto dados) {
        BoletoBuilder builder = switch (banco) {
            case BRADESCO -> new BradescoBoletoBuilder();
            case NUBANK   -> new NubankBoletoBuilder();
            case UNIBANCO -> new UnibancoBoletoBuilder();
        };
        return director.construirBoleto(builder, dados);
    }
}
```

### 7.8 Main.java (Interface Interativa Console)
```java
package br.com.projeto.boleto;

import br.com.projeto.boleto.model.DadosBoleto;
import br.com.projeto.boleto.service.GeradorBoletoService;
import br.com.projeto.boleto.service.GeradorBoletoService.Banco;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Scanner;

/**
 * Ponto de entrada do sistema.
 * Interface interativa via console.
 */
public class Main {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        GeradorBoletoService service = new GeradorBoletoService();

        System.out.println("╔══════════════════════════════════╗");
        System.out.println("║   SISTEMA DE GERAÇÃO DE BOLETOS  ║");
        System.out.println("║   Padrão Builder (GoF) — FEBRABAN ║");
        System.out.println("╚══════════════════════════════════╝");
        System.out.println();

        System.out.println("Selecione o banco:");
        System.out.println("  1 — Bradesco  (código 237)");
        System.out.println("  2 — Nubank    (código 260)");
        System.out.println("  3 — Unibanco  (código 341)");
        System.out.print("Opção: ");
        int opcao = sc.nextInt();
        sc.nextLine();

        Banco banco = switch (opcao) {
            case 1 -> Banco.BRADESCO;
            case 2 -> Banco.NUBANK;
            case 3 -> Banco.UNIBANCO;
            default -> throw new IllegalArgumentException("Opção inválida.");
        };

        DadosBoleto dados = coletarDados(sc);
        var boleto = service.gerar(banco, dados);
        boleto.imprimir();

        sc.close();
    }

    private static DadosBoleto coletarDados(Scanner sc) {
        System.out.print("Cedente (nome da empresa/pessoa): ");
        String cedente = sc.nextLine();

        System.out.print("Sacado (nome do pagador): ");
        String sacado = sc.nextLine();

        System.out.print("CPF/CNPJ do sacado: ");
        String cpfCnpj = sc.nextLine();

        System.out.print("Valor (ex: 150.75): ");
        BigDecimal valor = sc.nextBigDecimal();
        sc.nextLine();

        System.out.print("Data de vencimento (AAAA-MM-DD): ");
        LocalDate vencimento = LocalDate.parse(sc.nextLine());

        System.out.print("Nosso Número (até 8 dígitos): ");
        String nossoNumero = sc.nextLine();

        System.out.print("Agência (3 dígitos): ");
        String agencia = sc.nextLine();

        System.out.print("Conta (até 7 dígitos): ");
        String conta = sc.nextLine();

        System.out.print("Número do documento: ");
        String numDoc = sc.nextLine();

        // Montar DTO (implementar construtor completo em DadosBoleto)
        return new DadosBoleto(cedente, sacado, cpfCnpj, valor,
                               vencimento, nossoNumero, agencia, conta, numDoc);
    }
}
```

---

## 8. pom.xml (Maven — Java 21)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>br.com.projeto</groupId>
    <artifactId>boleto-builder-system</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- JUnit 5 para testes de auditoria -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.10.0</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.1.2</version>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <configuration>
                    <archive>
                        <manifest>
                            <mainClass>br.com.projeto.boleto.Main</mainClass>
                        </manifest>
                    </archive>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

---

## 9. CHECKLIST DE AUDITORIA (para o Arquiteto revisar o output do Manus)

```
AUDITORIA OBRIGATÓRIA — faça no Cursor/Neovim após o Manus entregar o código:

[ ] 1. MÓDULO 11: a condição é (resto == 0 || resto == 1) → DV = 1
        NÃO aceitar apenas (resto == 0) → DV = 1. Isso é bug FEBRABAN.

[ ] 2. IMUTABILIDADE: classe Boleto não pode ter nenhum método set*()
        Todos os campos devem ser "private final"

[ ] 3. LINHA DIGITÁVEL: deve ter exatamente 47 caracteres numéricos (sem formatação)
        Teste: assert boleto.getLinhaDigitavel().replaceAll("[^0-9]","").length() == 47

[ ] 4. CÓDIGO DE BARRAS: deve ter exatamente 44 dígitos numéricos
        Teste: assert boleto.getCodigoBarras().length() == 44

[ ] 5. VALOR ZERO: o sistema deve lançar IllegalArgumentException para valor <= 0

[ ] 6. FATOR DE VENCIMENTO: deve ser de 4 dígitos (com zero à esquerda se necessário)

[ ] 7. CAMPO LIVRE: deve ter exatamente 25 dígitos para todos os 3 bancos

[ ] 8. BUILDERS INDEPENDENTES: trocar o banco deve gerar linha digitável diferente
        (mesmo com dados idênticos de entrada, o campo livre muda por banco)

[ ] 9. CalculadoraFebraban: todos os métodos devem ser static e sem estado interno

[ ] 10. Nenhuma classe de negócio (Boleto, Builder) deve ter System.out.println()
         Saída apenas no Main e no método imprimir() do Boleto
```

---

## 10. JUSTIFICATIVA ARQUITETURAL (para entregar ao professor)

> Incluir este texto no README.md ou como comentário no início do Main.java

**Por que Builder foi a escolha correta:**

1. **Separação de complexidade**: Um boleto tem dados simples (valor, datas) e cálculos complexos específicos por banco (campo livre, DV FEBRABAN). O Builder separa essas responsabilidades — o Director orquestra a ordem, o Builder concreto implementa a lógica técnica de cada banco.

2. **Open/Closed Principle**: Para adicionar o Banco Inter, basta criar `InterBoletoBuilder implements BoletoBuilder` sem modificar nenhuma classe existente. O sistema é aberto para extensão e fechado para modificação.

3. **Imutabilidade como contrato financeiro**: O objeto `Boleto` é imutável por design. Um boleto bancário emitido é um documento fiscal — não pode ser alterado após a geração. A imutabilidade garante isso em nível de código.

4. **Fluent Interface**: O retorno `this` nos métodos do Builder permite código expressivo e legível: `builder.comCedente("X").comValor(100).build()` — a intenção fica clara mesmo para quem lê sem conhecer o sistema.

---

*Especificação gerada em 17/04/2026 — pronta para execução pelo Manus*
