# ------------------------------------------------------------------------------------------------------------------- #
# questionnaire mappings
# ------------------------------------------------------------------------------------------------------------------- #

# Maps internal ROSA metric keys to human-readable dimension labels per language.
ROSA_MAPPING = {
    "score_a_adapted":       {"pt": "Cadeira",  "eng": "Chair"},
    "monitor_adapted_norm":  {"pt": "Monitor",  "eng": "Monitor"},
    "phone_adapted_norm":    {"pt": "Telefone", "eng": "Phone"},
    "mouse_adapted_norm":    {"pt": "Rato",     "eng": "Mouse"},
    "keyboard_adapted_norm": {"pt": "Teclado",  "eng": "Keyboard"},
    "final_normalized":      {"pt": "ROSA Score", "eng": "ROSA Score"},
}

# no recommendations for office privacy (privacidade do escritório) thus they are omitted
ENVIRONMENT_MAPPING = {
    "Nível de Iluminação":       {"pt": "Nível de Iluminação",       "eng": "Lighting Level"},
    "Ar":                        {"pt": "Ar",                        "eng": "Air"},
    "Ruído":                     {"pt": "Ruído",                     "eng": "Noise"},
    "Design do Escritório":      {"pt": "Design do Escritório",      "eng": "Office Design"},
    "Organização do Escritório": {"pt": "Organização do Escritório", "eng": "Office Organisation"}
}


# ------------------------------------------------------------------------------------------------------------------- #
# sensor mappings
# ------------------------------------------------------------------------------------------------------------------- #
# TODO: for now only english is implemented. Therefore, at the moment all values are the same for the code to work
EMG_MAPPING = {

    "typical_high_pct": {"pt": "typical_high_pct", "eng": "typical_high_pct"},
    "high_for_you_pct": {"pt": "high_for_you_pct", "eng": "high_for_you_pct"},
    "typical_low_pct": {"pt": "typical_low_pct", "eng": "typical_low_pct"},
    "below_usual_pct": {"pt": "below_usual_pct", "eng": "below_usual_pct"},

}

HEART_RATE_MAPPING = {

    "max": {"pt": "max", "eng": "max"},
    "Ligeiramente elevado": {"pt": "Ligeiramente elevado", "eng": "Slightly elevated"},
    "Elevado": {"pt": "Elevado", "eng": "Elevated"},
    "Normal": {"pt": "Normal", "eng": "Normal"},
    "min": {"pt": "min", "eng": "min"},
    "mean": {"pt": "mean", "eng": "mean"},
    "Sem dados": {"pt": "Sem dados", "eng": "No data"},
}

HAR_MAPPING = {

    "Sentado": {"pt": "Sentado", "eng": "Sitting"},
    "De pé": {"pt": "De pé", "eng": "Standing"},
    "Sentado_duration_sec": {"pt": "Sentado_duration_sec", "eng": "sitting_duration_sec"},
    "num_steps": {"pt": "num_steps", "eng": "num_steps"},
    "Andar": {"pt": "Andar", "eng": "Walking"},
}

NOISE_MAPPING = {
    "Ruído incomodativo": {"pt": "Ruído incomodativo", "eng": "Disruptive noise"},
    "Ruído elevado": {"pt": "Ruído elevado", "eng": "High noise"},
    "Ruído_cronograma_cjan_10": {"pt": "Ruído_cronograma_cjan_10", "eng": "Noise_timeline_wlen-10"}
}

# TODO: for now only english is implemented. Therefore, at the moment all values are the same for the code to work
POSTURE_MAPPING = {

    "posture_95_confidence_ellipse_area": {"pt": "posture_95_confidence_ellipse_area", "eng": "posture_95_confidence_ellipse_area"},
    "posture_ap_range": {"pt": "posture_ap_range", "eng": "posture_ap_range"},
    "posture_ml_range": {"pt": "posture_ml_range", "eng": "posture_ml_range"},

}

