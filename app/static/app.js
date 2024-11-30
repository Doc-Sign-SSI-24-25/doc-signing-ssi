async function createKey() {
    var result = document.getElementById('result');
    result.innerHTML = '';
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;

    // Validação básica
    if (!name || !email) {
        var p = document.createElement('p');
        p.classList.add('text-danger');
        p.innerHTML = 'Por favor, preencha nome e email';
        result.appendChild(p);
        return;
    }

    try {
        var res = await fetch('http://localhost:8000/create_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: name, email: email })
        });

        if (!res.ok) {
            // Tenta obter o erro detalhado do servidor
            const errorData = await res.json();
            throw new Error(errorData.detail || 'Erro ao criar chave');
        }

        const json = await res.json();
        
        // Cria um arquivo com a chave privada
        var file = new File([json.private_key], json.filename, { type: 'text/plain' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(file);
        a.download = json.filename;
        a.classList.add('btn', 'btn-outline-dark', 'my-3');
        a.innerHTML = 'Download Key';
        result.appendChild(a);
    } catch (error) {
        var p = document.createElement('p');
        p.classList.add('text-danger');
        p.innerHTML = error.message;
        result.appendChild(p);
        console.error('Error:', error);
    }
}