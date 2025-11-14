"""
Système de génération de réponses intelligentes pour questions pharmaceutiques
Génère des réponses contextuelles même pour des questions non présentes dans la base de données
"""
import re

def extract_drug_name(message_lower: str) -> str:
    """Extrait le nom d'un médicament potentiel de la question"""
    # Patterns communs pour les noms de médicaments
    # Chercher des mots avec majuscules ou des noms propres
    words = message_lower.split()
    
    # Chercher des patterns comme "médicament X", "X 40mg", "X est"
    for i, word in enumerate(words):
        if word in ['médicament', 'medicament', 'drug', 'principe', 'actif']:
            if i + 1 < len(words):
                return words[i + 1]
        if word.endswith('ine') or word.endswith('ol') or word.endswith('ide') or word.endswith('ate'):
            # Patterns de terminaison communs pour médicaments
            if len(word) > 4:
                return word
    
    return None

def generate_intelligent_pharma_response(message_lower: str, message: str) -> str:
    """
    Génère une réponse intelligente pour une question pharmaceutique
    même si elle n'est pas dans la base de données
    """
    
    # 1. Questions sur les mécanismes d'action
    if any(word in message_lower for word in ['comment fonctionne', 'how does', 'mécanisme', 'mechanism', 'fonctionne', 'works', 'action']):
        drug_name = extract_drug_name(message_lower)
        if drug_name:
            return f"Le mécanisme d'action d'un médicament dépend de sa classe thérapeutique. Pour **{drug_name}**, le mécanisme peut varier selon sa classification :\n\n• **Antibiotiques** : inhibent la croissance ou tuent les bactéries en ciblant des structures spécifiques (paroi cellulaire, ADN, protéines)\n• **Anti-inflammatoires** : réduisent l'inflammation en inhibant les médiateurs inflammatoires\n• **Analgésiques** : soulagent la douleur en agissant sur les récepteurs de la douleur\n• **Antihypertenseurs** : abaissent la tension artérielle\n• **Antiacides** : réduisent l'acidité gastrique\n\nPour connaître le mécanisme précis de **{drug_name}**, je recommande de consulter la notice du médicament ou un professionnel de santé."
        else:
            return "Les médicaments fonctionnent selon différents mécanismes d'action selon leur classe thérapeutique :\n\n• **Antibiotiques** : inhibent la croissance ou tuent les bactéries en ciblant des structures spécifiques (paroi cellulaire, ADN, protéines)\n• **Anti-inflammatoires** : réduisent l'inflammation en inhibant les médiateurs inflammatoires (COX, cytokines)\n• **Analgésiques** : soulagent la douleur en agissant sur les récepteurs de la douleur dans le système nerveux central\n• **Antihypertenseurs** : abaissent la tension artérielle en agissant sur le système cardiovasculaire (inhibiteurs ACE, bêta-bloquants, diurétiques)\n• **Antiacides/anti-ulcéreux** : réduisent l'acidité gastrique (IPP, antagonistes H2)\n• **Statines** : réduisent le cholestérol en inhibant l'enzyme HMG-CoA réductase\n\nChaque médicament a un mécanisme spécifique qui cible des processus biologiques particuliers. Pour des informations précises sur un médicament spécifique, pouvez-vous me donner son nom ?"
    
    # 2. Questions sur les effets secondaires
    if any(word in message_lower for word in ['effet secondaire', 'side effect', 'effet indésirable', 'adverse', 'effets', 'effets secondaires']):
        drug_name = extract_drug_name(message_lower)
        if drug_name:
            return f"Les effets secondaires de **{drug_name}** peuvent varier selon plusieurs facteurs :\n\n**Effets secondaires fréquents :**\n• Troubles digestifs : nausées, diarrhée, constipation\n• Réactions cutanées : éruptions, urticaire\n• Maux de tête, vertiges\n• Fatigue, somnolence\n\n**Effets secondaires graves (rares) :**\n• Réactions allergiques sévères (anaphylaxie)\n• Troubles hépatiques ou rénaux\n• Troubles cardiovasculaires\n• Troubles hématologiques\n\n**Facteurs influençant les effets secondaires :**\n• Dosage et durée du traitement\n• Interactions médicamenteuses\n• Conditions médicales préexistantes\n• Âge et fonction rénale/hépatique\n\n⚠️ Pour connaître les effets secondaires spécifiques de **{drug_name}**, consultez la notice du médicament ou un professionnel de santé. En cas d'effets indésirables, contactez immédiatement un médecin."
        else:
            return "Les effets secondaires des médicaments varient selon le principe actif et la classe thérapeutique.\n\n**Effets secondaires fréquents :**\n• Troubles digestifs : nausées, vomissements, diarrhée, constipation\n• Réactions cutanées : éruptions, urticaire, démangeaisons\n• Maux de tête, vertiges\n• Fatigue, somnolence\n\n**Effets secondaires graves (plus rares) :**\n• Réactions allergiques sévères (anaphylaxie)\n• Troubles hépatiques ou rénaux\n• Troubles cardiovasculaires (arythmies, hypertension)\n• Troubles hématologiques (anémie, thrombopénie)\n• Troubles neurologiques\n\n**Facteurs influençant les effets secondaires :**\n• Dosage et durée du traitement\n• Interactions médicamenteuses\n• Conditions médicales préexistantes\n• Âge, poids, fonction rénale/hépatique\n• Génétique (pharmacogénomique)\n\n⚠️ Pour des informations précises sur les effets secondaires d'un médicament spécifique, consultez la notice du médicament ou un professionnel de santé."
    
    # 3. Questions sur la posologie/dosage
    if any(word in message_lower for word in ['posologie', 'dosage', 'dose', 'prendre', 'utiliser', 'combien', 'how much', 'how many']):
        drug_name = extract_drug_name(message_lower)
        if drug_name:
            return f"La posologie de **{drug_name}** dépend de plusieurs facteurs :\n\n**Facteurs déterminant la posologie :**\n• Type d'infection ou condition traitée\n• Sévérité de la condition\n• Âge et poids du patient\n• Fonction rénale et hépatique\n• Interactions médicamenteuses\n• Antécédents médicaux\n\n**Exemples de posologies courantes :**\n• **Antibiotiques** : généralement 2-3 fois par jour pendant 5-10 jours\n• **Analgésiques** : selon la douleur, toutes les 4-8 heures\n• **Antihypertenseurs** : généralement une fois par jour\n• **Anti-inflammatoires** : 2-3 fois par jour avec les repas\n\n⚠️ **IMPORTANT** : La posologie exacte de **{drug_name}** doit être déterminée par un professionnel de santé. Ne modifiez jamais la posologie sans avis médical. Consultez la notice du médicament ou votre médecin/pharmacien."
        else:
            return "La posologie d'un médicament dépend de plusieurs facteurs importants :\n\n**Facteurs déterminant la posologie :**\n• Type d'infection ou condition traitée\n• Sévérité de la condition\n• Âge et poids du patient\n• Fonction rénale et hépatique\n• Interactions médicamenteuses\n• Antécédents médicaux et allergies\n• Grossesse ou allaitement\n\n**Exemples de posologies courantes :**\n• **Antibiotiques** : généralement 2-3 fois par jour pendant 5-10 jours selon l'infection\n• **Analgésiques** : selon l'intensité de la douleur, toutes les 4-8 heures\n• **Antihypertenseurs** : généralement une fois par jour, le matin\n• **Anti-inflammatoires** : 2-3 fois par jour, de préférence avec les repas\n• **Statines** : généralement une fois par jour, le soir\n\n⚠️ **IMPORTANT** : La posologie exacte doit toujours être déterminée par un professionnel de santé. Ne modifiez jamais la posologie sans avis médical. Consultez la notice du médicament ou votre médecin/pharmacien."
    
    # 4. Questions sur les indications
    if any(word in message_lower for word in ['indication', 'utilisé', 'used', 'traitement', 'treatment', 'pour', 'for', 'contre quoi']):
        drug_name = extract_drug_name(message_lower)
        if drug_name:
            return f"**{drug_name}** peut être utilisé pour traiter diverses conditions selon sa classe thérapeutique :\n\n**Indications courantes selon les classes :**\n• **Antibiotiques** : infections bactériennes (respiratoires, urinaires, cutanées, etc.)\n• **Anti-inflammatoires** : douleur, inflammation, fièvre, arthrite\n• **Analgésiques** : douleur légère à modérée, fièvre\n• **Antihypertenseurs** : hypertension artérielle\n• **Antiacides** : ulcères gastriques, reflux gastro-œsophagien\n• **Statines** : hypercholestérolémie, prévention cardiovasculaire\n• **Antidiabétiques** : diabète de type 2\n\n⚠️ Pour connaître les indications spécifiques de **{drug_name}**, consultez la notice du médicament ou un professionnel de santé. L'utilisation d'un médicament doit toujours être prescrite par un médecin."
        else:
            return "Les médicaments sont utilisés pour traiter diverses conditions médicales selon leur classe thérapeutique :\n\n**Indications courantes :**\n• **Antibiotiques** : infections bactériennes (respiratoires, urinaires, cutanées, dentaires, gynécologiques)\n• **Anti-inflammatoires** : douleur, inflammation, fièvre, arthrite, rhumatismes\n• **Analgésiques** : douleur légère à modérée, fièvre, maux de tête\n• **Antihypertenseurs** : hypertension artérielle, prévention cardiovasculaire\n• **Antiacides/anti-ulcéreux** : ulcères gastriques et duodénaux, reflux gastro-œsophagien\n• **Statines** : hypercholestérolémie, prévention des événements cardiovasculaires\n• **Antidiabétiques** : diabète de type 2, prévention du diabète\n• **Anticoagulants** : prévention des thromboses, fibrillation auriculaire\n\n⚠️ L'utilisation d'un médicament doit toujours être prescrite par un médecin après évaluation de votre condition médicale."
    
    # 5. Questions sur les interactions
    if any(word in message_lower for word in ['interaction', 'interagit', 'compatible', 'compatibilité', 'peut prendre avec']):
        return "Les interactions médicamenteuses sont des modifications de l'effet d'un médicament lorsqu'il est pris avec un autre médicament, aliment, ou complément.\n\n**Types d'interactions :**\n• **Pharmacocinétiques** : modification de l'absorption, distribution, métabolisme, ou élimination\n• **Pharmacodynamiques** : modification de l'effet au niveau des récepteurs\n• **Interactions avec les aliments** : certains médicaments doivent être pris à jeun ou avec les repas\n• **Interactions avec l'alcool** : peuvent augmenter les effets secondaires\n\n**Exemples courants :**\n• Anticoagulants + AINS = risque de saignement accru\n• Statines + certains antibiotiques = risque de myopathie\n• IPP + certains médicaments = réduction de l'absorption\n\n⚠️ **IMPORTANT** : Avant de prendre plusieurs médicaments ensemble, consultez toujours un pharmacien ou un médecin. Informez votre professionnel de santé de tous les médicaments, compléments, et herbes que vous prenez."
    
    # 6. Questions sur les contre-indications
    if any(word in message_lower for word in ['contre-indication', 'contraindication', 'ne pas', 'interdit', 'peut pas prendre']):
        return "Les contre-indications sont des situations où un médicament ne doit pas être utilisé en raison d'un risque accru d'effets indésirables.\n\n**Contre-indications courantes :**\n• **Allergies** : allergie connue au médicament ou à ses composants\n• **Grossesse et allaitement** : certains médicaments sont contre-indiqués (catégories de risque)\n• **Insuffisance rénale ou hépatique sévère** : peut nécessiter une adaptation de la posologie ou contre-indication\n• **Interactions médicamenteuses** : certains médicaments ne doivent pas être pris ensemble\n• **Conditions médicales préexistantes** : certaines maladies peuvent être des contre-indications\n• **Âge** : certains médicaments sont contre-indiqués chez les enfants ou personnes âgées\n\n**Exemples :**\n• Pénicillines : contre-indiquées en cas d'allergie aux bêta-lactamines\n• AINS : contre-indiqués en cas d'insuffisance rénale sévère, ulcère gastrique actif\n• Statines : contre-indiquées en cas de maladie hépatique active\n\n⚠️ Pour connaître les contre-indications d'un médicament spécifique, consultez la notice du médicament ou un professionnel de santé."
    
    # 7. Questions générales "c'est quoi", "qu'est-ce que"
    if any(word in message_lower for word in ['c\'est quoi', 'qu\'est', 'what is', 'what', 'définition', 'definition']):
        # Essayer d'identifier le sujet
        if any(word in message_lower for word in ['médicament', 'medicament', 'drug']):
            return "Un **médicament** est une substance ou composition présentée comme possédant des propriétés curatives ou préventives à l'égard des maladies humaines ou animales.\n\n**Composants d'un médicament :**\n• **Principe actif** : substance responsable de l'effet thérapeutique\n• **Excipients** : substances inactives qui facilitent l'administration (liants, colorants, conservateurs)\n\n**Formes pharmaceutiques :**\n• Comprimés, gélules, sirops, injections, pommades, suppositoires, etc.\n\n**Classification :**\n• Médicaments sur ordonnance (prescription obligatoire)\n• Médicaments en vente libre (sans ordonnance)\n• Médicaments génériques vs médicaments princeps\n\n**Réglementation :**\n• Autorisation de mise sur le marché (AMM) par les agences réglementaires (ANSM, EMA, FDA)\n• Surveillance post-commercialisation (pharmacovigilance)\n\nLes médicaments sont développés et testés selon des processus stricts pour garantir leur sécurité et efficacité."
        
        # Si c'est une question générale sur le domaine pharmaceutique
        return "Le domaine **pharmaceutique et de la santé (Pharma/MedTech)** englobe :\n\n**1. Médicaments et principes actifs**\n• Développement, production, et commercialisation de médicaments\n• Recherche de nouveaux principes actifs\n• Formes pharmaceutiques et galénique\n\n**2. Dispositifs médicaux (MedTech)**\n• Instruments, appareils, équipements médicaux\n• Implants et prothèses\n• Classification et réglementation (Classe I, IIa, IIb, III)\n\n**3. Essais cliniques et recherche**\n• Phases I, II, III, IV des essais cliniques\n• Méthodologie et réglementation (ICH-GCP)\n• Développement de nouveaux traitements\n\n**4. Réglementation**\n• Agences réglementaires : FDA (USA), EMA (UE), ANSM (France)\n• Autorisation de mise sur le marché (AMM)\n• Surveillance post-commercialisation\n\n**5. Pharmacovigilance**\n• Surveillance des effets indésirables\n• Signalement et gestion des risques\n• Rapport bénéfice/risque\n\n**6. Biotechnologie pharmaceutique**\n• Médicaments biologiques et biosimilaires\n• Thérapies géniques et cellulaires\n• Technologies innovantes\n\nSouhaitez-vous des informations plus spécifiques sur l'un de ces domaines ?"
    
    # 8. Questions sur la sécurité
    if any(word in message_lower for word in ['sécurité', 'safety', 'sûr', 'safe', 'danger', 'risque', 'risk']):
        return "La **sécurité des médicaments** est évaluée à plusieurs niveaux :\n\n**1. Développement préclinique**\n• Tests de toxicité sur animaux\n• Études de pharmacocinétique et pharmacodynamie\n\n**2. Essais cliniques (Phases I-III)**\n• Évaluation de la sécurité chez l'humain\n• Identification des effets secondaires fréquents\n• Détermination de la dose maximale tolérée\n\n**3. Pharmacovigilance post-commercialisation**\n• Surveillance continue après autorisation\n• Détection des effets secondaires rares\n• Signalement des effets indésirables\n• Évaluation du rapport bénéfice/risque\n\n**4. Mesures de sécurité**\n• Notices d'information patient\n• Contre-indications et précautions d'emploi\n• Interactions médicamenteuses\n• Adaptations de posologie selon les populations\n\n**5. Gestion des risques**\n• Plans de gestion des risques (RMP)\n• Restrictions d'utilisation si nécessaire\n• Retrait du marché en cas de risque majeur\n\n⚠️ Pour des informations sur la sécurité d'un médicament spécifique, consultez la notice ou un professionnel de santé."
    
    # 9. Questions sur la recherche et développement
    if any(word in message_lower for word in ['recherche', 'research', 'développement', 'development', 'r&d', 'innovation', 'nouveau médicament']):
        return "Le **développement d'un nouveau médicament** suit un processus long et rigoureux :\n\n**1. Découverte (2-5 ans)**\n• Identification de cibles thérapeutiques\n• Découverte de molécules candidates\n• Tests in vitro et in silico\n\n**2. Développement préclinique (1-2 ans)**\n• Tests de toxicité sur animaux\n• Études de pharmacocinétique\n• Formulation galénique\n\n**3. Essais cliniques (5-10 ans)**\n• **Phase I** : sécurité et tolérance (20-100 volontaires)\n• **Phase II** : efficacité préliminaire (100-300 patients)\n• **Phase III** : confirmation efficacité/sécurité (1000-3000 patients)\n• **Phase IV** : surveillance post-commercialisation\n\n**4. Autorisation réglementaire (1-2 ans)**\n• Dossier d'AMM soumis aux agences (FDA, EMA, ANSM)\n• Évaluation par les experts\n• Décision d'autorisation\n\n**5. Commercialisation et surveillance**\n• Mise sur le marché\n• Pharmacovigilance continue\n• Optimisation des indications\n\n**Coût total** : généralement 1-2 milliards d'euros et 10-15 ans de développement.\n\n**Taux de succès** : seulement 1 molécule sur 10 000 testées arrive sur le marché."
    
    # 10. Réponse générique intelligente pour questions pharmaceutiques
    # Analyser les mots-clés pour donner une réponse contextuelle
    keywords_found = []
    if any(word in message_lower for word in ['médicament', 'medicament', 'drug']):
        keywords_found.append('médicament')
    if any(word in message_lower for word in ['dispositif', 'device', 'medtech']):
        keywords_found.append('dispositif médical')
    if any(word in message_lower for word in ['essai', 'clinical trial', 'phase']):
        keywords_found.append('essai clinique')
    if any(word in message_lower for word in ['réglementation', 'regulation', 'fda', 'ema', 'ansm']):
        keywords_found.append('réglementation')
    if any(word in message_lower for word in ['pharmacovigilance', 'effet indésirable']):
        keywords_found.append('pharmacovigilance')
    if any(word in message_lower for word in ['biotechnologie', 'biotech', 'biologique']):
        keywords_found.append('biotechnologie')
    
    if keywords_found:
        return f"Je comprends que votre question concerne le domaine pharmaceutique et de la santé, spécifiquement : **{', '.join(keywords_found)}**.\n\nBien que je n'aie pas d'informations détaillées spécifiques sur votre question exacte, voici des ressources utiles :\n\n**Pour obtenir des informations précises :**\n• Consultez les notices officielles des médicaments ou dispositifs médicaux\n• Contactez un pharmacien ou un professionnel de santé\n• Consultez les bases de données officielles :\n  - ANSM (France) : www.ansm.sante.fr\n  - EMA (Europe) : www.ema.europa.eu\n  - FDA (USA) : www.fda.gov\n• Consultez les publications scientifiques spécialisées\n\n**Je peux vous aider avec :**\n• Questions générales sur les médicaments (mécanismes, effets, posologie)\n• Informations sur les essais cliniques et leurs phases\n• Explications sur la réglementation pharmaceutique\n• Questions sur la pharmacovigilance et la sécurité\n• Informations sur la biotechnologie pharmaceutique\n\nPouvez-vous reformuler votre question de manière plus spécifique ?"
    
    # Réponse finale générique
    return "Je comprends que vous posez une question sur le domaine pharmaceutique et de la santé (Pharma/MedTech).\n\n**Je peux vous aider avec des questions sur :**\n• 💊 Médicaments et principes actifs (mécanismes, effets, posologie, indications)\n• 🏥 Dispositifs médicaux (MedTech) et leur classification\n• 🔬 Essais cliniques et recherche pharmaceutique\n• 📋 Réglementation (FDA, EMA, ANSM, AMM)\n• ⚠️ Pharmacovigilance et sécurité des médicaments\n• 🧬 Biotechnologie pharmaceutique (médicaments biologiques, biosimilaires, thérapies géniques)\n\n**Pour des informations très spécifiques :**\n• Consultez les notices officielles\n• Contactez un pharmacien ou un professionnel de santé\n• Consultez les bases de données officielles (ANSM, EMA, FDA)\n\nPouvez-vous reformuler votre question de manière plus précise sur l'un de ces domaines ?"

