"""
Base de données pharmaceutique pour réponses pré-définies
"""
PHARMA_DATABASE = {
    # Anti-ulcéreux et anti-acides
    "famotidine": {
        "name": "Famotidine (Famodine)",
        "class": "Antagoniste des récepteurs H2",
        "indications": [
            "Traitement des ulcères gastriques et duodénaux",
            "Réduction de l'acidité gastrique (reflux gastro-œsophagien)",
            "Prévention des ulcères de stress",
            "Traitement du syndrome de Zollinger-Ellison"
        ],
        "posology": "20-40 mg, 1 à 2 fois par jour selon l'indication",
        "side_effects": [
            "Troubles digestifs : nausées, diarrhée, constipation",
            "Maux de tête, vertiges",
            "Fatigue, somnolence",
            "Rarement : réactions allergiques, troubles hépatiques"
        ],
        "mechanism": "Inhibe les récepteurs H2 de l'histamine, réduisant ainsi la sécrétion d'acide gastrique"
    },
    "omeprazole": {
        "name": "Oméprazole",
        "class": "Inhibiteur de la pompe à protons (IPP)",
        "indications": [
            "Traitement des ulcères gastriques et duodénaux",
            "Reflux gastro-œsophagien",
            "Syndrome de Zollinger-Ellison",
            "Éradication de Helicobacter pylori"
        ],
        "posology": "20-40 mg par jour, généralement le matin à jeun",
        "side_effects": [
            "Troubles digestifs : nausées, diarrhée, constipation",
            "Maux de tête",
            "Rarement : carence en vitamine B12, fractures osseuses"
        ],
        "mechanism": "Inhibe de manière irréversible la pompe à protons (H+/K+-ATPase) dans les cellules pariétales gastriques"
    },
    
    # Antibiotiques
    "amoxicilline": {
        "name": "Amoxicilline",
        "class": "Antibiotique bêta-lactamine (pénicilline)",
        "indications": [
            "Infections respiratoires : pneumonie, bronchite, sinusite",
            "Infections urinaires : cystite, pyélonéphrite",
            "Infections cutanées et des tissus mous",
            "Infections dentaires et buccales",
            "Otite moyenne",
            "Infections gynécologiques"
        ],
        "posology": "Adultes : 500 mg à 1 g, 3 fois par jour. Enfants : 20-50 mg/kg/jour en 3 prises",
        "side_effects": [
            "Troubles digestifs : nausées, vomissements, diarrhée",
            "Réactions cutanées : éruptions, urticaire",
            "Réactions allergiques (plus rares) : anaphylaxie chez les personnes allergiques aux pénicillines",
            "Candidose buccale ou vaginale (surinfection fongique)"
        ],
        "mechanism": "Inhibe la synthèse de la paroi cellulaire bactérienne en se liant aux protéines de liaison aux pénicillines (PBP), entraînant la lyse et la mort des bactéries"
    },
    
    # Analgésiques et anti-inflammatoires
    "paracétamol": {
        "name": "Paracétamol (Acétaminophène)",
        "class": "Analgésique et antipyrétique",
        "indications": [
            "Douleur légère à modérée",
            "Fièvre",
            "Maux de tête",
            "Douleurs dentaires"
        ],
        "posology": "Adultes : 500-1000 mg, 3-4 fois par jour (max 4g/jour). Enfants : 10-15 mg/kg toutes les 4-6h",
        "side_effects": [
            "Rare aux doses thérapeutiques",
            "Surdosage : hépatotoxicité sévère, insuffisance hépatique"
        ],
        "mechanism": "Inhibe la cyclooxygénase (COX) dans le système nerveux central, réduisant la synthèse de prostaglandines impliquées dans la douleur et la fièvre"
    },
    "ibuprofene": {
        "name": "Ibuprofène",
        "class": "Anti-inflammatoire non stéroïdien (AINS)",
        "indications": [
            "Douleur légère à modérée",
            "Inflammation",
            "Fièvre",
            "Arthrite, rhumatismes"
        ],
        "posology": "200-400 mg, 3-4 fois par jour (max 1200-2400 mg/jour selon indication)",
        "side_effects": [
            "Troubles digestifs : nausées, douleurs abdominales, ulcères gastriques",
            "Maux de tête, vertiges",
            "Risque cardiovasculaire (à long terme)",
            "Insuffisance rénale (à fortes doses)"
        ],
        "mechanism": "Inhibe les enzymes COX-1 et COX-2, réduisant la synthèse de prostaglandines impliquées dans l'inflammation, la douleur et la fièvre"
    },
    
    # Antidiabétiques
    "metformine": {
        "name": "Metformine",
        "class": "Biguanide antidiabétique",
        "indications": [
            "Diabète de type 2",
            "Prévention du diabète de type 2 (chez patients à risque)"
        ],
        "posology": "500-1000 mg, 2-3 fois par jour (max 2550 mg/jour)",
        "side_effects": [
            "Troubles digestifs : nausées, diarrhée, goût métallique",
            "Acidose lactique (rare mais grave)",
            "Carence en vitamine B12 (à long terme)"
        ],
        "mechanism": "Réduit la production hépatique de glucose, améliore la sensibilité à l'insuline, et réduit l'absorption intestinale du glucose"
    },
    
    # Statines (hypolipémiants)
    "atorvastatine": {
        "name": "Atorvastatine",
        "class": "Statine (inhibiteur de l'HMG-CoA réductase)",
        "indications": [
            "Hypercholestérolémie",
            "Prévention des événements cardiovasculaires",
            "Syndrome coronarien aigu"
        ],
        "posology": "10-80 mg une fois par jour, généralement le soir",
        "side_effects": [
            "Douleurs musculaires, myopathie",
            "Troubles hépatiques (élévation des transaminases)",
            "Rarement : rhabdomyolyse",
            "Troubles digestifs"
        ],
        "mechanism": "Inhibe l'enzyme HMG-CoA réductase, réduisant ainsi la synthèse du cholestérol dans le foie et augmentant l'expression des récepteurs LDL"
    }
}

