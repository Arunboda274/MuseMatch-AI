from pathlib import Path

import librosa
import numpy as np


def clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    return max(minimum, min(value, maximum))


def normalize_db(
    value: float,
    minimum: float = -60.0,
    maximum: float = 0.0,
) -> float:
    normalized = (value - minimum) / (maximum - minimum)
    return clamp(normalized)


def analyze_audio_file(
    file_path: str | Path,
) -> dict[str, float]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            "Audio file was not found."
        )

    audio, sample_rate = librosa.load(
        path,
        sr=None,
        mono=True,
    )

    if audio.size == 0:
        raise ValueError(
            "The uploaded audio file is empty."
        )

    duration_seconds = librosa.get_duration(
        y=audio,
        sr=sample_rate,
    )

    tempo_values = librosa.feature.tempo(
        y=audio,
        sr=sample_rate,
    )

    tempo = (
        float(tempo_values[0])
        if len(tempo_values)
        else 0.0
    )

    rms = librosa.feature.rms(
        y=audio,
    )[0]

    average_rms = float(
        np.mean(rms)
    )

    energy = clamp(
        average_rms * 10
    )

    onset_strength = librosa.onset.onset_strength(
        y=audio,
        sr=sample_rate,
    )

    rhythmic_strength = float(
        np.mean(onset_strength)
    )

    danceability = clamp(
        0.55 * min(
            tempo / 180.0,
            1.0,
        )
        + 0.45 * min(
            rhythmic_strength / 4.0,
            1.0,
        )
    )

    spectral_centroid = (
        librosa.feature.spectral_centroid(
            y=audio,
            sr=sample_rate,
        )[0]
    )

    average_centroid = float(
        np.mean(spectral_centroid)
    )

    acousticness = clamp(
        1.0 - average_centroid / 5000.0
    )

    harmonic, percussive = librosa.effects.hpss(
        audio
    )

    harmonic_energy = float(
        np.mean(
            np.abs(harmonic)
        )
    )

    percussive_energy = float(
        np.mean(
            np.abs(percussive)
        )
    )

    total_component_energy = (
        harmonic_energy
        + percussive_energy
    )

    if total_component_energy > 0:
        instrumentalness = clamp(
            harmonic_energy
            / total_component_energy
        )
    else:
        instrumentalness = 0.0

    zero_crossing_rate = (
        librosa.feature.zero_crossing_rate(
            audio
        )[0]
    )

    speechiness = clamp(
        float(
            np.mean(zero_crossing_rate)
        )
        * 4
    )

    spectral_contrast = (
        librosa.feature.spectral_contrast(
            y=audio,
            sr=sample_rate,
        )
    )

    liveness = clamp(
        float(
            np.std(spectral_contrast)
        )
        / 20.0
    )

    chroma = librosa.feature.chroma_stft(
        y=audio,
        sr=sample_rate,
    )

    valence = clamp(
        float(
            np.mean(chroma)
        )
        * 2.5
    )

    loudness = float(
        librosa.amplitude_to_db(
            np.array(
                [
                    max(
                        average_rms,
                        1e-10,
                    )
                ]
            )
        )[0]
    )

    return {
        "duration_seconds": round(
            float(duration_seconds),
            2,
        ),
        "tempo": round(
            tempo,
            2,
        ),
        "energy": round(
            energy,
            4,
        ),
        "danceability": round(
            danceability,
            4,
        ),
        "acousticness": round(
            acousticness,
            4,
        ),
        "instrumentalness": round(
            instrumentalness,
            4,
        ),
        "liveness": round(
            liveness,
            4,
        ),
        "speechiness": round(
            speechiness,
            4,
        ),
        "valence": round(
            valence,
            4,
        ),
        "loudness": round(
            loudness,
            2,
        ),
        "sample_rate": float(
            sample_rate
        ),
    }