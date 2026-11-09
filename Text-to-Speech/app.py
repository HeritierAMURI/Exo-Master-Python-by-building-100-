#!/usr/bin/env python3
"""Application Flask de conversion de PDF en livre audio français.

Installation :
    python -m pip install Flask Flask-WTF pypdf gTTS

Lancement depuis ce dossier :
    python app.py

Ouvrez ensuite http://127.0.0.1:5000 dans votre navigateur.
En production, définissez également FLASK_SECRET_KEY avec une clé secrète stable.
gTTS requiert une connexion Internet et transmet le texte extrait à Google
pour la synthèse vocale.
"""

import logging
import os
import secrets
import shutil
import uuid
from pathlib import Path

from flask import Flask, Response, abort, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
from gtts import gTTS
from gtts.tts import gTTSError
from pypdf import PdfReader
from pypdf.errors import PdfReadError


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 26 * 1024 * 1024
CSRFProtect(app)

JOB_DIRECTORY = Path(app.instance_path) / "audiobooks"
MAX_PDF_SIZE_MB = 25

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserFacingError(Exception):
    """Erreur de traitement pouvant être affichée sans détail technique."""


def extract_pdf_text(pdf_path: Path) -> str:
    """Extrait le texte de chaque page et traite les PDF illisibles."""
    try:
        reader = PdfReader(str(pdf_path))
        if reader.is_encrypted:
            raise UserFacingError(
                "Ce PDF est protégé par mot de passe. "
                "Veuillez envoyer une version non protégée."
            )

        pages = []
        total_pages = len(reader.pages)
        for page_number, page in enumerate(reader.pages, start=1):
            logger.info("Extraction de la page %s/%s", page_number, total_pages)
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text.strip())
    except UserFacingError:
        raise
    except (PdfReadError, OSError, ValueError) as error:
        logger.info("PDF illisible ou endommagé : %s", error)
        raise UserFacingError(
            "Ce fichier PDF est corrompu ou illisible. "
            "Vérifiez le document et réessayez."
        ) from error
    except Exception as error:
        logger.exception("Erreur inattendue pendant la lecture du PDF")
        raise UserFacingError(
            "Impossible de lire ce PDF. Vérifiez que le document n'est pas "
            "endommagé et réessayez."
        ) from error

    text = "\n\n".join(pages).strip()
    if not text:
        raise UserFacingError(
            "Aucun texte n'a été trouvé dans ce PDF. "
            "Les documents numérisés sans texte sélectionnable ne sont pas pris en charge."
        )
    return text


def cleanup_job(job_directory: Path) -> None:
    """Supprime les fichiers temporaires d'une conversion et signale les échecs."""
    try:
        shutil.rmtree(job_directory)
    except FileNotFoundError:
        pass
    except OSError:
        logger.exception("Impossible de supprimer les fichiers temporaires de %s", job_directory)


@app.get("/")
def index():
    """Affiche le formulaire de dépôt du PDF."""
    return render_template("index.html", max_pdf_size_mb=MAX_PDF_SIZE_MB)


@app.post("/convert")
def convert():
    """Valide le PDF, le convertit, puis affiche le bouton de téléchargement."""
    uploaded_file = request.files.get("pdf")
    if uploaded_file is None or not uploaded_file.filename:
        return (
            render_template(
                "index.html",
                error="Sélectionnez un fichier PDF avant de lancer la conversion.",
                max_pdf_size_mb=MAX_PDF_SIZE_MB,
            ),
            400,
        )

    safe_filename = secure_filename(uploaded_file.filename)
    if not safe_filename or Path(safe_filename).suffix.lower() != ".pdf":
        return (
            render_template(
                "index.html",
                error="Le fichier sélectionné doit être au format PDF.",
                max_pdf_size_mb=MAX_PDF_SIZE_MB,
            ),
            400,
        )

    job_id = uuid.uuid4().hex
    job_directory = JOB_DIRECTORY / job_id
    pdf_path = job_directory / "source.pdf"
    audio_path = job_directory / "audiobook.mp3"

    try:
        job_directory.mkdir(parents=True, exist_ok=False)
        uploaded_file.save(pdf_path)
        if pdf_path.stat().st_size > MAX_PDF_SIZE_MB * 1024 * 1024:
            raise UserFacingError(
                f"Le fichier dépasse la limite de {MAX_PDF_SIZE_MB} Mo."
            )
        text = extract_pdf_text(pdf_path)
        try:
            gTTS(text=text, lang="fr").save(str(audio_path))
        except (gTTSError, OSError) as error:
            logger.warning("Échec de la synthèse vocale : %s", error)
            raise UserFacingError(
                "La synthèse vocale a échoué. Vérifiez votre connexion Internet "
                "puis réessayez."
            ) from error

        if not audio_path.is_file() or audio_path.stat().st_size == 0:
            raise UserFacingError(
                "La génération audio n'a pas abouti. Veuillez réessayer."
            )
    except UserFacingError as error:
        cleanup_job(job_directory)
        return (
            render_template(
                "index.html",
                error=str(error),
                max_pdf_size_mb=MAX_PDF_SIZE_MB,
            ),
            400,
        )
    except OSError as error:
        logger.exception("Erreur de lecture ou d'écriture pendant la conversion")
        cleanup_job(job_directory)
        return (
            render_template(
                "index.html",
                error="Une erreur est survenue pendant le traitement du fichier. "
                "Veuillez réessayer.",
                max_pdf_size_mb=MAX_PDF_SIZE_MB,
            ),
            500,
        )
    except Exception:
        logger.exception("Erreur inattendue pendant la conversion")
        cleanup_job(job_directory)
        return (
            render_template(
                "index.html",
                error="La conversion a échoué de manière inattendue. "
                "Veuillez réessayer.",
                max_pdf_size_mb=MAX_PDF_SIZE_MB,
            ),
            500,
        )
    finally:
        try:
            pdf_path.unlink(missing_ok=True)
        except OSError:
            logger.exception("Impossible de supprimer le PDF temporaire %s", pdf_path)

    return render_template(
        "index.html",
        audio_url=url_for("download_audio", job_id=job_id),
        max_pdf_size_mb=MAX_PDF_SIZE_MB,
        original_filename=safe_filename,
    )


@app.get("/download/<job_id>")
def download_audio(job_id: str):
    """Envoie un MP3 généré, puis supprime les fichiers de cette conversion."""
    if len(job_id) != 32:
        abort(404)
    try:
        uuid.UUID(hex=job_id)
    except ValueError:
        abort(404)

    job_directory = JOB_DIRECTORY / job_id
    audio_path = job_directory / "audiobook.mp3"
    if not audio_path.is_file():
        abort(404)

    audio_size = audio_path.stat().st_size

    def stream_audio():
        try:
            with audio_path.open("rb") as audio_file:
                while True:
                    chunk = audio_file.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
        finally:
            cleanup_job(job_directory)

    response = Response(stream_audio(), mimetype="audio/mpeg")
    response.headers.set(
        "Content-Disposition", "attachment", filename="livre-audio.mp3"
    )
    response.content_length = audio_size
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.call_on_close(lambda: cleanup_job(job_directory))
    return response


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_error):
    """Affiche une erreur claire lorsque l'envoi dépasse la limite autorisée."""
    return (
        render_template(
            "index.html",
            error=f"Le fichier dépasse la limite de {MAX_PDF_SIZE_MB} Mo.",
            max_pdf_size_mb=MAX_PDF_SIZE_MB,
        ),
        413,
    )


if __name__ == "__main__":
    app.run(debug=False)
