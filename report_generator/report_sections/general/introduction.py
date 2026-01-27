from constants import PT, ENG

# ------------------------------------------------------------------------------------------------------------------- #
# file constants
# ------------------------------------------------------------------------------------------------------------------- #
SECTION_0 = 'section_0'
SECTION_1 = 'section_1'
SECTION_2 = 'section_2'
SECTION_3 = 'section_3'
SECTION_4 = 'section_4'
SECTION_5 = 'section_5'
SECTION_6 = 'section_6'
SECTION_7 = 'section_7'
SECTION_8 = 'section_8'
SECTION_9 = 'section_9'
SECTION_10 = 'section_10'
SECTION_11 = 'section_11'
SECTION_12 = 'section_12'
SECTION_13 = 'section_13'
# ------------------------------------------------------------------------------------------------------------------- #
# portuguese
# ------------------------------------------------------------------------------------------------------------------- #
SECTION_0_PT = "Relatório Ocupacional Individual - PrevOccupAI+"
SECTION_1_PT = ("Este relatório reporta os resultados das aquisições realizadas ao longo de "
                "uma semana, com informação anónima e individual. Estes dados irão ser agregados aos dados "
                "recolhidos restantes trabalhadores da Câmara Municipal de Lisboa que participaram no estudo, "
                "por forma a dar corpo ao conjunto final de dados do projeto PrevOccupAI+.")
SECTION_2_PT = (
    "As doenças músculo-esqueléticas são o problema de saúde mais frequentemente reportado pelos trabalhadores da União Europeia. "
    "O trabalho sedentário, a utilização prolongada de computadores e a falta de condições ergonómicas no espaço de trabalho têm contribuído "
    "para um aumento da prevalência destas doenças entre os trabalhadores de escritório. "
    "A estes fatores juntam-se ainda as elevadas exigências laborais, frequentemente combinadas com recursos limitados para a realização das tarefas, "
    "o que contribui para o desenvolvimento de problemas de natureza psicológica, como stress, ansiedade e depressão."
)
SECTION_3_PT = (
    "A elevada exposição a estes fatores de risco pode resultar em impactos negativos "
    "tanto para o trabalhador como para a entidade empregadora, tornando necessário o recurso a ferramentas "
    "de avaliação destes riscos. Para esse efeito, devem ser consideradas múltiplas influências, incluindo "
    "fatores relacionados com o local de trabalho e fatores individuais do trabalhador. "
    "A avaliação de indicadores fisiológicos ou de padrões de movimento através de sensores permite uma análise "
    "mais objetiva e individualizada dos fatores de risco, quando comparada com os questionários. "
    "Assim, torna-se fundamental a utilização combinada de ambos como instrumentos de medição para a quantificação "
    "dos fatores de risco para doenças ocupacionais."
)
SECTION_4_PT = (
    "Através da quantificação destes fatores, torna-se possível identificar os domínios em que é necessário "
    "intervir, tanto a nível individual como organizacional, com o objetivo de promover a saúde, "
    "a eficiência e o bem-estar dos colaboradores, assegurando um trabalho seguro, satisfatório e produtivo."
)
SECTION_5_PT = ("O projeto PrevOccupAI+, Prevenção de Doenças Ocupacionais na Administração Pública "
                         "baseado em Inteligência Artificial PLUS, pretende recolher e investigar associações entre "
                         "tais fatores, sugerindo recomendações a nível organizacional e individual para reduzir "
                         "a exposição a riscos associados a doenças ocupacionais. Os objetivos destas aquisições são: ")
SECTION_6_PT = "**1. Recolher dados biomecânicos, ambientais e psicossociais em contexto ocupacional.**"
SECTION_7_PT = "**2. Criar bases de dados ocupacionais. **"
SECTION_8_PT = "**3. Analisar dados recolhidos para a criação de modelos de risco ocupacional personalizados a cada indivíduo.**"
SECTION_9_PT = "**4. Informar o trabalhador sobre os riscos ocupacionais a que está exposto e fornecer recomendações personalizadas.**"
SECTION_10_PT = (
    "Neste relatório, partilhado exclusivamente com o participante, são apresentados os resultados dos "
    "questionários e das aquisições realizadas ao longo de uma semana de trabalho. Para os diferentes itens "
    "avaliados, são propostas recomendações personalizadas, de acordo com o risco identificado, "
    "que podem ser adotadas pelo participante na procura contínua de melhorar as suas condições de trabalho. "
    "Estas recomendações baseiam-se em publicações de organizações internacionais e em literatura científica "
    "assente no consenso de peritos."
)
SECTION_11_PT = (
        "Destas aquisições, serão partilhadas com a **entidade patronal** apenas **resultados coletivos e "
        "anonimizados**. Tendo em conta o papel significativo que a entidade patronal representa "
        "na redução de riscos ergonómicos, ser-lhes-ão também apresentadas medidas de prevenção a "
        "implementar.")
SECTION_12_PT = (
    "**Importante**: A informação apresentada neste documento destina-se exclusivamente à consulta pessoal do trabalhador. "
    "A **decisão de partilhar este documento é inteiramente sua**, não podendo, em circunstância "
    "alguma, ser exigida por terceiros, incluindo a entidade empregadora. "
    "Caso assim o entenda, encorajamos a utilização deste documento como suporte para reflexão pessoal ou para a discussão "
    "com colegas de trabalho e/ou profissionais de saúde, nomeadamente médicos ou outros técnicos especializados."
)
SECTION_13_PT = ("Caso tenha alguma(s) questão(ões) relativamente ao documento e/ou à informação nele contida, "
                         "é possível contactar-nos em: **biosignals.libphys@gmail.com**.")
# ------------------------------------------------------------------------------------------------------------------- #
# english
# ------------------------------------------------------------------------------------------------------------------- #
# no need to do this now, I'll translate the texts at a later stage
SECTION_1_ENG = ""
SECTION_2_ENG = ""

# ------------------------------------------------------------------------------------------------------------------- #
# text dictionary
# ------------------------------------------------------------------------------------------------------------------- #
INTRO_DICT = {
    PT: {
        SECTION_0: SECTION_0_PT,
        SECTION_1: SECTION_1_PT, # please define the sections as constants as well
        SECTION_2: SECTION_2_PT,
        SECTION_3: SECTION_3_PT,
        SECTION_4: SECTION_4_PT,
        SECTION_5: SECTION_5_PT,
        SECTION_6: SECTION_6_PT,
        SECTION_7: SECTION_7_PT,
        SECTION_8: SECTION_8_PT,
        SECTION_9: SECTION_9_PT,
        SECTION_10: SECTION_10_PT,
        SECTION_11: SECTION_11_PT,
        SECTION_12: SECTION_12_PT,
        SECTION_13: SECTION_13_PT,
    },

    ENG: {
        'section1': {SECTION_1_ENG},
        'section2': {SECTION_2_ENG},
    }
}