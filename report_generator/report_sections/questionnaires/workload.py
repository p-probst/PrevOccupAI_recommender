from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Registo diário da carga de trabalho"

INTRO_2_PT = (
    "O trabalho de escritório pode envolver não apenas exigências físicas, mas também uma carga significativa "
    "de exigência mental e organizacional. Fatores como a necessidade de concentração prolongada, pressão temporal, "
    "interrupções frequentes e elevada quantidade de tarefas podem contribuir para o aumento do esforço diário "
    "perceptido pelo trabalhador."
)

INTRO_3_PT = (
    "De forma a avaliar a perceção da carga de trabalho ao longo da semana, "
    "os trabalhadores preencheram diariamente um questionário de autoavaliação no final de cada dia de trabalho. "
    "O questionário avaliou aspetos relacionados com o esforço mental e a concentração exigidos, "
    "a sensação de pressão ou urgência ao longo do dia, o impacto de interrupções frequentes na realização das tarefas, "
    "a relação entre o esforço investido e os recursos ou apoio disponíveis, "
    "bem como a perceção global da carga de trabalho diária."
)

INTRO_4_PT = (
    "As respostas foram registadas através de uma escala de 5 pontos, "
    "que varia entre \"discordo completamente\" e \"concordo completamente\". "
    "Este tipo de escala é amplamente utilizado em contextos ocupacionais, "
    "por permitir uma avaliação simples e intuitiva da perceção subjetiva do trabalhador."
)
INTRO_5_PT = (
    "A informação apresentada serve para ajudar a compreender a intensidade da carga de trabalho subjetiva durante a semana das aquisições. "
    "Esta informação será utilizada em conjunto com os dados dos sensores, nomeadamente de  "
    "frequência cardíaca e atividade muscular, com o objetivo de identificar possíveis "
    "situações de stress ao longo de cada dia de trabalho e assim gerar recomendações personalizadas. "
)

PLOT_1_PT = (
    "O gráfico apresentado resume as respostas ao questionário diário de carga de trabalho ao longo da semana. "
    "Cada painel corresponde a um dia de trabalho, permitindo comparar a exigência e carga de trabalho nos diferentes dias da semana. "
)

PLOT_2_PT = (
    "No eixo vertical encontram-se as opções de resposta, que variam entre \"discordo completamente\" "
    "e \"concordo completamente\". No eixo horizontal estão representadas as cinco afirmações avaliadas, "
    "relacionadas com esforço mental, pressão, interrupções, relação entre esforço e recursos disponíveis "
    "e carga de trabalho global."
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
WORKLOAD_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT, INTRO_4_PT],
        RISK_RULE_KEY: [RISK_1_PT],
        PLOT_EXPLAIN_KEY: [PLOT_1_PT, PLOT_2_PT],
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}