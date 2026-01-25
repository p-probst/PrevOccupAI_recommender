from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Avaliação Biomecânica" # section title
INTRO_2_PT = (
    "As análises biomecânicas contribuem para uma melhor compreensão das causas subjacentes ao movimento. "
    "Neste âmbito, foram avaliados os equipamentos utilizados no posto de trabalho, os quais, quando inadequados, "
    "podem aumentar o risco biomecânico. A entidade patronal desempenha um papel fundamental na redução destes riscos. "
    "Nesse sentido, foram também identificadas e transmitidas as medidas coletivas a implementar."
)

RISK_1_PT = (
    "A cada equipamento está associada uma cor que representa o nível de risco identificado. "
    "A cor verde indica baixo risco, a cor amarela sinaliza a existência de algum risco ergonómico, "
    "e a cor vermelha corresponde a um risco elevado, para o qual devem ser adotadas medidas com vista "
    "à sua redução. As secções que se encontrem a amarelo ou vermelho são consideradas de risco, logo, recomendações"
    "para essas secções são apresentadas"
)

PLOT_EXPLAIN_1_PT = (
    "O gráfico abaixo apresenta os resultados calculados com base nas respostas dadas ao questionário de "
    "avaliação biomecânica, para os diferentes equipamentos utilizados ao longo do dia de trabalho. "
    "Da esquerda para a direita, são apresentados os resultados correspondentes à cadeira (1), monitor (2), "
    "telefone (3), rato (4), teclado (5) e ao resultado geral final (6)."
)

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
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT],
        RISK_RULE_KEY: [RISK_1_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}