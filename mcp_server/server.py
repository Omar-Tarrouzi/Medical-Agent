from mcp.server.fastmcp import FastMCP
from typing import Optional
import json

# Initialisation du serveur MCP
mcp = FastMCP("medical-tools-server")

# -- Données de référence (temporaire le temps que je trouve une BD de médicament) -----------------
DRUG_DATABASE = {
    "paracetamol": {
        "indication": "Douleur, fièvre",
        "posologie": "500mg-1g toutes les 4-6h, max 4g/jour",
        "contre_indications": ["insuffisance hépatique sévère"],
        "interactions": ["alcool", "anticoagulants"]
    },
    "ibuprofene": {
        "indication": "Douleur, inflammation, fièvre",
        "posologie": "200-400mg toutes les 6-8h avec un repas",
        "contre_indications": ["ulcère gastrique", "grossesse > 24SA", "insuffisance rénale"],
        "interactions": ["anticoagulants", "aspirine", "lithium"]
    },
    "amoxicilline": {
        "indication": "Infections bactériennes",
        "posologie": "500mg-1g 3 fois/jour pendant 7-10 jours",
        "contre_indications": ["allergie aux pénicillines"],
        "interactions": ["methotrexate", "anticoagulants"]
    }
}

@mcp.tool()
def get_drug_info(drug_name: str) -> str:
    """
    Récupère les informations sur un médicament.

    Args:
        drug_name: Nom du médicament (en minuscules)

    Returns:
        Informations structurées sur le médicament
    """
    drug_lower = drug_name.lower().strip()
    drug_data = DRUG_DATABASE.get(drug_lower)

    if not drug_data:
        return f"Médicament '{drug_name}' non trouvé dans la base de données."

    return json.dumps({
        "medicament": drug_name,
        "indication": drug_data["indication"],
        "posologie": drug_data["posologie"],
        "contre_indications": drug_data["contre_indications"],
        "interactions": drug_data["interactions"],
        "avertissement": "Ces informations sont indicatives. Consultez un pharmacien."
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def check_drug_interaction(drug1: str, drug2: str) -> str:
    """
    Vérifie les interactions entre deux médicaments.

    Args:
        drug1: Premier médicament
        drug2: Deuxième médicament

    Returns:
        Rapport d’interaction
    """
    d1 = DRUG_DATABASE.get(drug1.lower(), {})
    d2 = DRUG_DATABASE.get(drug2.lower(), {})

    interactions_1 = [i.lower() for i in d1.get("interactions", [])]
    interactions_2 = [i.lower() for i in d2.get("interactions", [])]

    interaction_found = (
        drug2.lower() in interactions_1 or
        drug1.lower() in interactions_2
    )

    result = {
        "drug1": drug1,
        "drug2": drug2,
        "interaction_detectee": interaction_found,
        "niveau": "ATTENTION" if interaction_found else "Aucune interaction détectée",
        "recommandation": (
            "Consultez un médecin ou pharmacien avant association."
            if interaction_found else
            "Association a priori sans risque connu dans notre base."
        ),
        "avertissement": "Cette vérification est indicative et non exhaustive."
    }

    return json.dumps(result, ensure_ascii=False, indent=2)
mcp

@mcp.tool()
def get_red_flags(symptoms: str) -> str:
    """
    Identifie les signaux d’alarme dans une description de symptômes.

    Args:
        symptoms: Description textuelle des symptômes

    Returns:
        Liste des red flags détectés et recommandations d’urgence
    """
    symptoms_lower = symptoms.lower()

    red_flags_db = {
        "douleur thoracique": "Possible syndrome coronarien -- urgence cardiologique",
        "difficulte respiratoire": "Détresse respiratoire -- appel 15 immédiat",
        "perte de connaissance": "Syncope -- évaluation urgente",
        "paralysie": "AVC possible -- protocole FAST, appel 15",
        "convulsion": "Crise épileptique -- appel 15",
        "hemorragie": "Saignement important -- urgences chirurgicales",
        "fievre > 40": "Hyperthermie sévère -- évaluation urgente",
        "raideur nuque": "Méningite possible -- urgences immédiates",
        "douleur abdominale severe": "Abdomen aigu -- bilan chirurgical urgent"
    }

    detected = []
    for flag, description in red_flags_db.items():
        if flag in symptoms_lower:
            detected.append({"symptome": flag, "risque": description})

    return json.dumps({
        "red_flags_detectes": detected,
        "count": len(detected),
        "urgence": len(detected) > 0,
        "action": "APPEL 15 RECOMMANDE" if len(detected) > 0 else "Surveillance standard",
        "avertissement": "Cette détection automatique ne remplace pas l’évaluation clinique."
    }, ensure_ascii=False, indent=2)


# -- Point d’entrée -------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")
    # Pour un serveur HTTP :
    # mcp.run(transport="sse", port=8001)