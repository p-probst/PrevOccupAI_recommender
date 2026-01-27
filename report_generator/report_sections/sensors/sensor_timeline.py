from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Sensores fisiológicos: medições diárias"
INTRO_2_PT = (
    "Com o objetivo de estudar a saúde ocupacional, foram recolhidos dados diariamente ao longo de uma semana de trabalho. "
    "Foram utilizados três dispositivos diferentes: "
)
INTRO_3_PT = ("- um **smartphone**, que realizou aquisições ao longo de **todo o turno de trabalho**. Este dispositivo adquiriu "
              "dados de movimento e de nível de ruído.")
INTRO_4_PT = ("- Um **smartwatch**, agendado para adquirir **quatro vezes por dia durante 20 minutos**, recolheu sinais de movimento do punho e "
              "frequência cardíaca.")
INTRO_5_PT = ("- **dois** dispositivos de medição de **atividade elétrica muscular** (mBAN), colocados no trapézio esquerdo (esq.) e direito (dir.),"
              "programados para adquirir **quatro vezes por dia durante 20 minutos**.")
PLOT_EXPLAIN_PT = (
    "A figura abaixo apresenta o cronograma de aquisição dos sensores, com o objetivo de o relembrar o "
    "dos dias e horários em que decorreram as aquisições. Existe um gráfico por cada dia de aquisição, e cada gráfico "
    "contém barras horizontais que representam os períodos em que os quatro dispositivos (smartphone - cor verde, smartwatch - cor azul, "
    "mBAN direito - cor laranja escuro, mBAN esquerdo - cor laranja claro) recolheram dados. "
    "Caso existam aquisições em falta, é apresentada uma barra a cinzento no local onde a aquisição deveria ter ocorrido."
)

# ------------------------------------------------------------------------------------------------------------------- #
# english
# ------------------------------------------------------------------------------------------------------------------- #
# no need to do this now, I'll translate the texts at a later stage
INTRO_ENG = ""
PLOT_ENG = ""

# ------------------------------------------------------------------------------------------------------------------- #
# text dictionary
# ------------------------------------------------------------------------------------------------------------------- #
SENSOR_TIMELINE_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT, INTRO_5_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_PT],
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}