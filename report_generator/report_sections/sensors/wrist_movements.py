from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Sensores de movimento - movimentos significativos do pulso"
INTRO_2_PT =(
    "Os movimentos do punho analisados nesta secção referem-se ao punho da mão que utiliza o rato "
    "e foram avaliados apenas durante os períodos em que o trabalhador se encontrava sentado. "
    "A análise considera exclusivamente as acelerações do punho, não sendo avaliados movimentos de rotação."
)
INTRO_3_PT = (
    "Durante o trabalho de escritório, são comuns movimentos frequentes do punho e da mão, "
    "como ao utilizar o rato, o teclado ou manusear documentos. "
    "Estes movimentos podem ser pequenos e repetitivos ou mais rápidos e abruptos, "
    "estando padrões muito intensos associados a maior esforço dos membros superiores."
)
INTRO_4_PT = (
    "Por outro lado, uma frequência muito reduzida de movimentos do punho "
    "também pode não ser desejável. "
    "A imobilidade prolongada, especialmente na ausência de apoio ergonómico adequado, "
    "pode contribuir para posturas desfavoráveis e desconforto músculo-esquelético."
)
INTRO_5_PT = (
    "A percentagem de movimentos significativos do punho indica quantos dos movimentos realizados "
    "foram mais rápidos ou abruptos, em relação ao total de movimentos registados "
    "durante o trabalho sentado. "
    "Esta métrica permite identificar tanto situações de elevada atividade do punho "
    "como padrões de imobilidade prolongada, devendo ser interpretada no contexto ergonómico."
)

PLOT_EXPLAIN_1_PT = (
    "O gráfico apresenta a percentagem de movimentos significativos do punho "
    "em cada aquisição ao longo da semana. "
    "Cada linha corresponde a um dia de trabalho e cada coluna a uma aquisição. "
    "Valores mais elevados indicam maior frequência de movimentos rápidos do punho, "
    "enquanto células a cinzento indicam ausência de dados."
)
RISK_PT=''
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
WRIST_MOVEMENT_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT, INTRO_5_PT],
        RISK_RULE_KEY: [RISK_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}