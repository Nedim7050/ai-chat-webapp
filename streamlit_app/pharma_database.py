"""
Base de données pharmaceutique complète pour réponses pré-définies
Couvre : Médicaments, Dispositifs médicaux, Essais cliniques, Réglementation, Pharmacovigilance, Biotechnologie
"""
import re

# ============================================================================
# 1. MÉDICAMENTS ET PRINCIPES ACTIFS
# ============================================================================
MEDICATIONS_DATABASE = {
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
    "penicilline": {
        "name": "Pénicilline",
        "class": "Antibiotique bêta-lactamine",
        "indications": [
            "Infections à streptocoques",
            "Syphilis",
            "Infections cutanées",
            "Prophylaxie de la fièvre rhumatismale"
        ],
        "posology": "Varie selon l'indication et la forme (orale, injectable)",
        "side_effects": [
            "Réactions allergiques (fréquentes)",
            "Diarrhée",
            "Nausées",
            "Rarement : anaphylaxie"
        ],
        "mechanism": "Inhibe la synthèse de la paroi cellulaire bactérienne en bloquant les enzymes de transpeptidation"
    },
    
    # Analgésiques et anti-inflammatoires
    "paracetamol": {
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

# ============================================================================
# 2. DISPOSITIFS MÉDICAUX (MedTech)
# ============================================================================
MEDICAL_DEVICES_DATABASE = {
    "dispositif_medical": {
        "definition": "Un dispositif médical est tout instrument, appareil, équipement, logiciel, implant, réactif, matériau ou autre article destiné par le fabricant à être utilisé, seul ou en association, chez l'homme à des fins médicales.",
        "classes": {
            "classe_i": {
                "name": "Classe I",
                "description": "Risque faible. Exemples : fauteuil roulant, béquilles, lunettes de vue",
                "conformite": "Auto-déclaration du fabricant"
            },
            "classe_iia": {
                "name": "Classe IIa",
                "description": "Risque moyen-faible. Exemples : lentilles de contact, appareils auditifs",
                "conformite": "Examen CE par un organisme notifié"
            },
            "classe_iib": {
                "name": "Classe IIb",
                "description": "Risque moyen-élevé. Exemples : préservatifs, seringues",
                "conformite": "Examen CE par un organisme notifié"
            },
            "classe_iii": {
                "name": "Classe III",
                "description": "Risque élevé. Exemples : implants cardiaques, stents coronariens, prothèses de hanche",
                "conformite": "Examen CE approfondi par un organisme notifié + évaluation clinique"
            }
        },
        "reglementation": {
            "europe": "Règlement (UE) 2017/745 (MDR - Medical Device Regulation)",
            "usa": "FDA 510(k) ou PMA (Pre-Market Approval)",
            "france": "ANSM (Agence Nationale de Sécurité du Médicament et des produits de santé)"
        },
        "marquage_ce": "Le marquage CE indique que le dispositif médical est conforme aux exigences essentielles de sécurité et de performance"
    },
    "implant": {
        "definition": "Dispositif médical implantable conçu pour être placé à l'intérieur ou à la surface du corps humain",
        "exemples": [
            "Implants cardiaques (pacemakers, défibrillateurs)",
            "Prothèses articulaires (hanche, genou)",
            "Stents coronariens",
            "Implants dentaires",
            "Implants mammaires"
        ],
        "surveillance": "Surveillance post-commercialisation obligatoire, traçabilité, registres d'implants"
    }
}

# ============================================================================
# 3. ESSAIS CLINIQUES ET RECHERCHE PHARMACEUTIQUE
# ============================================================================
CLINICAL_TRIALS_DATABASE = {
    "essai_clinique": {
        "definition": "Étude scientifique réalisée chez l'humain pour évaluer l'efficacité et la sécurité d'un médicament, dispositif médical, ou traitement",
        "phases": {
            "phase_i": {
                "name": "Phase I",
                "objectif": "Évaluer la sécurité et la tolérance",
                "participants": "20-100 volontaires sains ou patients",
                "duree": "Quelques mois",
                "focus": "Dosage, pharmacocinétique, effets secondaires"
            },
            "phase_ii": {
                "name": "Phase II",
                "objectif": "Évaluer l'efficacité préliminaire et la posologie",
                "participants": "100-300 patients",
                "duree": "Plusieurs mois à 2 ans",
                "focus": "Efficacité, dose optimale, effets secondaires"
            },
            "phase_iii": {
                "name": "Phase III",
                "objectif": "Confirmer l'efficacité et la sécurité",
                "participants": "1000-3000 patients ou plus",
                "duree": "1-4 ans",
                "focus": "Efficacité vs placebo/traitement standard, profil de sécurité complet"
            },
            "phase_iv": {
                "name": "Phase IV (Post-commercialisation)",
                "objectif": "Surveillance à long terme après autorisation",
                "participants": "Plusieurs milliers de patients",
                "duree": "Plusieurs années",
                "focus": "Effets secondaires rares, efficacité en conditions réelles"
            }
        },
        "methodologie": {
            "randomisation": "Répartition aléatoire des patients dans les groupes de traitement",
            "double_aveugle": "Ni le patient ni le médecin ne savent quel traitement est administré",
            "placebo_controle": "Comparaison avec un placebo (traitement inactif)",
            "groupe_temoin": "Groupe de patients recevant le traitement standard pour comparaison"
        },
        "reglementation": {
            "ich_gcp": "ICH-GCP (International Council for Harmonisation - Good Clinical Practice)",
            "fda": "FDA 21 CFR Part 50, 56 (Protection des sujets humains)",
            "ema": "Directive 2001/20/CE et Règlement (UE) 536/2014",
            "france": "Code de la santé publique, loi Huriet-Sérusclat"
        }
    },
    "endpoint": {
        "definition": "Critère d'évaluation mesuré dans un essai clinique pour déterminer l'efficacité d'un traitement",
        "types": {
            "primaire": "Critère principal d'évaluation (ex: survie globale, réduction des symptômes)",
            "secondaire": "Critères d'évaluation supplémentaires (ex: qualité de vie, biomarqueurs)",
            "surrogate": "Marqueur substitut (ex: pression artérielle comme substitut aux événements cardiovasculaires)"
        }
    }
}

# ============================================================================
# 4. RÉGLEMENTATION (FDA, EMA, ANSM)
# ============================================================================
REGULATION_DATABASE = {
    "fda": {
        "nom_complet": "Food and Drug Administration",
        "pays": "États-Unis",
        "role": "Agence fédérale réglementant les médicaments, dispositifs médicaux, aliments, et cosmétiques",
        "processus_amm": {
            "nda": "New Drug Application - pour nouveaux médicaments",
            "anda": "Abbreviated New Drug Application - pour médicaments génériques",
            "bla": "Biologics License Application - pour produits biologiques",
            "pma": "Pre-Market Approval - pour dispositifs médicaux de classe III",
            "510k": "510(k) - notification pré-commercialisation pour dispositifs médicaux"
        },
        "centers": [
            "CDER (Center for Drug Evaluation and Research) - Médicaments",
            "CDRH (Center for Devices and Radiological Health) - Dispositifs médicaux",
            "CBER (Center for Biologics Evaluation and Research) - Produits biologiques"
        ]
    },
    "ema": {
        "nom_complet": "European Medicines Agency",
        "pays": "Union Européenne",
        "role": "Agence européenne d'évaluation des médicaments",
        "processus_amm": {
            "centralisee": "Procédure centralisée - pour tous les États membres de l'UE",
            "decentralisee": "Procédure décentralisée - reconnaissance mutuelle",
            "mutuelle": "Procédure de reconnaissance mutuelle",
            "nationale": "Procédure nationale - pour un seul pays"
        },
        "comites": [
            "CHMP (Committee for Medicinal Products for Human Use) - Médicaments humains",
            "COMP (Committee for Orphan Medicinal Products) - Médicaments orphelins",
            "PDCO (Paediatric Committee) - Médicaments pédiatriques"
        ]
    },
    "ansm": {
        "nom_complet": "Agence Nationale de Sécurité du Médicament et des produits de santé",
        "pays": "France",
        "role": "Autorité compétente pour l'évaluation, l'autorisation et la surveillance des médicaments et dispositifs médicaux en France",
        "responsabilites": [
            "Autorisation de mise sur le marché (AMM) des médicaments",
            "Évaluation des dispositifs médicaux",
            "Pharmacovigilance et matériovigilance",
            "Inspection des établissements pharmaceutiques",
            "Contrôle de la publicité des médicaments"
        ],
        "processus_amm": "Dossier d'AMM soumis avec données précliniques, cliniques, et de fabrication"
    },
    "amm": {
        "definition": "Autorisation de Mise sur le Marché - autorisation administrative nécessaire pour commercialiser un médicament",
        "dossier": {
            "qualite": "Données sur la qualité du médicament (composition, fabrication, contrôle)",
            "securite": "Données précliniques (toxicologie, pharmacologie)",
            "efficacite": "Données cliniques (essais cliniques phases I, II, III)",
            "rmp": "Risk Management Plan - plan de gestion des risques"
        },
        "duree_validite": "5 ans renouvelable, puis illimitée après réévaluation"
    }
}

# ============================================================================
# 5. PHARMACOVIGILANCE ET SÉCURITÉ
# ============================================================================
PHARMACOVIGILANCE_DATABASE = {
    "pharmacovigilance": {
        "definition": "Science et activités relatives à la détection, l'évaluation, la compréhension et la prévention des effets indésirables des médicaments",
        "objectifs": [
            "Détecter les effets indésirables rares ou à long terme",
            "Identifier les nouveaux risques",
            "Évaluer le rapport bénéfice/risque",
            "Prendre des mesures correctives (modification notice, restriction, retrait)"
        ],
        "signalement": {
            "qui": "Professionnels de santé, patients, fabricants",
            "quoi": "Tout effet indésirable suspecté",
            "comment": "Formulaire de déclaration (ANSM, EMA, FDA)",
            "delai": "Sous 15 jours pour les effets graves"
        },
        "effets_indesirables": {
            "graves": "Effets mettant en danger la vie, nécessitant une hospitalisation, causant une invalidité, ou entraînant la mort",
            "non_graves": "Effets ne répondant pas aux critères de gravité",
            "inattendus": "Effets non mentionnés dans la notice du médicament"
        }
    },
    "materiovigilance": {
        "definition": "Surveillance des incidents et risques liés aux dispositifs médicaux",
        "objectifs": [
            "Détecter les dysfonctionnements des dispositifs médicaux",
            "Identifier les risques pour la sécurité des patients",
            "Prendre des mesures correctives (rappel, modification, retrait)"
        ]
    },
    "rapport_benefice_risque": {
        "definition": "Évaluation comparative des bénéfices thérapeutiques attendus et des risques associés à un médicament",
        "facteurs": [
            "Gravité de la maladie traitée",
            "Efficacité du traitement",
            "Fréquence et gravité des effets indésirables",
            "Alternatives thérapeutiques disponibles"
        ]
    }
}

# ============================================================================
# 6. BIOTECHNOLOGIE PHARMACEUTIQUE
# ============================================================================
BIOTECH_DATABASE = {
    "biotechnologie": {
        "definition": "Utilisation d'organismes vivants ou de leurs composants pour produire des médicaments ou des technologies médicales",
        "applications": [
            "Production de médicaments biologiques (protéines recombinantes, anticorps monoclonaux)",
            "Thérapies géniques",
            "Thérapies cellulaires",
            "Vaccins recombinants"
        ]
    },
    "medicament_biologique": {
        "definition": "Médicament produit à partir de sources biologiques (cellules, organismes vivants)",
        "exemples": [
            "Insuline recombinante",
            "Anticorps monoclonaux (trastuzumab, rituximab)",
            "Hormones de croissance",
            "Facteurs de coagulation",
            "Vaccins (hépatite B, HPV)"
        ],
        "caracteristiques": {
            "complexite": "Molécules complexes, difficiles à caractériser complètement",
            "variabilite": "Variabilité naturelle du processus de production",
            "immunogenicite": "Risque de réactions immunitaires"
        }
    },
    "biosimilaire": {
        "definition": "Médicament biologique similaire à un médicament biologique de référence déjà autorisé",
        "exigences": {
            "similarite": "Similitude démontrée en termes de qualité, sécurité et efficacité",
            "etudes": "Études comparatives avec le médicament de référence",
            "immunogenicite": "Évaluation spécifique de l'immunogénicité"
        },
        "avantages": [
            "Réduction des coûts",
            "Accès élargi aux traitements",
            "Concurrence sur le marché"
        ]
    },
    "therapie_genique": {
        "definition": "Technique thérapeutique consistant à introduire du matériel génétique dans les cellules d'un patient pour traiter une maladie",
        "approches": [
            "Remplacement de gène défectueux",
            "Inactivation de gène pathogène",
            "Introduction de nouveau gène thérapeutique"
        ],
        "vecteurs": [
            "Virus modifiés (adénovirus, lentivirus, AAV)",
            "Vecteurs non viraux (liposomes, nanoparticules)"
        ],
        "applications": [
            "Maladies génétiques rares",
            "Cancers",
            "Maladies dégénératives"
        ]
    },
    "therapie_cellulaire": {
        "definition": "Utilisation de cellules vivantes comme traitement médical",
        "types": {
            "cellules_souches": "Cellules souches hématopoïétiques pour greffes de moelle osseuse",
            "car_t": "CAR-T cells (Chimeric Antigen Receptor T-cells) pour cancers",
            "cellules_mesenchymateuses": "Cellules mésenchymateuses pour réparation tissulaire"
        }
    }
}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_drug_info(drug_name_lower: str):
    """Récupère les informations sur un médicament depuis la base de données"""
    # Recherche exacte
    if drug_name_lower in MEDICATIONS_DATABASE:
        return MEDICATIONS_DATABASE[drug_name_lower]
    
    # Recherche partielle
    for key, info in MEDICATIONS_DATABASE.items():
        if key in drug_name_lower or drug_name_lower in key:
            return info
    
    # Recherche dans le nom du médicament
    for key, info in MEDICATIONS_DATABASE.items():
        drug_name = info.get('name', '').lower()
        if drug_name and (drug_name in drug_name_lower or any(word in drug_name_lower for word in drug_name.split())):
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

def search_database(query_lower: str):
    """
    Recherche dans toutes les bases de données pharmaceutiques
    Retourne les informations pertinentes selon le domaine
    """
    results = []
    
    # Recherche dans les médicaments
    for drug_key, drug_info in MEDICATIONS_DATABASE.items():
        if drug_key in query_lower or any(word in query_lower for word in drug_info['name'].lower().split()):
            results.append(("medication", drug_key, drug_info))
    
    # Recherche dans les dispositifs médicaux
    if any(word in query_lower for word in ['dispositif', 'device', 'medtech', 'implant', 'prothese']):
        if 'classe' in query_lower:
            for class_key, class_info in MEDICAL_DEVICES_DATABASE['dispositif_medical']['classes'].items():
                if class_key.replace('_', ' ') in query_lower:
                    results.append(("medical_device", class_key, class_info))
        else:
            results.append(("medical_device", "dispositif_medical", MEDICAL_DEVICES_DATABASE['dispositif_medical']))
    
    # Recherche dans les essais cliniques
    if any(word in query_lower for word in ['essai', 'clinical trial', 'phase', 'etude clinique']):
        if 'phase' in query_lower:
            for phase_key, phase_info in CLINICAL_TRIALS_DATABASE['essai_clinique']['phases'].items():
                if phase_key.replace('_', ' ') in query_lower:
                    results.append(("clinical_trial", phase_key, phase_info))
        else:
            results.append(("clinical_trial", "essai_clinique", CLINICAL_TRIALS_DATABASE['essai_clinique']))
    
    # Recherche dans la réglementation
    if 'fda' in query_lower:
        results.append(("regulation", "fda", REGULATION_DATABASE['fda']))
    if 'ema' in query_lower:
        results.append(("regulation", "ema", REGULATION_DATABASE['ema']))
    if 'ansm' in query_lower:
        results.append(("regulation", "ansm", REGULATION_DATABASE['ansm']))
    if 'amm' in query_lower or 'autorisation' in query_lower:
        results.append(("regulation", "amm", REGULATION_DATABASE['amm']))
    
    # Recherche dans la pharmacovigilance
    if any(word in query_lower for word in ['pharmacovigilance', 'effet indesirable', 'side effect', 'signalement']):
        results.append(("pharmacovigilance", "pharmacovigilance", PHARMACOVIGILANCE_DATABASE['pharmacovigilance']))
    
    # Recherche dans la biotechnologie
    if any(word in query_lower for word in ['biotechnologie', 'biotech', 'biologique', 'biosimilaire', 'therapie genique']):
        if 'biosimilaire' in query_lower:
            results.append(("biotech", "biosimilaire", BIOTECH_DATABASE['biosimilaire']))
        elif 'therapie genique' in query_lower or 'gene therapy' in query_lower:
            results.append(("biotech", "therapie_genique", BIOTECH_DATABASE['therapie_genique']))
        elif 'biologique' in query_lower or 'biologic' in query_lower:
            results.append(("biotech", "medicament_biologique", BIOTECH_DATABASE['medicament_biologique']))
        else:
            results.append(("biotech", "biotechnologie", BIOTECH_DATABASE['biotechnologie']))
    
    return results

def generate_domain_response(query_lower: str, domain: str, data: dict):
    """Génère une réponse structurée selon le domaine"""
    if domain == "medication":
        return generate_drug_response(data, "general")
    elif domain == "medical_device":
        if isinstance(data, dict) and 'name' in data:
            # Classe de dispositif
            return f"**{data['name']}**\n\n{data['description']}\n\n**Conformité :** {data['conformite']}"
        else:
            # Dispositif médical général
            return f"**{data.get('definition', 'Dispositif médical')}**\n\n**Classes :**\n• Classe I : Risque faible\n• Classe IIa : Risque moyen-faible\n• Classe IIb : Risque moyen-élevé\n• Classe III : Risque élevé\n\n**Réglementation :** {data.get('reglementation', {}).get('europe', 'MDR')}"
    elif domain == "clinical_trial":
        if isinstance(data, dict) and 'name' in data:
            # Phase spécifique
            return f"**{data['name']}**\n\n**Objectif :** {data['objectif']}\n**Participants :** {data['participants']}\n**Durée :** {data['duree']}\n**Focus :** {data['focus']}"
        else:
            # Essai clinique général
            phases = "\n".join([f"• **{phase['name']}** : {phase['objectif']}" for phase in data['phases'].values()])
            return f"**Essai clinique**\n\n{data['definition']}\n\n**Phases :**\n{phases}"
    elif domain == "regulation":
        if 'nom_complet' in data:
            return f"**{data['nom_complet']} ({data.get('pays', '')})**\n\n**Rôle :** {data['role']}\n\n**Processus d'AMM :** {', '.join(data.get('processus_amm', {}).keys())}"
        else:
            return f"**{data.get('definition', 'Réglementation')}**\n\n**Dossier requis :** {', '.join(data.get('dossier', {}).keys())}"
    elif domain == "pharmacovigilance":
        return f"**Pharmacovigilance**\n\n{data['definition']}\n\n**Objectifs :**\n" + "\n".join([f"• {obj}" for obj in data['objectifs']])
    elif domain == "biotech":
        if 'definition' in data:
            return f"**{data.get('definition', 'Biotechnologie')}**\n\n**Applications :**\n" + "\n".join([f"• {app}" for app in data.get('applications', [])])
        else:
            return str(data)
    
    return None

# Export pour compatibilité
PHARMA_DATABASE = MEDICATIONS_DATABASE
