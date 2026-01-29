from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Avaliação biomecânica" # section title
INTRO_2_PT = (
    "As análises biomecânicas contribuem para uma melhor compreensão das causas subjacentes ao movimento. "
    "Neste âmbito, foram avaliados os **equipamentos** utilizados no posto de trabalho, os quais, quando inadequados ou utilizados de forma incorreta, "
    "podem aumentar o risco biomecânico. A entidade patronal desempenha um papel fundamental na redução destes riscos. "
    "Nesse sentido, foram também identificadas e transmitidas as medidas coletivas a implementar."
)
INTRO_3_PT = (
    "O instrumento de avaliação biomecânica utilizado foi o questionário **ROSA** (*Rapid Office Strain Assessment*). "
    "Este questionário foi desenvolvido para avaliar o risco ergonómico associado ao trabalho de escritório, "
    "tendo em consideração a postura adotada e a forma como são utilizados equipamentos como a **cadeira**, o **monitor**, "
    "o **teclado**, o **rato** e o **telefone**. Com base nas respostas fornecidas, o questionário permite identificar situações "
    "de maior risco biomecânico e apoiar a definição de recomendações para a melhoria das condições ergonómicas "
    "no posto de trabalho."
)

PLOT_EXPLAIN_0_PT = (
    "O gráfico abaixo apresenta os resultados calculados com base nas respostas dadas ao questionário de "
    "avaliação biomecânica, para os diferentes equipamentos utilizados ao longo do dia de trabalho. "
    "A tabela mostra as diferentes dimensões do questionário, numeradas conforme a figura dos resultados."
    "O **resultado geral final** é utilizado para avaliação ergonómica e fornece uma indicação do seu **risco "
    "ergonómico global**. Quando este resultado se encontra assinalado a amarelo ou a vermelho, significa que "
    "existem aspetos a melhorar na forma como utiliza os diferentes equipamentos de trabalho. Nesses casos, "
    "recomenda-se a análise das dimensões específicas que contribuíram para esse resultado, de modo a identificar "
    "os domínios que necessitam de intervenção."
)

PLOT_EXPLAIN_1_1_PT = "1. Cadeira"
PLOT_EXPLAIN_1_2_PT = "2. Monitor"
PLOT_EXPLAIN_1_3_PT = "3. Telefone"
PLOT_EXPLAIN_1_4_PT = "4. Rato"
PLOT_EXPLAIN_1_5_PT = "5. Teclado"
PLOT_EXPLAIN_1_6_PT = "6. Resultado geral final (*ROSA score*)"

# ------------------------------------------------------------------------------------------------------------------- #
# english
# ------------------------------------------------------------------------------------------------------------------- #
# no need to do this now, I'll translate the texts at a later stage
INTRO_ENG = ""
RISK_ENG = ""
PLOT_ENG = ""

# ------------------------------------------------------------------------------------------------------------------- #
# text dictionary
# ------------------------------------------------------------------------------------------------------------------- #
ROSA_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT],
        RISK_RULE_KEY: [],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_0_PT, PLOT_EXPLAIN_1_1_PT, PLOT_EXPLAIN_1_2_PT, PLOT_EXPLAIN_1_3_PT, PLOT_EXPLAIN_1_4_PT, PLOT_EXPLAIN_1_5_PT, PLOT_EXPLAIN_1_6_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}