from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Sensores de Ruído"
INTRO_2_PT = (
    "A exposição prolongada ou excessiva a níveis elevados de ruído pode causar problemas de saúde, como stress, "
    "dificuldade de concentração e diminuição da produtividade no trabalho. De acordo com orientações de "
    "organizações internacionais, níveis de ruído abaixo de 80 dBA não estão geralmente associados a riscos "
    "significativos de perda auditiva. No entanto, em contextos de trabalho de escritório, níveis de ruído acima "
    "de 60 dBA, apesar de não serem necessariamente perigosos para a audição, são considerados incomodativos, podendo "
    "afetar negativamente a capacidade de concentração e o bem-estar emocional do trabalhador. "
    "Deste modo, para avaliar o nível de ruído a que o trabalhador está exposto e identificar possíveis riscos, "
    "foram definidas quatro classes de ruído:"
)

INTRO_3_PT = (
    "- **silencioso**, valores de ruído abaixo de **40 dBA**, correspondentes a um ambiente muito calmo, "
    "como uma sala silenciosa com ruído de fundo mínimo;"
)

INTRO_4_PT = (
    "- **baixo**, valores de ruído entre **40 e 60 dBA**, correspondentes a um ambiente com algum ruído de fundo "
    "(por exemplo, semelhante ao som de uma máquina de lavar loiça), mas que, em geral, não provoca incómodo;"
)

INTRO_5_PT = (
    "- **incomodativo**, valores de ruído entre **60 e 80 dBA**, correspondentes a um nível de ruído de fundo que "
    "causa desconforto e dificulta a concentração, semelhante a trabalhar próximo de um aspirador ou de um despertador;"
)

INTRO_6_PT = (
    "- **elevado**, valores de ruído acima de **80 dBA**, que, se prolongados no tempo, podem provocar problemas "
    "auditivos, sendo comparáveis a trabalhar perto de equipamentos ruidosos, como uma trituradora."
)

PLOT_EXPLAIN_PT = "this is the plot explain"

RISK_PT = "Tendo em conta estas classes de ruído, foram delineadas dois regras à definir o risco. "

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
NOISE_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT, INTRO_5_PT, INTRO_6_PT],
        RISK_RULE_KEY: {RISK_PT},
        PLOT_EXPLAIN_KEY: {PLOT_EXPLAIN_PT}
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}