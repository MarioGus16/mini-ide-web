const editor = CodeMirror.fromTextArea(document.getElementById('code'), {
    lineNumbers: true,
    mode: 'python',
    theme: 'default'
});

let errorMarkers = [];

function clearErrorMarkers() {
    errorMarkers.forEach(marker => marker.clear());
    errorMarkers = [];
}

function markError(line, column, message) {
    const lineIndex = line - 1;
    const chIndex = Math.max(column - 1, 0);
    const lineContent = editor.getLine(lineIndex);

    const from = { line: lineIndex, ch: chIndex };
    const to = { line: lineIndex, ch: lineContent.length };

    const marker = editor.markText(from, to, {
        className: 'error-marker',
        title: message
    });
    errorMarkers.push(marker);
}

function traducirTipo(tipo) {
    const mapa = {
        'NUMERO': 'Número',
        'ID': 'Identificador',
        'ASIGNAR': 'Asignación (=)',
        'OP': 'Operador',
        'PAR_IZQ': 'Paréntesis izquierdo',
        'PAR_DER': 'Paréntesis derecho',
        'ESPACIO': 'Espacio',
        'SALTO': 'Salto de línea',
        'DESCONOCIDO': 'Desconocido'
    };
    return mapa[tipo] || tipo;
}

function traducirEstadoTuring(estado) {
    const mapa = {
        'ACCEPT': 'ACEPTADO',
        'REJECT': 'RECHAZADO'
    };
    return mapa[estado] || estado;
}

function analyze(mode, realtime = false) {
    const code = editor.getValue();
    if (!realtime) document.getElementById('output').innerHTML = '';
    clearErrorMarkers();

    if (realtime) {
        const lines = code.split('\n');
        lines.forEach((lineText, i) => {
            fetch(`/analyze/${mode}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: lineText })
            })
            .then(res => res.json())
            .then(data => {
                if (data.errors && data.errors.length > 0) {
                    data.errors.forEach(err => {
                        if (typeof err === 'object' && err.line && err.column && err.message) {
                            let mensaje = err.message;
                            if (mensaje.toLowerCase().includes("falta signo de asignación") || 
                                mensaje.toLowerCase().includes("asignación") ||
                                (mensaje.toLowerCase().includes("asignar") && lineText.includes('='))) {
                                mensaje = "Falta asignarle valor";
                            }
                            markError(i + 1, err.column, mensaje);
                        }
                    });
                }
            });
        });
        return;
    }

    // Modo normal (por botón)
    fetch(`/analyze/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    })
    .then(res => res.json())
    .then(data => {
        const out = document.getElementById('output');

        if (data.tokens && !realtime) {
            let html = `<h5>Tokens</h5><table class="table table-bordered token-table"><thead><tr><th>Tipo</th><th>Valor</th><th>Línea</th><th>Columna</th></tr></thead><tbody>`;
            data.tokens.forEach(tok => {
                html += `<tr>
                    <td>${traducirTipo(tok.type)}</td>
                    <td>${tok.value}</td>
                    <td>${tok.line}</td>
                    <td>${tok.column}</td>
                </tr>`;
            });
            html += `</tbody></table>`;
            out.innerHTML += html;
        }

        if (data.errors && data.errors.length > 0) {
            data.errors.forEach(err => {
                if (typeof err === 'object' && err.line && err.column && err.message) {
                    let mensaje = err.message;
                    if (mensaje.toLowerCase().includes("falta signo de asignación") || 
                        mensaje.toLowerCase().includes("asignación") ||
                        (mensaje.toLowerCase().includes("asignar") && code.includes('='))) {
                        mensaje = "Falta asignarle valor";
                    }
                    markError(err.line, err.column, mensaje);
                    out.innerHTML += `<div class="alert alert-danger">Error en línea ${err.line}, columna ${err.column}: ${mensaje}</div>`;
                } else {
                    out.innerHTML += `<div class="alert alert-danger">${String(err)}</div>`;
                }
            });
        }

        if (data.success) {
            if (Array.isArray(data.success)) {
                out.innerHTML += `<div class="alert alert-success">${data.success.join('<br>')}</div>`;
            } else {
                out.innerHTML += `<div class="alert alert-success">${data.success}</div>`;
            }
        }

        if (data.turing_result !== undefined && !realtime) {
            out.innerHTML += 
                `<div class="card mt-4">
                    <div class="card-body">
                        <h5 class="card-title">Máquina de Turing</h5>
                        <p><strong>Resultado:</strong> 
                            <span class="badge ${data.turing_result ? 'bg-success' : 'bg-danger'}">
                                ${data.turing_result ? 'ACEPTADO' : 'RECHAZADO'}
                            </span>
                        </p>
                        <div class="alert alert-info">
                            <h6 class="mb-2">¿Cómo funciona esta Máquina de Turing?</h6>
                            <ul class="mb-0">
                                <li>La máquina acepta cadenas formadas por pares ordenados de "10"</li>
                                <li>Por ejemplo: "1010" o "101010" son válidas</li>
                                <li>La cadena debe tener longitud par</li>
                                <li>Cada par debe comenzar con "1" y terminar con "0"</li>
                                <li>Solo se permiten los símbolos "1" y "0"</li>
                            </ul>
                        </div>
                    </div>
                </div>`;
        }
    });
}

editor.on('change', () => {
    analyze('syntactic', true);
}); 