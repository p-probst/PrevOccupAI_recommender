from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #

INTRO_1_PT = "Sensores ambientais de medição única"
INTRO_2_PT = (
    "As aquisições de dados dos sensores ambientais foram realizadas por profissionais da Câmara Municipal de Lisboa. "
    "Estes dados foram recolhidos apenas uma vez no local de trabalho de cada participante. "
    "Os sensores permitiram medir a temperatura (em graus Celsius, $^\circ$C), a humidade relativa (em percentagem, %), "
    "as concentrações de dióxido de carbono (CO$_2$), monóxido de carbono (CO) e compostos orgânicos voláteis (COV), "
    "expressas em partes por milhão (ppm), bem como a concentração de partículas em suspensão com diâmetro "
    "de 2,5 $\mu$m e 10 $\mu$m (PM2.5 e PM10), expressa em microgramas por metro cúbico ($\mu$g/m$^3$). "
    "No posto de trabalho de cada participante foram ainda medidos, em vários pontos, os níveis de iluminância (lux), "
    "tendo sido considerada a média dessas medições como valor final. Não existem recomendações individuais relativas a"
    "estes dados."
)
PLOT_EXPLAIN_PT = (
    "Os gráficos que se seguem apresentam os valores medidos pelos sensores ambientais, bem como os respetivos "
    "valores de referência, os quais se baseiam em publicações de organizações internacionais e em literatura científica."
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
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}