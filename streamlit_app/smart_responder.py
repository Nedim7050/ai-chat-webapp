"""
Système intelligent de génération de réponses pour questions pharmaceutiques
Comprend le contexte, gère les interactions, et génère des réponses adaptées
"""
import re
from typing import List, Dict, Optional

class SmartPharmaResponder:
    """Répondeur intelligent pour questions pharmaceutiques"""
    
    def __init__(self):
        self.conversation_context = []
        self.question_patterns = self._init_question_patterns()
        self.response_templates = self._init_response_templates()
    
    def _init_question_patterns(self):
        """Initialise les patterns de questions"""
        return {
            'mechanism': [
                r'comment\s+(fonctionne|marche|agit)',
                r'how\s+(does|do)\s+(it|.*)\s+(work|function)',
                r'mécanisme\s+d\'?action',
                r'mechanism\s+of\s+action',
                r'comment\s+ça\s+marche',
                r'pourquoi\s+(.*)\s+fonctionne'
            ],
            'side_effects': [
                r'effet\s+(secondaire|indésirable)',
                r'side\s+effect',
                r'effet\s+adverse',
                r'quels?\s+effets?',
                r'risque',
                r'danger',
                r'contre-indication'
            ],
            'dosage': [
                r'posologie',
                r'dosage',
                r'dose',
                r'combien\s+(prendre|utiliser|mg|ml)',
                r'how\s+much',
                r'how\s+many',
                r'fréquence',
                r'pendant\s+combien'
            ],
            'indications': [
                r'pour\s+quoi',
                r'pour\s+quelle',
                r'indication',
                r'utilisé?\s+pour',
                r'used\s+for',
                r'traitement\s+de',
                r'treatment\s+of',
                r'contre\s+quoi'
            ],
            'interactions': [
                r'interaction',
                r'peut\s+(prendre|utiliser)\s+avec',
                r'compatible',
                r'compatibilité',
                r'associer',
                r'prendre\s+en\s+même\s+temps',
                r'take\s+with'
            ],
            'general': [
                r'c\'?est\s+quoi',
                r'qu\'?est\s+(ce\s+que|ce\s+qu\')',
                r'what\s+is',
                r'définition',
                r'definition',
                r'explique',
                r'explain',
                r'parle\s+moi\s+de',
                r'tell\s+me\s+about'
            ],
            'comparison': [
                r'différence\s+entre',
                r'difference\s+between',
                r'comparer',
                r'compare',
                r'vs',
                r'versus',
                r'meilleur',
                r'better',
                r'plus\s+efficace'
            ],
            'safety': [
                r'sécurité',
                r'safety',
                r'sûr',
                r'safe',
                r'risque',
                r'risk',
                r'dangereux',
                r'dangerous'
            ]
        }
    
    def _init_response_templates(self):
        """Initialise les templates de réponses"""
        return {
            'mechanism': {
                'antibiotic': "Les **antibiotiques** comme {drug} fonctionnent en ciblant des structures spécifiques des bactéries :\n\n• **Inhibition de la synthèse de la paroi cellulaire** : Empêche la formation de la paroi, entraînant la lyse bactérienne (pénicillines, céphalosporines)\n• **Inhibition de la synthèse protéique** : Bloque la production de protéines essentielles (macrolides, tétracyclines)\n• **Inhibition de la réplication de l'ADN** : Empêche la division bactérienne (quinolones)\n• **Inhibition du métabolisme** : Bloque des voies métaboliques essentielles (sulfamides)\n\n**{drug}** appartient à la classe des {class}, ce qui signifie qu'il {specific_mechanism}.\n\n⚠️ Le mécanisme exact peut varier selon la souche bactérienne et la résistance. Consultez un professionnel de santé pour des informations spécifiques.",
                'anti_inflammatory': "Les **anti-inflammatoires** comme {drug} fonctionnent en réduisant l'inflammation :\n\n• **Inhibition des enzymes COX** : Bloque la cyclooxygénase (COX-1 et/ou COX-2), réduisant la production de prostaglandines inflammatoires\n• **Réduction de la douleur** : Les prostaglandines sont impliquées dans la transmission de la douleur\n• **Réduction de la fièvre** : Action sur le centre de régulation de la température\n• **Réduction de l'inflammation** : Diminue le gonflement, la rougeur, et la chaleur\n\n**{drug}** {specific_mechanism}.\n\n⚠️ Les AINS peuvent avoir des effets secondaires digestifs. Consultez un professionnel de santé.",
                'analgesic': "Les **analgésiques** comme {drug} fonctionnent pour soulager la douleur :\n\n• **Action centrale** : Agissent sur le système nerveux central pour réduire la perception de la douleur\n• **Inhibition des prostaglandines** : Réduit les médiateurs de la douleur\n• **Modulation des récepteurs** : Interagit avec les récepteurs de la douleur\n\n**{drug}** {specific_mechanism}.\n\n⚠️ Respectez la posologie recommandée pour éviter les effets secondaires.",
                'default': "**{drug}** fonctionne selon un mécanisme d'action spécifique à sa classe thérapeutique :\n\n• **{class}** : {specific_mechanism}\n\nLe mécanisme d'action dépend de plusieurs facteurs :\n• La cible moléculaire du médicament\n• La voie d'administration\n• La pharmacocinétique (absorption, distribution, métabolisme, élimination)\n• Les interactions avec d'autres substances\n\n⚠️ Pour connaître le mécanisme précis de **{drug}**, consultez la notice du médicament ou un professionnel de santé."
            },
            'side_effects': {
                'default': "Les **effets secondaires de {drug}** peuvent varier selon plusieurs facteurs :\n\n**Effets secondaires fréquents :**\n• Troubles digestifs : nausées, vomissements, diarrhée, constipation, douleurs abdominales\n• Réactions cutanées : éruptions, urticaire, démangeaisons\n• Maux de tête, vertiges\n• Fatigue, somnolence\n\n**Effets secondaires graves (rares) :**\n• Réactions allergiques sévères (anaphylaxie)\n• Troubles hépatiques ou rénaux\n• Troubles cardiovasculaires\n• Troubles hématologiques\n\n**Facteurs influençant les effets secondaires :**\n• Dosage et durée du traitement\n• Interactions médicamenteuses\n• Conditions médicales préexistantes\n• Âge, poids, fonction rénale/hépatique\n• Génétique (pharmacogénomique)\n\n⚠️ **IMPORTANT** : En cas d'effets indésirables, arrêtez le traitement et consultez immédiatement un professionnel de santé. Pour des informations spécifiques sur **{drug}**, consultez la notice du médicament."
            },
            'dosage': {
                'default': "La **posologie de {drug}** dépend de plusieurs facteurs importants :\n\n**Facteurs déterminant la posologie :**\n• Type et sévérité de la condition traitée\n• Âge et poids du patient\n• Fonction rénale et hépatique\n• Interactions médicamenteuses\n• Antécédents médicaux\n• Grossesse ou allaitement\n\n**Exemples de posologies courantes :**\n• **Antibiotiques** : généralement 2-3 fois par jour pendant 5-10 jours\n• **Analgésiques** : selon l'intensité, toutes les 4-8 heures\n• **Antihypertenseurs** : généralement une fois par jour\n• **Anti-inflammatoires** : 2-3 fois par jour avec les repas\n\n⚠️ **IMPORTANT** : La posologie exacte de **{drug}** doit être déterminée par un professionnel de santé. Ne modifiez jamais la posologie sans avis médical. Respectez toujours la prescription."
            },
            'interactions': {
                'default': "Les **interactions médicamenteuses** sont des modifications de l'effet d'un médicament lorsqu'il est pris avec un autre médicament, aliment, ou complément.\n\n**Types d'interactions :**\n• **Pharmacocinétiques** : modification de l'absorption, distribution, métabolisme, ou élimination\n• **Pharmacodynamiques** : modification de l'effet au niveau des récepteurs\n• **Interactions avec les aliments** : certains médicaments doivent être pris à jeun ou avec les repas\n• **Interactions avec l'alcool** : peuvent augmenter les effets secondaires\n\n**Exemples d'interactions courantes :**\n• Anticoagulants + AINS = risque de saignement accru\n• Statines + certains antibiotiques = risque de myopathie\n• IPP + certains médicaments = réduction de l'absorption\n• Antidépresseurs + alcool = effets sédatifs accrus\n\n⚠️ **IMPORTANT** : Avant de prendre plusieurs médicaments ensemble, consultez toujours un pharmacien ou un médecin. Informez votre professionnel de santé de tous les médicaments, compléments, et herbes que vous prenez."
            }
        }
    
    def extract_drug_name(self, message: str) -> Optional[str]:
        """Extrait le nom d'un médicament de la question"""
        message_lower = message.lower()
        
        # Patterns pour détecter les noms de médicaments
        # Chercher après "médicament", "drug", etc.
        patterns = [
            r'médicament\s+([a-zA-Z]+)',
            r'drug\s+([a-zA-Z]+)',
            r'([a-zA-Z]+)\s+(40|20|50|100|200|500|1000)\s*mg',
            r'([a-zA-Z]+)\s+(fonctionne|marche|agit|effet|posologie)',
            r'effets?\s+(secondaires?|indésirables?)\s+de\s+([a-zA-Z]+)',
            r'posologie\s+de\s+([a-zA-Z]+)',
            r'comment\s+fonctionne\s+([a-zA-Z]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                drug = match.group(1) if match.lastindex >= 1 else match.group(0)
                if len(drug) > 3:  # Filtrer les mots trop courts
                    return drug.capitalize()
        
        # Chercher des mots avec terminaisons typiques de médicaments
        words = message.split()
        for word in words:
            word_lower = word.lower()
            if (word_lower.endswith('ine') or word_lower.endswith('ol') or 
                word_lower.endswith('ide') or word_lower.endswith('ate') or
                word_lower.endswith('azole') or word_lower.endswith('mycin')):
                if len(word_lower) > 4 and word_lower not in ['dose', 'prise', 'fois']:
                    return word.capitalize()
        
        return None
    
    def detect_question_type(self, message: str) -> str:
        """Détecte le type de question"""
        message_lower = message.lower()
        
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return q_type
        
        return 'general'
    
    def generate_contextual_response(self, message: str, history: List[Dict], question_type: str, drug_name: Optional[str] = None) -> str:
        """Génère une réponse contextuelle intelligente"""
        
        # Analyser le contexte de la conversation
        context = self._analyze_conversation_context(history)
        
        # Générer la réponse selon le type de question
        if question_type == 'mechanism':
            return self._generate_mechanism_response(message, drug_name, context)
        elif question_type == 'side_effects':
            return self._generate_side_effects_response(message, drug_name, context)
        elif question_type == 'dosage':
            return self._generate_dosage_response(message, drug_name, context)
        elif question_type == 'indications':
            return self._generate_indications_response(message, drug_name, context)
        elif question_type == 'interactions':
            return self._generate_interactions_response(message, drug_name, context)
        elif question_type == 'comparison':
            return self._generate_comparison_response(message, context)
        elif question_type == 'safety':
            return self._generate_safety_response(message, drug_name, context)
        else:
            return self._generate_general_response(message, drug_name, context)
    
    def _analyze_conversation_context(self, history: List[Dict]) -> Dict:
        """Analyse le contexte de la conversation"""
        context = {
            'mentioned_drugs': [],
            'topics_discussed': [],
            'last_question_type': None
        }
        
        if history:
            for msg in history[-5:]:  # Analyser les 5 derniers messages
                content = msg.get('content', '').lower()
                role = msg.get('role', '')
                
                # Extraire les médicaments mentionnés
                drug = self.extract_drug_name(content)
                if drug and drug not in context['mentioned_drugs']:
                    context['mentioned_drugs'].append(drug)
                
                # Détecter les sujets discutés
                if 'effet' in content:
                    context['topics_discussed'].append('effets_secondaires')
                if 'posologie' in content or 'dosage' in content:
                    context['topics_discussed'].append('posologie')
                if 'interaction' in content:
                    context['topics_discussed'].append('interactions')
        
        return context
    
    def _generate_mechanism_response(self, message: str, drug_name: Optional[str], context: Dict) -> str:
        """Génère une réponse sur le mécanisme d'action"""
        if drug_name:
            # Détecter la classe du médicament
            drug_lower = drug_name.lower()
            if any(term in drug_lower for term in ['cilline', 'mycin', 'cycline', 'floxacine']):
                class_type = 'antibiotic'
                specific = "inhibe la croissance ou tue les bactéries en ciblant des structures spécifiques"
            elif any(term in drug_lower for term in ['profène', 'coxib', 'diclofenac']):
                class_type = 'anti_inflammatory'
                specific = "inhibe les enzymes COX, réduisant la production de prostaglandines inflammatoires"
            elif any(term in drug_lower for term in ['paracétamol', 'acetaminophen']):
                class_type = 'analgesic'
                specific = "inhibe la cyclooxygénase dans le système nerveux central"
            else:
                class_type = 'default'
                specific = "agit selon un mécanisme spécifique à sa classe"
            
            template = self.response_templates['mechanism'].get(class_type, self.response_templates['mechanism']['default'])
            return template.format(drug=drug_name, class=class_type, specific_mechanism=specific)
        else:
            return self._generate_comprehensive_mechanism_explanation()
    
    def _generate_side_effects_response(self, message: str, drug_name: Optional[str], context: Dict) -> str:
        """Génère une réponse sur les effets secondaires"""
        template = self.response_templates['side_effects']['default']
        if drug_name:
            return template.format(drug=drug_name)
        else:
            return template.format(drug="un médicament")
    
    def _generate_dosage_response(self, message: str, drug_name: Optional[str], context: Dict) -> str:
        """Génère une réponse sur la posologie"""
        template = self.response_templates['dosage']['default']
        if drug_name:
            return template.format(drug=drug_name)
        else:
            return template.format(drug="un médicament")
    
    def _generate_indications_response(self, message: str, drug_name: Optional[str], context: Dict) -> str:
        """Génère une réponse sur les indications"""
        if drug_name:
            return f"**{drug_name}** est utilisé pour traiter diverses conditions selon sa classe thérapeutique :\n\n**Indications courantes selon les classes :**\n• **Antibiotiques** : infections bactériennes (respiratoires, urinaires, cutanées, dentaires, gynécologiques)\n• **Anti-inflammatoires** : douleur, inflammation, fièvre, arthrite, rhumatismes\n• **Analgésiques** : douleur légère à modérée, fièvre, maux de tête\n• **Antihypertenseurs** : hypertension artérielle, prévention cardiovasculaire\n• **Antiacides** : ulcères gastriques, reflux gastro-œsophagien\n• **Statines** : hypercholestérolémie, prévention des événements cardiovasculaires\n• **Antidiabétiques** : diabète de type 2\n\n⚠️ Pour connaître les indications spécifiques de **{drug_name}**, consultez la notice du médicament ou un professionnel de santé. L'utilisation doit toujours être prescrite par un médecin."
        else:
            return "Les médicaments sont utilisés pour traiter diverses conditions médicales. Les indications dépendent de la classe thérapeutique du médicament. Pouvez-vous me donner le nom du médicament pour des informations plus précises ?"
    
    def _generate_interactions_response(self, message: str, drug_name: Optional[str], context: Dict) -> str:
        """Génère une réponse sur les interactions"""
        template = self.response_templates['interactions']['default']
        
        # Extraire les médicaments mentionnés dans la question
        mentioned_drugs = context.get('mentioned_drugs', [])
        if drug_name and drug_name not in mentioned_drugs:
            mentioned_drugs.append(drug_name)
        
        response = template
        if len(mentioned_drugs) >= 2:
            response += f"\n\n**Concernant {', '.join(mentioned_drugs)}** : Avant de prendre ces médicaments ensemble, consultez absolument un pharmacien ou un médecin pour vérifier les interactions spécifiques."
        
        return response
    
    def _generate_comparison_response(self, message: str, context: Dict) -> str:
        """Génère une réponse de comparaison"""
        mentioned_drugs = context.get('mentioned_drugs', [])
        
        if len(mentioned_drugs) >= 2:
            return f"**Comparaison entre {', '.join(mentioned_drugs)}** :\n\nLes différences entre médicaments dépendent de plusieurs facteurs :\n• **Classe thérapeutique** : Mécanismes d'action différents\n• **Efficacité** : Peut varier selon la condition traitée\n• **Effets secondaires** : Profils différents\n• **Posologie** : Dosages et fréquences différents\n• **Interactions** : Interactions médicamenteuses différentes\n• **Contre-indications** : Peuvent varier\n\n⚠️ Pour une comparaison détaillée, consultez un professionnel de santé qui pourra évaluer votre situation spécifique."
        else:
            return "Pour comparer des médicaments, j'aurais besoin de connaître les noms des médicaments à comparer. Pouvez-vous me les donner ?"
    
    def _generate_safety_response(self, message: str, drug_name: Optional[str], context: Dict) -> str:
        """Génère une réponse sur la sécurité"""
        if drug_name:
            return f"**Sécurité de {drug_name}** :\n\nLa sécurité d'un médicament est évaluée à plusieurs niveaux :\n\n**1. Développement** : Tests précliniques et cliniques rigoureux\n**2. Autorisation** : Évaluation par les agences réglementaires (ANSM, EMA, FDA)\n**3. Surveillance** : Pharmacovigilance post-commercialisation\n\n**Facteurs de sécurité :**\n• Respect de la posologie prescrite\n• Prise en compte des contre-indications\n• Gestion des interactions médicamenteuses\n• Surveillance des effets secondaires\n\n⚠️ Pour des informations spécifiques sur la sécurité de **{drug_name}**, consultez la notice du médicament ou un professionnel de santé."
        else:
            return "La sécurité des médicaments est une priorité absolue. Tous les médicaments autorisés ont été évalués pour leur sécurité et efficacité. Pour des informations spécifiques, pouvez-vous me donner le nom du médicament ?"
    
    def _generate_general_response(self, message: str, drug_name: Optional[str], context: Dict) -> str:
        """Génère une réponse générale intelligente"""
        message_lower = message.lower()
        
        # Si un médicament est mentionné
        if drug_name:
            return f"**{drug_name}** est un médicament utilisé dans le domaine pharmaceutique.\n\n**Je peux vous fournir des informations sur :**\n• Mécanisme d'action (comment il fonctionne)\n• Effets secondaires\n• Posologie et dosage\n• Indications thérapeutiques\n• Interactions médicamenteuses\n• Contre-indications\n• Sécurité\n\n**Quelle information souhaitez-vous sur {drug_name} ?**\n\nVous pouvez poser des questions comme :\n• \"Comment fonctionne {drug_name} ?\"\n• \"Quels sont les effets secondaires de {drug_name} ?\"\n• \"Quelle est la posologie de {drug_name} ?\""
        
        # Analyser les mots-clés pour donner une réponse contextuelle
        if any(word in message_lower for word in ['médicament', 'medicament', 'drug']):
            return "Les **médicaments** sont des substances utilisées pour traiter, prévenir, ou diagnostiquer des maladies.\n\n**Composants :**\n• Principe actif : substance responsable de l'effet thérapeutique\n• Excipients : substances facilitant l'administration\n\n**Classification :**\n• Par classe thérapeutique (antibiotiques, anti-inflammatoires, etc.)\n• Par voie d'administration (orale, injectable, topique)\n• Par statut réglementaire (sur ordonnance, en vente libre)\n\n**Développement :**\n• Recherche et développement (10-15 ans)\n• Essais cliniques (phases I, II, III, IV)\n• Autorisation réglementaire (AMM)\n• Surveillance post-commercialisation\n\nSouhaitez-vous des informations sur un médicament spécifique ou un aspect particulier ?"
        
        # Réponse générique intelligente
        return "Je suis un assistant spécialisé dans le domaine **pharmaceutique et de la santé (Pharma/MedTech)**.\n\n**Je peux vous aider avec :**\n• 💊 **Médicaments** : mécanismes, effets, posologie, indications, interactions\n• 🏥 **Dispositifs médicaux** : classification, réglementation\n• 🔬 **Essais cliniques** : phases, méthodologie\n• 📋 **Réglementation** : FDA, EMA, ANSM, AMM\n• ⚠️ **Pharmacovigilance** : sécurité, effets indésirables\n• 🧬 **Biotechnologie** : médicaments biologiques, biosimilaires, thérapies géniques\n\n**Comment puis-je vous aider aujourd'hui ?**\n\nPosez-moi une question spécifique, par exemple :\n• \"Comment fonctionne l'amoxicilline ?\"\n• \"Quels sont les effets secondaires de l'ibuprofène ?\"\n• \"Qu'est-ce qu'un essai clinique de phase III ?\""
    
    def _generate_comprehensive_mechanism_explanation(self) -> str:
        """Génère une explication complète des mécanismes d'action"""
        return """**Mécanismes d'action des médicaments** :

Les médicaments fonctionnent selon différents mécanismes selon leur classe :

**1. Antibiotiques :**
• Inhibition de la synthèse de la paroi cellulaire (pénicillines, céphalosporines)
• Inhibition de la synthèse protéique (macrolides, tétracyclines)
• Inhibition de la réplication de l'ADN (quinolones)
• Inhibition du métabolisme (sulfamides)

**2. Anti-inflammatoires :**
• Inhibition des enzymes COX (COX-1, COX-2)
• Réduction de la production de prostaglandines
• Action sur les médiateurs inflammatoires

**3. Analgésiques :**
• Action sur le système nerveux central
• Inhibition des récepteurs de la douleur
• Réduction de la perception de la douleur

**4. Antihypertenseurs :**
• Inhibition de l'enzyme de conversion de l'angiotensine (IEC)
• Blocage des récepteurs bêta-adrénergiques
• Action diurétique

**5. Statines :**
• Inhibition de l'HMG-CoA réductase
• Réduction de la synthèse du cholestérol

Chaque médicament a un mécanisme spécifique. Pour des informations précises, donnez-moi le nom du médicament."""

def generate_smart_response(message: str, history: List[Dict] = None) -> str:
    """Fonction principale pour générer une réponse intelligente"""
    if history is None:
        history = []
    
    responder = SmartPharmaResponder()
    
    # Extraire le nom du médicament
    drug_name = responder.extract_drug_name(message)
    
    # Détecter le type de question
    question_type = responder.detect_question_type(message)
    
    # Générer la réponse contextuelle
    response = responder.generate_contextual_response(message, history, question_type, drug_name)
    
    return response

