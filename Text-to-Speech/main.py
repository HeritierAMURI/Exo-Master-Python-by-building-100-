#!/usr/bin/env python3
"""Convertit un fichier PDF en livre audio français au format MP3.

Installation des dépendances (dans un terminal) :
    python -m pip install pypdf gTTS

Utilisation :
    python main.py
    python main.py "mon document.pdf"
    python main.py "mon document.pdf" --output "mon livre audio.mp3"

gTTS utilise le service Google Text-to-Speech et nécessite une connexion
Internet. Le texte du PDF est envoyé à ce service pour la synthèse vocale.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from gtts import gTTS
from gtts.tts import gTTSError
from pypdf import PdfReader
from pypdf.errors import PdfReadError


ORANGE = "\033[38;2;209;148;26m"  # #d1941a
ORANGE_CLAIR = "\033[38;2;224;176;69m"  # #e0b045
RESET = "\033[0m"


def afficher_titre(message: str) -> None:
    """Affiche un titre ou un résultat important avec la couleur d'accent."""
    print(f"{ORANGE}{message}{RESET}")


def afficher_etape(message: str) -> None:
    """Affiche une étape ou un détail avec la couleur d'accent claire."""
    print(f"{ORANGE_CLAIR}{message}{RESET}")


def extraire_texte(pdf_path: Path) -> str:
    """Extrait et rassemble le texte du PDF, en signalant chaque page."""
    try:
        reader = PdfReader(str(pdf_path))
        if reader.is_encrypted:
            raise ValueError(
                "Ce PDF est protégé par mot de passe et ne peut pas être lu."
            )

        pages = []
        for numero, page in enumerate(reader.pages, start=1):
            afficher_etape(f"Extraction de la page {numero}/{len(reader.pages)}...")
            texte_page = page.extract_text() or ""
            if texte_page.strip():
                pages.append(texte_page.strip())
    except PdfReadError as erreur:
        raise ValueError(f"Le PDF est illisible ou endommagé : {erreur}") from erreur

    texte = "\n\n".join(pages).strip()
    if not texte:
        raise ValueError("Aucun texte extractible n'a été trouvé dans ce PDF.")
    return texte


def convertir_en_audio(texte: str, output_path: Path) -> None:
    """Synthétise le texte en français et enregistre le résultat en MP3."""
    afficher_etape("Conversion en cours (français)...")
    try:
        gTTS(text=texte, lang="fr").save(str(output_path))
    except (gTTSError, OSError) as erreur:
        raise RuntimeError(
            "La synthèse vocale a échoué. Vérifiez votre connexion Internet "
            f"puis réessayez. Détail : {erreur}"
        ) from erreur


def demander_pdf() -> str:
    """Demande le chemin du PDF lorsque le script est lancé sans argument."""
    afficher_etape("Chemin du fichier PDF à convertir :")
    return input().strip().strip('"')


def construire_analyseur() -> argparse.ArgumentParser:
    """Construit l'analyseur des arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Convertit un fichier PDF en livre audio français (.mp3)."
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        help="chemin du PDF (si absent, le script le demandera)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="chemin du MP3 de sortie (par défaut : nom du PDF avec .mp3)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Exécute le processus de conversion et renvoie le code de sortie."""
    args = construire_analyseur().parse_args(argv)
    chemin_pdf = args.pdf if args.pdf else demander_pdf()
    if not chemin_pdf:
        afficher_titre("Erreur : aucun fichier PDF n'a été indiqué.")
        return 1

    pdf_path = Path(chemin_pdf).expanduser()
    if not pdf_path.is_file():
        afficher_titre(f"Erreur : fichier introuvable : {pdf_path}")
        return 1

    output_path = (
        Path(args.output).expanduser()
        if args.output
        else pdf_path.with_suffix(".mp3")
    )

    afficher_titre("=== Conversion PDF en livre audio ===")
    afficher_etape(f"Fichier source : {pdf_path}")
    try:
        texte = extraire_texte(pdf_path)
        convertir_en_audio(texte, output_path)
    except (OSError, PermissionError, ValueError, RuntimeError) as erreur:
        afficher_titre(f"Erreur : {erreur}")
        return 1

    afficher_titre(f"Conversion terminée : {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
