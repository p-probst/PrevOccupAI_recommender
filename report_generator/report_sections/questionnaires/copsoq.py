from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Avaliação Psicossocial"
INTRO_2_PT = (
    "Os fatores psicossociais permitem avaliar as interações entre o ambiente de trabalho, o conteúdo das tarefas, "
    "as condições organizacionais e as características pessoais extralaborais dos trabalhadores, que podem "
    "influenciar a saúde, a produtividade e a satisfação profissional. "
    "A avaliação psicossocial é realizada ao nível do grupo, o que significa que os resultados apresentados neste "
    "relatório correspondem a valores médios de toda a população que participou no estudo, e não a valores individuais. "
    "Deste modo, não serão apresentadas recomendações individuais, mas apenas recomendações de natureza organizacional "
    "dirigidas à CML."
)

RISK_PT = (
    "A cada tópico está associado uma cor que representa o nível de risco identificado. "
    "A cor verde indica baixo risco, a cor amarela sinaliza a existência de algum risco, "
    "e a cor vermelha corresponde a um risco elevado. "
)
PLOT_EXPLAIN_1_PT = (
    "São apresentadas quatro visualizações com os resultados da avaliação psicossocial da população do estudo. "
    "Os dois primeiros gráficos mostram os resultados do questionário COPSOQ para toda a população e para os "
    "trabalhadores com o mesmo tipo de função, nomeadamente ‘front office’ e ‘back office’. "
    "Da esquerda para a direita, são apresentados os resultados relativos às exigências cognitivas (1), ritmo de "
    "trabalho (2), exigências quantitativas (3), exigências emocionais (4), influência no trabalho (5), "
    "possibilidade de desenvolvimento (6), significado do trabalho (7), compromisso com o local de trabalho (8), "
    "previsibilidade (9), recompensas (10), clareza do papel desempenhado (11), conflitos de papéis laborais (12), "
    "apoio social dos colegas (13), apoio social das chefias (14), qualidade da liderança (15), confiança horizontal (16), "
    "confiança vertical (17), justiça e respeito (18), comunicação no trabalho (19), comportamentos ofensivos (20), "
    "insegurança laboral (21), conflito trabalho–família (22), satisfação laboral (23), saúde geral (24), "
    "problemas de sono (25), burnout (26), stresse (27), sintomas depressivos (28) e autoeficácia (29)."
)
PLOT_EXPLAIN_2_PT = ("Os restantes dois gráficos mostram os resultados do questionário MUEQ para toda a população do estudo"
                     "e para os trabalhadores do mesmo tipo de função, nomeadamente 'front office' e 'back office'. Da esquerda "
                     "para a direita são apresentados os resultados relativos à autonomia (1) e qualidade das pausas (2)."
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
COPSOQ_DICT = {
    PT: {
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT],
        RISK_RULE_KEY: [RISK_PT],
        PLOT_EXPLAIN_KEY: [PLOT_EXPLAIN_1_PT, PLOT_EXPLAIN_2_PT],
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG}
    }
}