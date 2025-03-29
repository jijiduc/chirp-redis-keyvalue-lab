#!/usr/bin/env python3
"""
Script pour traiter les fichiers de tweets au format JSONL compressés en bz2
"""

import json
import bz2
import os
from pathlib import Path

def process_jsonl_bz2_files(input_dir, output_dir):
    """Traite les fichiers JSONL compressés en bz2 et extrait les tweets en anglais"""
    # Créer le répertoire de sortie
    os.makedirs(output_dir, exist_ok=True)
    
    # Trouver tous les fichiers .bz2
    bz2_files = list(Path(input_dir).glob("*.json.bz2"))
    print(f"Trouvé {len(bz2_files)} fichiers .bz2")
    
    if not bz2_files:
        print(f"Aucun fichier .bz2 trouvé dans {input_dir}")
        return
    
    # Traiter chaque fichier
    all_english_tweets = []
    for file_path in bz2_files:
        print(f"Traitement de {file_path}...")
        try:
            english_tweets_in_file = 0
            
            # Ouvrir le fichier bz2 et lire ligne par ligne
            with bz2.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Ignorer les lignes vides
                        continue
                    
                    try:
                        # Analyser chaque ligne comme un objet JSON indépendant
                        tweet = json.loads(line)
                        
                        # Vérifier si le tweet est en anglais
                        if tweet.get('lang') == 'en':
                            all_english_tweets.append(tweet)
                            english_tweets_in_file += 1
                    except json.JSONDecodeError as je:
                        print(f"  Erreur de décodage JSON dans {file_path}: {je}")
                        continue
            
            print(f"  {english_tweets_in_file} tweets en anglais trouvés dans {file_path.name}")
        
        except Exception as e:
            print(f"Erreur lors du traitement de {file_path}: {e}")
    
    # Sauvegarder les résultats
    print(f"Total: {len(all_english_tweets)} tweets en anglais")
    
    if all_english_tweets:
        sample_size = min(1000, len(all_english_tweets))
        sample_file = os.path.join(output_dir, "english_sample.json")
        
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(all_english_tweets[:sample_size], f, ensure_ascii=False, indent=2)
        
        print(f"Échantillon de {sample_size} tweets sauvegardé dans {sample_file}")
    else:
        print("Aucun tweet en anglais trouvé pour créer un échantillon.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = "./data/twitter_data"
    
    output_dir = "./data/processed"
    process_jsonl_bz2_files(input_dir, output_dir)