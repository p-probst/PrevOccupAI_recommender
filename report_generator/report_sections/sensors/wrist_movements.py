from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Sensores de movimento: movimentos significativos do pulso"
INTRO_2_PT =(
    "Os movimentos do punho analisados nesta secção referem-se ao **punho da mão que utiliza o rato** "
    "e foram **avaliados** apenas durante os **períodos** em que se encontrava **sentado**. "
    "A análise considera exclusivamente as acelerações do punho, não sendo avaliados movimentos de rotação."
)
INTRO_3_PT = (
    "Durante o trabalho de escritório são frequentes os movimentos do punho e da mão, "
    "como na utilização do rato, do teclado ou no manuseamento de documentos. "
    "Padrões de movimento muito intensos ou repetitivos podem estar associados a um maior esforço "
    "dos membros superiores."
)

INTRO_4_PT = (
    "Por outro lado, uma frequência muito reduzida de movimentos do punho também pode ser desfavorável. "
    "A imobilidade prolongada, sobretudo na ausência de apoio ergonómico adequado, pode contribuir "
    "para posturas inadequadas e desconforto músculo-esquelético."
)
INTRO_5_PT = (
    "**A percentagem de movimentos significativos** do punho indica quantos dos movimentos realizados "
    "foram mais rápidos ou abruptos, **em relação ao total de movimentos registados** "
    "durante o trabalho sentado. "
    "Esta métrica permite identificar tanto situações de elevada atividade do punho "
    "como padrões de imobilidade prolongada, devendo ser interpretada no contexto ergonómico."
)

PLOT_EXPLAIN_1_PT = (
    "O gráfico apresenta a **percentagem de movimentos significativos do punho** "
    "ao longo da semana. "
    "Cada linha corresponde a um dia de trabalho e cada coluna a uma aquisição (I, II, III, IV) nesse dia. "
    "Valores mais elevados indicam maior frequência de movimentos rápidos do punho, "
    "enquanto células a cinzento indicam ausência de dados."
)
RISK_PT = (
    "Atualmente, não existem indicadores científicos que definam uma percentagem ideal de movimentos "
    "significativos do punho. No entanto, um **número reduzido** destes movimentos pode refletir um **comportamento "
    "mais estático** que, associado ao uso prolongado de um rato não ergonómico ou à ausência de apoio para o "
    "punho, pode levar a uma **flexão superior a 20 graus**, considerada um fator de **risco para lesões "
    "músculo-esqueléticas**. Assim, embora não seja possível definir recomendações personalizadas, a **realização "
    "regular de exercícios de mobilização do punho** pode ajudar a reduzir este risco."
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