import os
import yaml
from google.cloud import storage

def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_config():
    """Llegeix la configuració des de GCS (si GCS_CONFIG_URI està definit) o localment."""
    gcs_uri = os.getenv("GCS_CONFIG_URI")
    if gcs_uri and gcs_uri.startswith("gs://"):
        try:
            print(f"Descarregant configuració des de {gcs_uri}...")
            client = storage.Client()
            bucket_name = gcs_uri.split("/")[2]
            blob_name = "/".join(gcs_uri.split("/")[3:])
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            yaml_content = blob.download_as_text()
            return yaml.safe_load(yaml_content)
        except Exception as e:
            print(f"Error descarregant config des de GCS: {e}. Utilitzant fallback local.")
    
    # Fallback local
    local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml")
    return load_yaml(local_path)

def load_airports():
    local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "airports.yaml")
    return load_yaml(local_path)
