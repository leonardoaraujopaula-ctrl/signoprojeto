import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Signos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            simbolo TEXT NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL,
            elemento TEXT NOT NULL,
            descricao TEXT NOT NULL
        )
    ''')

    # Nova Tabela de Consultas (Histórico de ocorrências)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consulta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signo_id INTEGER NOT NULL,
            data_nascimento TEXT NOT NULL,
            data_ocorrencia TEXT NOT NULL,
            FOREIGN KEY (signo_id) REFERENCES signos (id)
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM signos')
    if cursor.fetchone()[0] == 0:
        signos_dados = [
            ('Áries', '♈', '03-21', '04-19', 'Fogo 🔥', 'Impulsivos, corajosos e cheios de energia. Adoram novos desafios e liderança.'),
            ('Touro', '♉', '04-20', '05-20', 'Terra 🌿', 'Práticos, leais e determinados. Valorizam o conforto, a estabilidade e os prazeres da vida.'),
            ('Gêmeos', '♊', '05-21', '06-20', 'Ar 💨', 'Comunicativos, curiosos e versáteis. Adaptam-se facilmente e adoram aprender coisas novas.'),
            ('Câncer', '♋', '06-21', '07-22', 'Água 💧', 'Emotivos, protetores e intuitivos. Têm forte ligação com a família, o lar e as memórias.'),
            ('Leão', '♌', '07-23', '08-22', 'Fogo 🔥', 'Criativos, generosos e autoconfiantes. Gostam de brilhar e inspirar as pessoas ao redor.'),
            ('Virgem', '♍', '08-23', '09-22', 'Terra 🌿', 'Analíticos, organizados e prestativos. Prezam pela perfeição e atenção aos detalhes.'),
            ('Libra', '♎', '09-23', '10-22', 'Ar 💨', 'Diplomáticos, sociáveis e amantes da harmonia. Buscam equilíbrio e justiça em tudo.'),
            ('Escorpião', '♏', '10-23', '11-21', 'Água 💧', 'Intensos, misteriosos e apaixonados. Possuem grande força emocional e intuição aguçada.'),
            ('Sagitário', '♐', '11-22', '12-21', 'Fogo 🔥', 'Aventureiros, otimistas e filosóficos. Amam a liberdade, viagens e novos horizontes.'),
            ('Capricórnio', '♑', '12-22', '01-19', 'Terra 🌿', 'Ambiciosos, disciplinados e responsáveis. Focam nos objetivos de longo prazo com paciência.'),
            ('Aquário', '♒', '01-20', '02-18', 'Ar 💨', 'Inovadores, independentes e humanitários. Pensam fora da caixa e valorizam a originalidade.'),
            ('Peixes', '♓', '02-19', '03-20', 'Água 💧', 'Sonhadores, empáticos e artísticos. Têm grande sensibilidade e conexão espiritual.')
        ]
        cursor.executemany('''
            INSERT INTO signos (nome, simbolo, data_inicio, data_fim, elemento, descricao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', signos_dados)
        conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/descobrir', methods=['POST'])
def descobrir():
    data_nascimento = request.form.get('data_nascimento')
    if not data_nascimento:
        return redirect(url_for('index'))
    
    mes_dia = data_nascimento[5:]
    
    conn = get_db_connection()
    signos = conn.execute('SELECT * FROM signos').fetchall()
    
    signo_encontrado = None
    for s in signos:
        if s['nome'] == 'Capricórnio':
            if mes_dia >= s['data_inicio'] or mes_dia <= s['data_fim']:
                signo_encontrado = s
                break
        else:
            if s['data_inicio'] <= mes_dia <= s['data_fim']:
                signo_encontrado = s
                break
                
    if signo_encontrado:
        # Registra a ocorrência na tabela consulta
        data_ocorrencia = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        conn.execute('''
            INSERT INTO consulta (signo_id, data_nascimento, data_ocorrencia)
            VALUES (?, ?, ?)
        ''', (signo_encontrado['id'], data_nascimento, data_ocorrencia))
        conn.commit()
        conn.close()
        
        return redirect(url_for('resultado', signo_id=signo_encontrado['id']))
        
    conn.close()
    return redirect(url_for('index'))

@app.route('/resultado/<int:signo_id>')
def resultado(signo_id):
    conn = get_db_connection()
    signo = conn.execute('SELECT * FROM signos WHERE id = ?', (signo_id,)).fetchone()
    conn.close()
    
    if signo is None:
        return redirect(url_for('index'))
        
    return render_template('resultado.html', signo=signo)

# Rota extra para visualizar o histórico de consultas gravadas no banco
@app.route('/historico')
def historico():
    conn = get_db_connection()
    consultas = conn.execute('''
        SELECT c.id, s.nome AS signo_nome, s.simbolo, c.data_nascimento, c.data_ocorrencia
        FROM consulta c
        JOIN signos s ON c.signo_id = s.id
        ORDER BY c.id DESC
    ''').fetchall()
    conn.close()
    return render_template('historico.html', consultas=consultas)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)