from constants import PT, ENG


# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #
TITLE_KEY = 'title'
SUB_TITLE_Q_KEY = 'sub_title_q'
SUB_TITLE_S_KEY = 'sub_title_s'
SECTION_1_KEY = 'section_1'
SECTION_2_KEY = 'section_2'

# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
SUMMARY_TITLE = "Resumo"

SUMMARY_QUESTIONNAIRES = "Resultados dos seus questionários"

SUMMARY_SENSORS = "Resultados das suas acquisições"

SUMMARY_1_PT = ("As tabelas seguintes apresentam um resumo dos principais indicadores de saúde ocupacional avaliados ao "
                "longo do período de monitorização. Para cada métrica, são sintetizadas as regras de risco consideradas, "
                "a incidência das situações detetadas, os dias em que ocorreram e as respetivas recomendações.")

SUMMARY_2_PT = ("Este resumo foi pensado para te dar uma visão rápida e integrada dos resultados, ajudando a identificar "
                "de forma simples potenciais fatores de risco e áreas que podem merecer maior atenção. Para uma análise "
                "mais detalhada de cada métrica e do respetivo contexto, recomenda-se a consulta das "
                "secções anteriores do relatório.")
# ------------------------------------------------------------------------------------------------------------------- #
# english
# ------------------------------------------------------------------------------------------------------------------- #
# no need to do this now, I'll translate the texts at a later stage

# ------------------------------------------------------------------------------------------------------------------- #
# text dictionary
# ------------------------------------------------------------------------------------------------------------------- #
SUMMARY_DICT = {
    PT: {
        TITLE_KEY: SUMMARY_TITLE,
        SUB_TITLE_Q_KEY: SUMMARY_QUESTIONNAIRES,
        SUB_TITLE_S_KEY: SUMMARY_SENSORS,
        SECTION_1_KEY: SUMMARY_1_PT,
        SECTION_2_KEY: SUMMARY_2_PT
    },

    ENG: {
        'section1': "",
        'section2': "",
    }
}