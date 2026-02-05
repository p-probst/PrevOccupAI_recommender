from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Registo diário da dor"
INTRO_2_PT = (
    "O trabalho de escritório encontra-se frequentemente associado ao aparecimento de dor músculo-esquelética, "
    "em particular nas regiões do pescoço, ombros, costas e membros superiores. "
    "Estas queixas podem surgir de forma progressiva ao longo do dia de trabalho, "
    "especialmente quando existe permanência prolongada em posturas estáticas ou movimentos repetitivos."
)

INTRO_3_PT = (
    "De forma a avaliar a **presença e evolução da dor** ao longo da semana de trabalho, "
    "preencheu um questionário de autoavaliação da dor no **início e no final de cada turno**. "
    "Este questionário consistiu na identificação das zonas do corpo onde existia dor, "
    "bem como na indicação da sua intensidade."
)

INTRO_4_PT = (
    "A intensidade da dor foi avaliada através da escala numérica de dor (NPRS), "
    "que varia de zero a dez. Nesta escala, o valor 0 corresponde à ausência total de dor, "
    "valores baixos indicam dor ligeira, valores intermédios indicam dor moderada "
    "e valores elevados correspondem a dor intensa. "
)

INTRO_5_PT = (
    "O registo de dor no início e no final do turno permite analisar não só "
    "a presença de dor, mas também possíveis alterações ao longo do dia de trabalho, "
    "identificando situações em que a atividade profissional possa estar associada ao agravamento dos sintomas."
)


PLOT_EXPLAIN_1_PT = (
    "O gráfico apresenta a evolução semanal da dor reportada por si."
" Cada par de figuras corresponde a um dia de aquisição, permitindo comparar visualmente "
    "as zonas do corpo onde foi reportada dor e a respetiva intensidade antes e depois do trabalho."
" As cores utilizadas representam a intensidade da dor, de acordo com a escala numérica apresentada no topo do gráfico. A ausência de "
    "dor corresponde a uma intensidade zero, ou seja, sem dor. "
    "Sempre que não é reportada dor, as figuras correspondentes surgem sem marcação de áreas coloridas."
)


RISK_1_PT = ""

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
PAIN_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT, INTRO_5_PT],
        RISK_RULE_KEY: [RISK_1_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}