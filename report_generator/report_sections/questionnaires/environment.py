from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Avaliação Ambiental"
INTRO_2_PT = (
    "Ambientes de trabalho com condições inadequadas aumentam o risco de lesões músculo-esqueléticas e "
    "influenciam negativamente a produtividade e o bem-estar geral do trabalhador. Neste contexto, foram "
    "avaliados fatores ambientais, tais como o nível de iluminação, a qualidade do ar, o ruído e a organização "
    "do posto de trabalho. "
    "Relativamente à dimensão da privacidade do escritório, os resultados apresentados têm um caráter "
    "exclusivamente informativo, não estando associadas recomendações individuais, uma vez que este aspeto "
    "depende sobretudo de fatores organizacionais. "
    "A entidade patronal desempenha um papel fundamental na redução destes riscos e, nesse sentido, foram "
    "identificadas e transmitidas as medidas coletivas a implementar."
)

PLOT_EXPLAIN_1_PT = (
    "O gráfico abaixo apresenta os resultados calculados com base nas respostas dadas ao questionário de "
    "avaliação ambiental. A tabela abaixo mostra as diferentes dimensões do questionário, numeradas conforme a figura dos resultados."
)
PLOT_EXPLAIN_2_1_PT = "1. Iluminação"
PLOT_EXPLAIN_2_2_PT = "2. Ar"
PLOT_EXPLAIN_2_3_PT = "3. Ruído"
PLOT_EXPLAIN_2_4_PT = "4. Design do escritório"
PLOT_EXPLAIN_2_5_PT = "5. Privacidade do escritório"
PLOT_EXPLAIN_2_6_PT = "6. Organização do escritório"

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
ENVIRONMENT_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT],
        RISK_RULE_KEY: [],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT, PLOT_EXPLAIN_2_1_PT, PLOT_EXPLAIN_2_2_PT, PLOT_EXPLAIN_2_3_PT, PLOT_EXPLAIN_2_4_PT,
                           PLOT_EXPLAIN_2_5_PT, PLOT_EXPLAIN_2_6_PT],
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}