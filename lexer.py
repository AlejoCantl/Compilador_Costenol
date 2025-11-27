import ply.lex as lex

class AnalizadorLexico:
    """Analizador léxico"""
    
    def __init__(self):
        self.errores = []
        self.lexer = None
        
    def construir(self):
        """Construye el lexer de PLY"""
        self.lexer = lex.lex(module=self)
        return self.lexer
    
    def reset(self):
        """Limpia el estado del lexer"""
        self.errores.clear()
        if self.lexer:
            self.lexer.lineno = 1
    
    def tokenizar(self, codigo):
        """Tokeniza el código y retorna lista de tokens"""
        self.lexer.input(codigo)
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens
    
    # ===================== DEFINICIÓN DE TOKENS =====================
    
    tokens = (
        'IGUAL', 'MAS', 'MENOS', 'POR', 'DIVIDIDO',
        'NUMERO_ENTERO', 'NUMERO_REAL', 'IDENTIFICADOR',
        'PARENTESIS_IZQ', 'PARENTESIS_DER',
        'PUNTO_Y_COMA', 'CADENA_TEXTO', 'PUNTO'
    )
    
    # Palabras reservadas
    reservadas = {
        'Texto': 'TEXTO',
        'Entero': 'ENTERO',
        'Real': 'REAL',
        'Captura': 'CAPTURA',
        'Mensaje': 'MENSAJE'
    }
    
    tokens = tokens + tuple(reservadas.values())
    
    # ===================== TOKENS SIMPLES =====================
    
    t_IGUAL = r'='
    t_MAS = r'\+'
    t_MENOS = r'-'
    t_POR = r'\*'
    t_DIVIDIDO = r'/'
    t_PARENTESIS_IZQ = r'\('
    t_PARENTESIS_DER = r'\)'
    t_PUNTO_Y_COMA = r';'
    t_PUNTO = r'\.'
    
    # Ignorar espacios y tabs
    t_ignore = ' \t'
    
    # ===================== TOKENS COMPLEJOS =====================
    
    # IMPORTANTE: El orden importa - las funciones se evalúan antes que los strings
    
    def t_CARACTER_ESPECIAL_PEGADO_A_LETRA(self, t):
        r'[$@#%&!?~`|\\^<>\[\]{}]+[a-zA-Z_][a-zA-Z0-9_]*'
        self.errores.append({
            'tipo': 'error',
            'linea': t.lineno,
            'mensaje': f"¡Eche tú que ve! Las variables no pueden empezar con simbolos especiales: '{t.value}'"
        })
        # NO retornar token - esto previene que se use como identificador válido
        t.lexer.skip(len(t.value))
    
    def t_NUMERO_PEGADO_A_LETRA(self, t):
        r'\d+[a-zA-Z_][a-zA-Z0-9_]*'
        self.errores.append({
            'tipo': 'error',
            'linea': t.lineno,
            'mensaje': f"¡Eche tú que ve! Las variables no pueden empezar con números: '{t.value}'"
        })
        # NO retornar token - esto previene que se use como identificador válido
        t.lexer.skip(len(t.value))
    
    def t_IDENTIFICADOR(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        # Verificar si es palabra reservada
        t.type = self.reservadas.get(t.value, 'IDENTIFICADOR')
        return t
    
    def t_NUMERO_REAL(self, t):
        r'\d+[,.]\d+'
        # Normalizar: aceptar coma o punto
        t.value = float(t.value.replace(',', '.'))
        return t
    
    def t_NUMERO_ENTERO(self, t):
        r'\d+'
        t.value = int(t.value)
        return t
    
    def t_CADENA_TEXTO(self, t):
        r'\"([^\\\n]|(\\.))*?\"'
        # Remover comillas
        t.value = t.value[1:-1]
        return t
    
    # ===================== COMENTARIOS =====================
    
    def t_COMENTARIO_SIMPLE(self, t):
        r'//.*'
        pass  # Ignorar comentarios
    
    def t_COMENTARIO_MULTILINEA(self, t):
        r'/\*[\s\S]*?\*/'
        # Contar líneas en el comentario
        t.lexer.lineno += t.value.count('\n')
        pass  # Ignorar comentarios
    
    # ===================== CONTROL DE LÍNEAS =====================
    
    def t_nueva_linea(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    # ===================== MANEJO DE ERRORES =====================
    
    def t_error(self, t):
        """Manejo de caracteres ilegales"""
        self.errores.append({
            'tipo': 'error',
            'linea': t.lineno,
            'mensaje': f"Carácter ilegal: '{t.value[0]}'"
        })
        t.lexer.skip(1)