def get_drug_info(drug_name_lower: str):
    """Récupère les informations sur un médicament depuis la base de données"""
    # Recherche exacte
    if drug_name_lower in PHARMA_DATABASE:
        return PHARMA_DATABASE[drug_name_lower]
    
    # Recherche partielle
    for key, info in PHARMA_DATABASE.items():
        if key in drug_name_lower or drug_name_lower in key:
            return info
    
    return None

def generate_drug_response(drug_name_lower: str, question_type: str = "general"):
    """
    Génère une réponse sur un médicament basée sur la base de données
    
    question_type: "general", "mechanism", "side_effects", "posology", "indications"
    """
    drug_info = get_drug_info(drug_name_lower)
    
    if not drug_info:
        return None
    
    if question_type == "mechanism" or "fonctionne" in question_type or "mécanisme" in question_type:
        return f"{drug_info['name']} ({drug_info['class']})\n\n**Mécanisme d'action :**\n{drug_info['mechanism']}"
    
    elif question_type == "side_effects" or "effet" in question_type:
        effects = "\n".join([f"• {effect}" for effect in drug_info['side_effects']])
        return f"**Effets secondaires de {drug_info['name']} :**\n\n{effects}\n\nLes effets graves sont rares. En cas d'effets indésirables persistants, consultez un professionnel de santé."
    
    elif question_type == "posology" or "posologie" in question_type or "dosage" in question_type:
        return f"**Posologie de {drug_info['name']} :**\n\n{drug_info['posology']}\n\nLa posologie exacte doit être déterminée par un professionnel de santé selon l'indication, l'âge, le poids, et les conditions médicales du patient."
    
    elif question_type == "indications" or "indication" in question_type or "utilisé" in question_type:
        indications = "\n".join([f"• {ind}" for ind in drug_info['indications']])
        return f"**Indications de {drug_info['name']} :**\n\n{indications}"
    
    else:  # general
        indications = "\n".join([f"• {ind}" for ind in drug_info['indications']])
        effects = "\n".join([f"• {effect}" for effect in drug_info['side_effects'][:3]])  # Limiter à 3
        
        return f"{drug_info['name']} ({drug_info['class']})\n\n**Indications principales :**\n{indications}\n\n**Posologie typique :** {drug_info['posology']}\n\n**Effets secondaires fréquents :**\n{effects}\n\n**Mécanisme d'action :** {drug_info['mechanism']}\n\n⚠️ La posologie exacte doit être déterminée par un professionnel de santé."

