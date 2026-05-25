# ------------------------------------------------------------------------------------------------------------------- #
# project constants
# ------------------------------------------------------------------------------------------------------------------- #
PT = 'pt'
ENG = 'eng'

USER = 'phill'


# general file keys
INTRODUCTION_KEY = 'intro_and_context'
RISK_RULE_KEY = 'risk_rule'
PLOT_EXPLAIN_KEY = 'plot_explain'


# recommendation keys for generated recommendations
RISK_DATES_KEY = 'risk_dates'
NUM_INSTANCES_KEY = 'num_instances'
RECOMMENDATIONS_KEY = 'recommendation'
RULE_KEY = 'rule'
RISK_DIMENSIONS_KEY = 'risk_dimensions' # only for questionnaire related risks

# general keys for recommendations.json
SENSORS_KEY = 'sensors'

# no recommendations
NO_RECOMMENDATIONS = {
    PT: "Boas notícias: Não se detetaram situações de risco.",
    ENG: "Good news: No risk situations were detected."
}

# pain questionnaire
VIABLE_PAIN_DIMENSIONS = ["localização", "tempo", "incapacidade", "sofrimento", "intensidade", "perceção"]

# colors for plotting
BO_COLOR = "#4d92d0"
FO_COLOR = "#06171c"
# work type colors
WORK_TYPE_COLORS = {'FO': FO_COLOR, 'BO': BO_COLOR}
EDGE_COLOR = "#222e35"

GREEN = "#81C784"
PALE_GREEN = "#A5D6A7"
STRONG_GREEN = "#3F8D43"
YELLOW = "#FFCC80"
RED = "#EF9A9A"
DEEP_RED = '#FF6A60'
LIGHT_RED = '#F8C1C1'
BLUE_STATE = '#7391AB'
SALMON = '#F19C93'
LIGHT_GRAY = '#E0E0E0'
GRAY = '#B0B0B0'

# work types order
WORK_TYPES = ['FO', 'BO']

FILE_FORMAT = '.png'

