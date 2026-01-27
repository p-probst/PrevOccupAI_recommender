from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #

INTRO_1_PT = "Sensores ambientais: medição única"
INTRO_2_PT = (
    "As aquisições de dados dos sensores ambientais foram realizadas por profissionais da CML. "
    "Estes dados foram recolhidos apenas uma vez no local de trabalho de cada participante. "

    "Os sensores permitiram medir: "
)
INTRO_3_PT = "- **temperatura** (em graus Celsius, $^\\circ$C);"

INTRO_4_PT = "- **humidade relativa** (em percentagem, %);"

INTRO_5_PT = (
    "- concentrações de **dióxido de carbono (CO$_2$)**, **monóxido de carbono (CO)** e "
    "**compostos orgânicos voláteis (COV)**, expressas em partes por milhão (ppm);"
)

INTRO_6_PT = (
    "- concentração de **partículas em suspensão** com diâmetro de 2,5 $\\mu$m e 10 $\\mu$m (micrómetros) "
    "(PM2.5 e PM10), expressa em microgramas por metro cúbico ($\\mu$g/m$^3$);"
)

INTRO_7_PT = (
    "- **iluminância** (lux), medida em vários pontos do posto de trabalho de cada participante, "
    "tendo sido calculada a média dessas medições para obtenção do valor final."
)
PLOT_EXPLAIN_PT = (
    "Os gráficos que se seguem apresentam os valores medidos pelos sensores ambientais, representados por linhas verdes, "
    "bem como os respetivos valores de referência, definidos com base em publicações de organizações internacionais "
    "e em literatura científica. "
    "Sempre que existam valores de referência mínimos, estes são representados por uma linha azul tracejada. "
    "Os valores de referência máximos, ou o valor de referência único, "
    "são representados por uma linha vermelha tracejada."
)
# ------------------------------------------------------------------------------------------------------------------- #
# english
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_ENG = ''
PLOT_ENG = ''
# ------------------------------------------------------------------------------------------------------------------- #
# text dictionary
# ------------------------------------------------------------------------------------------------------------------- #
CML_SENSORS_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT, INTRO_5_PT, INTRO_6_PT, INTRO_7_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}