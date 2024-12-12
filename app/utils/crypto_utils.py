import hashlib

def create_hash(input_file: bytes) -> str:
    """
    Cria um hash a partir de um arquivo em bytes.

    :param input_file: O conteúdo do arquivo em bytes.
    O algoritmo de hash a ser utilizado é 'sha256').
    :return: O hash gerado em formato hexadecimal.
    """
    hash_func = hashlib.new("sha256")
    hash_func.update(input_file)
    return hash_func.hexdigest()


def verify_hash(input_file: bytes, hash: str) -> bool:
    """
    Verifica se o hash gerado a partir do arquivo em bytes corresponde ao hash esperado.

    :param input_file: O conteúdo do arquivo em bytes.
    :param hash: O hash esperado para comparação.
    O algoritmo de hash a ser utilizado é 'sha256').
    :return: True se os hashes corresponderem, False caso contrário.
    """
    hash_gerado = create_hash(input_file)
    return hash_gerado == hash