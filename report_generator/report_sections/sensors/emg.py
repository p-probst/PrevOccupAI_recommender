from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_EMG_PT = "Sensor de atividade muscular (EMG)"
INTRO_2_EMG_PT = (
    "Os sinais de **atividade muscular (EMG)** foram recolhidos ao longo do turno de trabalho, "
    "com o objetivo de **avaliar o esforço realizado pelos músculos trapézios**. "
    "Este tipo de medição permite perceber quando o músculo está em repouso, em atividade ligeira "
    "ou sujeito a esforço mais intenso e prolongado."
)
INTRO_3_EMG_PT = (
    "Para que os valores possam ser comparados entre diferentes trabalhadores, a atividade muscular "
    "é expressa em **percentagem de uma contração máxima voluntária**, tendo esta sido adquirida todos os dias no início do turno. "
    "Isto significa que a **atividade muscular de cada pessoa é avaliada em relação à sua própria força máxima**, "
    "permitindo uma interpretação mais justa e personalizada."
)
INTRO_4_EMG_PT = (
    "Durante o trabalho, o músculo alterna naturalmente entre momentos de atividade e momentos de repouso. "
    "Valores muito baixos de atividade muscular correspondem a repouso ou relaxamento, "
    "enquanto valores mais elevados indicam esforço muscular. "
    "Para esta análise, considera-se que o músculo está ativo quando a atividade ultrapassa 0,5 % da força máxima."
)
INTRO_5_EMG_PT = (
    "Para compreender melhor se o esforço muscular é leve, normal ou excessivo para cada trabalhador, "
    "a atividade muscular foi classificada em níveis de intensidade relativa. "
    "Esta classificação não compara pessoas entre si, mas sim cada trabalhador consigo próprio, "
    "tendo como referência o seu padrão habitual de atividade ao longo da semana."
)
INTRO_6_EMG_PT = (
    "A análise é feita em pequenos intervalos de tempo (5 segundos) e indica quanto tempo o músculo "
    "esteve em diferentes níveis de esforço, considerando apenas os períodos em que o músculo esteve ativo. "
    "Foram definidas as seguintes classes:"
)
INTRO_7_EMG_PT = "- **Abaixo do habitual**: esforço muscular inferior ao normalmente observado para essa pessoa. Corresponde a trabalho leve."
INTRO_8_EMG_PT = "- **Habitual – Típico baixo**: esforço dentro do seu padrão normal, mas no intervalo mais baixo de intensidade."
INTRO_9_EMG_PT = "- **Habitual – Típico alto**: esforço ainda considerado normal para si, mas mais próximo do seu limite habitual."
INTRO_10_EMG_PT = (
    "- **Alto para si**: esforço muscular acima do que é habitual para si. "
    "A permanência prolongada neste nível pode indicar sobrecarga muscular e maior risco de fadiga ou desconforto."
)

RISK_PT = "Em relação aos figuras da atividade muscular alongo dos dias, foi delineado o seguinte risco:"

PLOT_EXPLAIN_1_PT = ("O gráfico que se segue apresenta uma visão geral semanal da intensidade relativa da atividade "
                     "muscular nos ombros (trapézios) esquerdo e direito. **Cada linha corresponde a uma sessão de trabalho**, "
                     "identificada pelo horário, e mostra a **percentagem do tempo em que o músculo esteve ativo**, "
                     "distribuída pelos diferentes níveis de esforço. "
                     "As cores representam o quão intenso foi o esforço em relação ao padrão habitual da própria pessoa."
                     " De um modo geral, estão previstas quatro sessões de aquisição por dia, no entanto, em alguns casos, "
                     "podem ocorrer falhas nos dispositivos, resultando em dados em falta. "
                     "Sempre que a informação de um dos lados (esquerdo ou direito) não esteja disponível numa determinada sessão, "
                     "essa ausência é assinalada através de uma barra a cinzento. Caso os dados de um dos lados estejam em falta "
                     "ao longo de todo o dia, não é apresentada qualquer informação para esse lado nesse dia. "
                     "Quando não existem dados disponíveis para ambos os lados numa sessão de trabalho, essa sessão não é "
                     "representada no gráfico."
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
EMG_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_EMG_PT, INTRO_2_EMG_PT, INTRO_3_EMG_PT, INTRO_4_EMG_PT, INTRO_5_EMG_PT, INTRO_6_EMG_PT,
                           INTRO_7_EMG_PT, INTRO_8_EMG_PT, INTRO_9_EMG_PT, INTRO_10_EMG_PT],
        RISK_RULE_KEY: [RISK_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}