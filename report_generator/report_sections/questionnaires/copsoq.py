from constants import PT, ENG, INTRODUCTION_KEY, RISK_RULE_KEY, PLOT_EXPLAIN_KEY

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #
MUEQ_EXPLAIN_KEY = f'mueq_{PLOT_EXPLAIN_KEY}'
COPSOQ_EXPLAIN_KEY = f'copsoq_{PLOT_EXPLAIN_KEY}'
# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_1_PT = "Avaliação Psicossocial"
INTRO_2_PT = (
    "Os fatores psicossociais permitem avaliar as interações entre o ambiente de trabalho, o conteúdo das tarefas, "
    "as condições organizacionais e as características pessoais extralaborais dos trabalhadores, que podem "
    "influenciar a saúde, a produtividade e a satisfação profissional. Para isto, foram utilizados dois questionários validados: COPSOQ e MUEQ."
    "COPSOQ (*Copenhagen Psychosocial Questionnaire*) é um instrumento científico internacionalmente reconhecido para avaliar e "
    "melhorar os fatores psicossociais no local de trabalho. MUEQ (*Maastricht Upper Extremity Questionnaire*) é um questionário utilizado "
    "para avaliar lesões musculoesqueléticas. No contexto deste estudo, MUEQ foi utilizado para avaliar a qualidade das pausas.  "
)
INTRO_3_PT = (
"A avaliação psicossocial é realizada ao nível do grupo, o que significa que os resultados apresentados neste "
    "relatório correspondem a valores médios de toda a população que participou no estudo, e não a valores individuais. "
    "Deste modo, não serão apresentadas recomendações individuais, mas apenas recomendações de natureza organizacional "
    "dirigidas à CML. Nesta secção são apresentadas quatro visualizações com os resultados da avaliação psicossocial da população do estudo."
)
RISK_PT = (
    "A cada tópico está associado uma cor que representa o nível de risco identificado. "
    "A cor verde indica baixo risco, a cor amarela sinaliza a existência de algum risco, "
    "e a cor vermelha corresponde a um risco elevado. "
)
PLOT_EXPLAIN_1_PT = (
    "Os dois primeiros gráficos mostram os resultados do questionário COPSOQ para toda a população e para os "
    "trabalhadores com o mesmo tipo de função, nomeadamente ‘front office’ e ‘back office’. "
    "A tabela abaixo mostra as diferentes dimensões do questionário, numeradas conforme a figura dos resultados. "
)
PLOT_EXPLAIN_1_1_PT  = "1. Exigências cognitivas"
PLOT_EXPLAIN_1_2_PT  = "2. Ritmo de trabalho"
PLOT_EXPLAIN_1_3_PT  = "3. Exigências quantitativas"
PLOT_EXPLAIN_1_4_PT  = "4. Exigências emocionais"
PLOT_EXPLAIN_1_5_PT  = "5. Influência no trabalho"
PLOT_EXPLAIN_1_6_PT  = "6. Possibilidade de desenvolvimento"
PLOT_EXPLAIN_1_7_PT  = "7. Significado do trabalho"
PLOT_EXPLAIN_1_8_PT  = "8. Compromisso com o local de trabalho"
PLOT_EXPLAIN_1_9_PT  = "9. Previsibilidade"
PLOT_EXPLAIN_1_10_PT = "10. Recompensas"
PLOT_EXPLAIN_1_11_PT = "11. Clareza do papel desempenhado"
PLOT_EXPLAIN_1_12_PT = "12. Conflitos de papéis laborais"
PLOT_EXPLAIN_1_13_PT = "13. Apoio social dos colegas"
PLOT_EXPLAIN_1_14_PT = "14. Apoio social das chefias"
PLOT_EXPLAIN_1_15_PT = "15. Qualidade da liderança"
PLOT_EXPLAIN_1_16_PT = "16. Confiança horizontal"
PLOT_EXPLAIN_1_17_PT = "17. Confiança vertical"
PLOT_EXPLAIN_1_18_PT = "18. Justiça e respeito"
PLOT_EXPLAIN_1_19_PT = "19. Comunicação no trabalho"
PLOT_EXPLAIN_1_20_PT = "20. Comportamentos ofensivos"
PLOT_EXPLAIN_1_21_PT = "21. Insegurança laboral"
PLOT_EXPLAIN_1_22_PT = "22. Conflito trabalho/família"
PLOT_EXPLAIN_1_23_PT = "23. Satisfação laboral"
PLOT_EXPLAIN_1_24_PT = "24. Saúde geral"
PLOT_EXPLAIN_1_25_PT = "25. Problemas de sono"
PLOT_EXPLAIN_1_26_PT = "26. Burnout"
PLOT_EXPLAIN_1_27_PT = "27. Stress"
PLOT_EXPLAIN_1_28_PT = "28. Sintomas depressivos"
PLOT_EXPLAIN_1_29_PT = "29. Autoeficácia"
PLOT_EXPLAIN_2_PT = ("Os restantes dois gráficos mostram os resultados do questionário MUEQ para toda a população do estudo "
                     "e para os trabalhadores do mesmo tipo de função, nomeadamente 'front office' e 'back office'. "
                     "A tabela abaixo mostra as diferentes dimensões do questionário, numeradas conforme a figura dos resultados."
)
PLOT_EXPLAIN_2_1_PT = "1. Autonomia"
PLOT_EXPLAIN_2_2_PT = "2. Qualidade das pausas"
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
        INTRODUCTION_KEY: [INTRO_1_PT, INTRO_2_PT, INTRO_3_PT],
        RISK_RULE_KEY: [RISK_PT],
        COPSOQ_EXPLAIN_KEY: [
            PLOT_EXPLAIN_1_PT,
            PLOT_EXPLAIN_1_1_PT,
            PLOT_EXPLAIN_1_2_PT,
            PLOT_EXPLAIN_1_3_PT,
            PLOT_EXPLAIN_1_4_PT,
            PLOT_EXPLAIN_1_5_PT,
            PLOT_EXPLAIN_1_6_PT,
            PLOT_EXPLAIN_1_7_PT,
            PLOT_EXPLAIN_1_8_PT,
            PLOT_EXPLAIN_1_9_PT,
            PLOT_EXPLAIN_1_10_PT,
            PLOT_EXPLAIN_1_11_PT,
            PLOT_EXPLAIN_1_12_PT,
            PLOT_EXPLAIN_1_13_PT,
            PLOT_EXPLAIN_1_14_PT,
            PLOT_EXPLAIN_1_15_PT,
            PLOT_EXPLAIN_1_16_PT,
            PLOT_EXPLAIN_1_17_PT,
            PLOT_EXPLAIN_1_18_PT,
            PLOT_EXPLAIN_1_19_PT,
            PLOT_EXPLAIN_1_20_PT,
            PLOT_EXPLAIN_1_21_PT,
            PLOT_EXPLAIN_1_22_PT,
            PLOT_EXPLAIN_1_23_PT,
            PLOT_EXPLAIN_1_24_PT,
            PLOT_EXPLAIN_1_25_PT,
            PLOT_EXPLAIN_1_26_PT,
            PLOT_EXPLAIN_1_27_PT,
            PLOT_EXPLAIN_1_28_PT,
            PLOT_EXPLAIN_1_29_PT,
        ],
        MUEQ_EXPLAIN_KEY: [PLOT_EXPLAIN_2_PT, PLOT_EXPLAIN_2_1_PT, PLOT_EXPLAIN_2_2_PT]
    },

    ENG: {
        INTRODUCTION_KEY: {INTRO_ENG},
        RISK_RULE_KEY: {RISK_ENG},
        PLOT_EXPLAIN_KEY: {PLOT_ENG},
    }
}
