from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Sensores de movimento: atividades realizadas durante o dia"
INTRO_2_PT = (
    "Devido à natureza do seu trabalho, os trabalhadores de escritório estão geralmente sujeitos a permanecer "
    "longos períodos de tempo sentados. O **trabalho estático e sedentário** encontra-se fortemente associado ao "
    "aparecimento de **lesões músculo-esqueléticas**, em particular na região lombar, no pescoço, nos ombros e nos joelhos. "
    "Para além destes problemas, a permanência prolongada em postura sentada pode também estar associada a outros "
    "efeitos negativos na saúde, como diabetes tipo 2, obesidade, doenças cardiovasculares e impactos na saúde mental. "

)
INTRO_3_PT = ("Deste modo, torna-se fundamental identificar situações de risco relacionadas com a postura sentada prolongada, "
    "de forma a permitir a adoção de medidas que contribuam para a melhoria da saúde do trabalhador. "
    "Uma das estratégias para prevenir estas doenças ocupacionais passa pela **promoção de práticas mais ativas ao longo "
    "do dia de trabalho**, reduzindo o tempo passado sentado e incentivando a realização de mais movimento.")

INTRO_4_PT = (
    "Para o estudo das atividades realizadas ao longo do dia de trabalho, foram desenvolvidos **modelos de inteligência artificial** que, "
    "com base nos dados dos sensores de movimento do smartphone, permitem distinguir entre **três atividades principais**: "
    "estar **sentado**, estar **de pé** e a **andar**. A partir desta informação, é possível determinar quanto tempo cada trabalhador "
    "passou em cada uma destas atividades e, assim, identificar possíveis padrões de risco."
)

INTRO_5_PT = ("A Organização Mundial da Saúde (OMS) recomenda que adultos realizem **pelo menos 4 mil passos por dia**. "
              "Esta quantidade é considerado o mínimo para evitar o sedentarismo. A **meta ideal**, para obter benefícios "
              "significativos para à saúde, situa-se entre **7 e 9 mil passos por dia**. Estudos indicam que este nível de "
              "atividade pode reduzir significativamente o risco de doenças crónicas e morte prematura. Sempre que "
              "possível, procure integrar este objetivo no seu dia a dia.")

RISK_1_PT = "Em relação ao cronograma das atividades ao longo do dia, foram delineados os seguinte riscos:"
RISK_2_PT = "Em relação à distribuição das atividades ao longo do dia, foram delineados os seguinte riscos:"
RISK_3_PT = "Em relação ao número de passoas realizados ao longo do dia, foram delineados o seguinte risco:"

PLOT_EXPLAIN_1_PT = (
    "Para cada dia de aquisição, foram construídos **cronogramas das atividades realizadas ao longo de todo o turno de trabalho**. "
    "As três barras horizontais representam os períodos em que esteve em **postura sentada (a verde)**, **de pé (a salmão)** e a **andar (a azul)**. "
    "Sempre que permaneceu sentada/o durante mais de uma hora consecutiva, a barra verde passa a amarelo. "
    "Caso a postura sentada se prolongue por mais de duas horas consecutivas sem interrupção, a barra passa a vermelho."
)
PLOT_EXPLAIN_2_PT = (
    "Segue-se o gráfico que apresenta a **distribuição das atividades** realizadas em cada dia da semana. "
    "Este gráfico permite compreender de forma mais intuitiva a proporção do tempo do seu dia de trabalho "
    "que passou sentada/o, de pé e a andar. "
    "A barra da esquerda mostra a percentagem que indicou no questionário relativamente ao tempo que considera "
    "passar em cada uma destas atividades. As barras à direita mostram os resultados obtidos a partir "
    "dos dados recolhidos pelos sensores. As percentagens de cada atividade estão escritas em cada barra, excepto percentagens menores que 2 %, que foram omitidas "
    "para facilitar a interpretação do gráfico."
)
PLOT_EXPLAIN_3_PT = (
    "O último gráfico apresentado relativamente às atividades corresponde ao **número de passos "
    "e da distância percorrida** por dia. A parte da barra a azul corresponde ao número de passos efetivamente realizados, enquanto que, a "
    "parte a cinzento, indica o número de passos recomendado para um dia inteiro. "
    "Este valor recomendado depende da sua idade e encontra-se indicado no topo do gráfico. "
    "A correspondente distância percorrida no respetivo dia, expressa em quilómetros (km), é apresentada à direita de cada barra."
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
HAR_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT, INTRO_5_PT],
        RISK_RULE_KEY: [RISK_1_PT, RISK_2_PT, RISK_3_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT, PLOT_EXPLAIN_2_PT, PLOT_EXPLAIN_3_PT],
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}