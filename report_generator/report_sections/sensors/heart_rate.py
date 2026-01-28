from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Sensor de medição de frequência cardíaca"
INTRO_2_PT = (
    "Os sinais de **frequência cardíaca** foram recolhidos **quatro vezes por dia**, durante períodos de **20 minutos**, "
    "com o principal objetivo de identificar possíveis situações de stress. Uma frequência cardíaca elevada, "
    "quando não associada à realização de atividade física, pode indicar — embora não de forma conclusiva — "
    "situações de stress. Por esse motivo, foram considerados apenas os dados de frequência cardíaca recolhidos "
    "quando o trabalhador se encontrava em postura sentada, de forma a excluir aumentos associados ao movimento."
)

INTRO_3_PT = (
    "Em adultos, a frequência cardíaca em repouso situa-se **normalmente entre 60 e 100 batimentos por minuto (BPM)**. "
    "Estes valores podem variar consoante a idade e o nível de atividade física de cada pessoa, devendo por isso "
    "ser interpretados apenas como valores de referência."
)

INTRO_4_PT = (
    "De modo a permitir a comparação dos resultados entre diferentes trabalhadores, foi calculado um *rácio de frequência cardíaca*."
    " Este rácio tem em consideração a frequência cardíaca máxima, que depende da idade, e a "
    "frequência cardíaca em repouso de cada trabalhador. Com base neste rácio, foram definidos diferentes níveis "
    "para classificar a frequência cardíaca. Uma vez que valores entre 30% e 39% são considerados normais durante "
    "atividade física ligeira, a presença destes valores, ou superiores, enquanto o trabalhador se encontra sentado "
    "pode ser interpretada como um possível indicador de stress. Assim, foram definidas as seguintes classes:"
)

INTRO_5_PT = "- **Normal**: rácio de frequência cardíaca inferior a **30%**."

INTRO_6_PT = "- **Ligeiramente elevado**: rácio de frequência cardíaca entre **30% e 39%**."

INTRO_7_PT = "- **Elevado**: rácio de frequência cardíaca superior a **39%**."


PLOT_EXPLAIN_1_PT = (
    "O gráfico abaixo apresenta a variação da frequência cardíaca em cada aquisição ao longo dos diferentes "
    "dias da semana. Cada barra vermelha representa uma aquisição e mostra, no topo, o valor máximo de "
    "frequência cardíaca registado (em batimentos por minuto) e, na base, o valor mínimo. "
    "Desta forma, é possível analisar as variações da frequência cardíaca entre aquisições no mesmo dia "
    "e entre dias diferentes. Caso alguma aquisição não tenha sido realizada, é apresentada uma barra a "
    "cinzento no local correspondente."
)
PLOT_EXPLAIN_2_PT = (
    "O gráfico seguinte apresenta a distribuição do rácio de frequência cardíaca em cada aquisição, "
    "ao longo dos diferentes dias. A cor verde representa a percentagem de tempo em que a frequência cardíaca "
    "se encontrou dentro do intervalo normal, a cor amarela indica valores ligeiramente elevados e a cor vermelha "
    "corresponde a valores elevados. "
    "À direita são indicadas as horas a que ocorreram as aquisições em cada dia, permitindo identificar o momento "
    "em que cada registo do smartwatch foi realizado. Caso necessário, pode consultar novamente a secção do "
    "cronograma das aquisições diárias para verificar os horários correspondentes. "
    "As aquisições que não se realizaram são representadas a cinzento."
)
RISK_1_PT = "Em relação ao intervalo de frequência cardíaca ao longo do dia, foram delineados os seguinte riscos:"
RISK_2_PT = "Em relação ao nível de ritmo cardíaco ao longo do dia, foram delineados os seguinte riscos:"
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
HEART_RATE_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT, INTRO_5_PT, INTRO_6_PT, INTRO_7_PT],
        RISK_RULE_KEY: [RISK_1_PT, RISK_2_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT, PLOT_EXPLAIN_2_PT],
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}