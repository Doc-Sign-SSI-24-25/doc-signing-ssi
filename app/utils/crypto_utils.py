import hashlib

def create_hash(input_file: bytes, algorithm: str = "sha256") -> str:
    """
    Cria um hash a partir de um arquivo em bytes.

    :param input_file: O conteúdo do arquivo em bytes.
    :param algorithm: O algoritmo de hash a ser utilizado (padrão: 'sha256').
    :return: O hash gerado em formato hexadecimal.
    """
    try:
        hash_func = hashlib.new(algorithm)
        hash_func.update(input_file)
        return hash_func.hexdigest()
    except ValueError:
        raise ValueError(f"Algoritmo de hash '{algorithm}' não é suportado.")

def verify_hash(input_file: bytes, hash: str, algorithm: str = "sha256") -> bool:
    """
    Verifica se o hash gerado a partir do arquivo em bytes corresponde ao hash esperado.

    :param input_file: O conteúdo do arquivo em bytes.
    :param hash: O hash esperado para comparação.
    :param algorithm: O algoritmo de hash a ser utilizado (padrão: 'sha256').
    :return: True se os hashes corresponderem, False caso contrário.
    """
    hash_gerado = create_hash(input_file, algorithm)
    return hash_gerado == hash