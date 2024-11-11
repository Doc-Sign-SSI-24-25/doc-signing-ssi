from dotenv import load_dotenv
import os

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a URI diretamente do .env
MONGODB_URI = os.getenv("MONGODB_URI")

# Nome do banco de dados
DATABASE_NAME = "digital_signature_db"

# Verificar se a URI foi carregada corretamente
if MONGODB_URI is None:
    raise ValueError("A URI do MongoDB não foi definida no arquivo .env.")