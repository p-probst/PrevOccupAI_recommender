from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Sensores de movimento: estabilidade e variabilidade da postura sentada"

INTRO_2_PT = (
    "O trabalho de escritório implica, na maioria dos casos, permanecer sentado durante longos períodos de tempo. "
    "Tradicionalmente, o **trabalho em postura sentada é considerado prejudicial** quando realizado de **forma muito estática**, "
    "ou seja, quando a pessoa permanece muito tempo na mesma posição. Este tipo de trabalho está associado a sobrecarga "
    "da coluna vertebral, sobretudo quando realizado em posturas não fisiológicas ou sem um bom apoio lombar, o que pode "
    "condicionar toda a postura até à cabeça."
)

INTRO_3_PT = (
    "Estudos científicos recentes mostram que o corpo humano não foi concebido para permanecer imóvel durante longos "
    "períodos. Pelo contrário, **pequenas variações naturais da postura** — mesmo quando estamos sentados — são **consideradas saudáveis** "
    "e fazem parte de um bom controlo postural. Estas pequenas mudanças ajudam a distribuir melhor as cargas "
    "sobre a coluna e os músculos, reduzindo a fadiga e o desconforto."
)

INTRO_4_PT = (
    "Para avaliar este comportamento, foram utilizados dados de **movimento recolhidos pelo smartphone colocado no tronco**. "
    "A partir destes dados, foi possível **estimar o deslocamento do tronco** enquanto se encontrava em posição sentada, "
    "permitindo analisar a forma como a postura varia ao longo do tempo durante o trabalho."
)

INTRO_5_PT = (
    "Um dos **indicadores analisados** foi a área da elipse de confiança a 95%. De forma simples, este valor representa a área onde ocorrem a **maioria (95%) dos pequenos movimentos** "
    "do tronco durante o período analisado. Valores mais elevados indicam maior variabilidade postural, enquanto valores "
    "muito baixos podem refletir uma postura excessivamente rígida "
    "ou estática."
)

INTRO_6_PT = (
    "A evidência científica sugere que uma postura demasiado fixa ao longo do dia está associada a maior risco de dor e "
    "desconforto na coluna, enquanto uma postura com alguma variabilidade — caracterizada por pequenos ajustes frequentes — "
    "está associada a um melhor controlo postural e menor risco músculo-esquelético. Assim, alguma variabilidade não é um "
    "sinal negativo, mas sim um comportamento natural e desejável."
)

INTRO_7_PT = (
    "A análise da variabilidade da postura sentada permite, deste modo, identificar padrões potencialmente associados a "
    "trabalho excessivamente estático. Esta informação pode apoiar a adoção de estratégias preventivas simples, como "
    "ajustes ergonómicos, mudanças regulares de posição e pausas ativas, contribuindo para a proteção da coluna e para o "
    "bem-estar geral ao longo do dia de trabalho."
)

RISK_PT = "Em relação aos figuras do movimento do tronco ao longo do dia, foi delineado o seguinte risco:"

PLOT_EXPLAIN_1_PT = (
    "A figura apresenta, numa única visualização, os pequenos movimentos do tronco enquanto esteve sentada/o "
    "ao longo dos diferentes dias de trabalho. Cada linha da figura corresponde a um dia da semana, e cada "
    "coluna representa uma perspetiva diferente do tronco: vista superior, vista lateral e vista das costas. "
    "Os pontos representam posições do tronco registadas pelos sensores, sendo que as zonas mais escuras indicam "
    "as posições onde permaneceu durante mais tempo, enquanto as zonas mais claras correspondem a posições "
    "ocupadas de forma mais breve. Desta forma, a intensidade da cor permite compreender não só o movimento, "
    "mas também o tempo passado em cada posição. De um modo geral, a dispersão dos pontos e a variação das cores "
    "refletem a variabilidade da postura ao longo do dia."
)

PLOT_EXPLAIN_2_PT = (
    "- **Na vista superior**, é possível observar em conjunto os movimentos para a frente/trás e para os lados, oferecendo uma visão global "
    "da forma como a postura variou ao longo do tempo."
)


PLOT_EXPLAIN_3_PT = (
    "- **Na vista lateral**, são representados os movimentos do tronco para a frente e para trás. Estas variações refletem ajustes naturais "
    "da postura durante o trabalho, como inclinar-se ligeiramente para a frente ou endireitar o tronco."
)

PLOT_EXPLAIN_4_PT = (
    "- **Na vista de costas**, é possível observar os movimentos do tronco para a esquerda e para a direita, ou seja, os ajustes laterais "
    "da postura enquanto trabalha sentada/o, permitindo identificar possíveis assimetrias na postura ao longo do dia."
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
POSTURE_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT, INTRO_5_PT, INTRO_6_PT, INTRO_7_PT],
        RISK_RULE_KEY: [RISK_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT, PLOT_EXPLAIN_2_PT, PLOT_EXPLAIN_3_PT, PLOT_EXPLAIN_4_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}