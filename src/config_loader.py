import os
import yaml
from google.cloud import storage

def load_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_config():
    """Llegeix la configuració des de GCS (si GCS_CONFIG_URI està definit) o localment."""
    gcs_uri = (os.getenv("GCS_CONFIG_URI") or "").strip("\"' \t\r\n")
    if gcs_uri:
        if gcs_uri.startswith("gs://"):
            try:
                print(f"Descarregant configuració des de {gcs_uri}...")
                client = storage.Client()
                bucket_name = gcs_uri.split("/")[2]
                blob_name = "/".join(gcs_uri.split("/")[3:])
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                yaml_content = blob.download_as_text()
                print("Configuració descarregada correctament de GCS!")
                return yaml.safe_load(yaml_content)
            except Exception as e:
                print(f"Error descarregant config des de GCS: {e}. Utilitzant fallback local.")
        else:
            print(f"Avís: GCS_CONFIG_URI '{gcs_uri}' no comença per 'gs://'.")
    else:
        print("GCS_CONFIG_URI no està definit. Utilitzant configuració local.")
    
    # Fallback local (primer busca config.yaml, si no existeix usa config_template.yaml)
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
    local_path = os.path.join(config_dir, "config.yaml")
    
    if not os.path.exists(local_path):
        template_path = os.path.join(config_dir, "config_template.yaml")
        if os.path.exists(template_path):
            print("Avís: No s'ha trobat 'config.yaml'. S'utilitzarà 'config_template.yaml'.")
            return load_yaml(template_path)
            
    return load_yaml(local_path)

def load_airports():
    local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "airports.yaml")
    return load_yaml(local_path)
