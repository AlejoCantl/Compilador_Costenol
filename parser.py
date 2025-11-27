import ply.yacc as yacc
from lexer import AnalizadorLexico
from semantic import AnalizadorSemantico

class AnalizadorSintactico:
    """Parser sintáctico - Aprovecha PLY al máximo con recuperación inteligente"""
    
    def __init__(self, lexer, semantico):
        self.lexer_obj = lexer
        self.semantico = semantico
        self.tokens = lexer.tokens
        self.parser = None
        
        # Control de errores
        self.errores_sintacticos = []
        self.lineas_con_error = set()
        self.ultima_linea_completa = 0
        self.ultimo_error_linea = -1
    
    def construir(self, debug=False):
        """Construye el parser de PLY"""
        self.parser = yacc.yacc(
            module=self,
            debug=debug,
            write_tables=False
        )
        return self.parser
    
    def reset(self):
        """Limpia el estado del parser"""
        self.errores_sintacticos.clear()
        self.lineas_con_error.clear()
        self.ultima_linea_completa = 0
        self.ultimo_error_linea = -1
    
    def agregar_error(self, linea, mensaje):
        """Agrega un error sintáctico"""
        if linea not in self.lineas_con_error:
            self.errores_sintacticos.append({
                'tipo': 'error',
                'linea': linea,
                'mensaje': mensaje
            })
            self.lineas_con_error.add(linea)
    
    # ===================== PRECEDENCIA DE OPERADORES =====================
    
    precedence = (
        ('left', 'MAS', 'MENOS'),
        ('left', 'POR', 'DIVIDIDO'),
        ('right', 'UMINUS'),
    )
    
    # ===================== REGLAS GRAMATICALES =====================
    
    def p_programa(self, p):
        'programa : lista_sentencias'
        p[0] = p[1]
    
    def p_lista_sentencias(self, p):
        '''lista_sentencias : lista_sentencias sentencia
                            | sentencia'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]] if p[2] is not None else p[1]
        else:
            p[0] = [p[1]] if p[1] is not None else []
    
    # ===================== TIPOS =====================
    
    def p_tipo(self, p):
        '''tipo : ENTERO
                | REAL
                | TEXTO'''
        p[0] = p[1]
    
    def p_tipo_declaracion_minuscula(self, p):
        '''tipo : IDENTIFICADOR'''
        if p[1].lower() in ['texto', 'entero', 'real']:
            linea = p.lineno(1)
            self.agregar_error(linea, 
                f"¡Ombe! '{p[1]}' debe escribirse con mayúscula inicial: '{p[1].capitalize()}'")
            p[0] = None
        else:
            linea = p.lineno(1)
            self.agregar_error(linea, 
                f"¡Qué vaina! '{p[1]}' no es un tipo válido. Usa: Texto, Entero o Real")
            p[0] = None
    
    def p_tipo_captura(self, p):
        '''tipo_captura : ENTERO
                        | REAL
                        | TEXTO'''
        p[0] = p[1]
    
    def p_tipo_captura_minuscula(self, p):
        '''tipo_captura : IDENTIFICADOR'''
        if p[1].lower() in ['texto', 'entero', 'real']:
            linea = p.lineno(1)
            self.agregar_error(linea, 
                f"¡Ombe! '{p[1]}' debe escribirse con mayúscula inicial: '{p[1].capitalize()}'")
            p[0] = None
        else:
            linea = p.lineno(1)
            self.agregar_error(linea, 
                f"¡Qué vaina! 'Captura.{p[1]}()' no existe. Usa: Captura.Texto(), Captura.Entero() o Captura.Real()")
            p[0] = None
    
    # ===================== DECLARACIONES =====================
    
    def p_sentencia_declaracion(self, p):
        'sentencia : IDENTIFICADOR tipo PUNTO_Y_COMA'
        var, tipo_var = p[1], p[2]
        linea = p.lineno(1)
        
        if tipo_var is None:
            p[0] = None
            return
        
        if self.semantico.declarar_variable(var, tipo_var, linea):
            self.ultima_linea_completa = linea
            p[0] = ('declarar', var, tipo_var)
        else:
            p[0] = None
    
    def p_sentencia_declaracion_sin_punto_coma(self, p):
        'sentencia : IDENTIFICADOR tipo error'
        var, tipo_var = p[1], p[2]
        linea = p.lineno(1)
        
        if linea not in self.lineas_con_error:
            self.agregar_error(linea, 
                f"¡Ey mi llave! Te faltó el punto y coma (;) después de '{var} {tipo_var}'")
        
        p[0] = None
    
    # ===================== ASIGNACIONES =====================
    def p_sentencia_asignacion(self, p):
        'sentencia : IDENTIFICADOR IGUAL expresion PUNTO_Y_COMA'
        var, expr = p[1], p[3]
        linea = p.lineno(1)
        
        # Verificar si la expresión contiene errores sintácticos
        if isinstance(expr, tuple) and expr[0] == 'error':
            # Si hay error en la expresión, NO realizar la asignación
            # Ya se reportó el error en p_error o en las reglas de expresión
            
            # EXCEPCIÓN: Si el error es 'variable_no_definida', permitir que el semántico lo maneje
            # para dar el mensaje de "falta comillas" si es Texto.
            if len(expr) > 1 and expr[1] == 'variable_no_definida':
                pass # Continuar a semantico.asignar_variable
            else:
                p[0] = None
                return
        
        if self.semantico.asignar_variable(var, expr, linea):
            self.ultima_linea_completa = linea
            p[0] = ('asignar', var, expr)
        else:
            p[0] = None
    
    def p_sentencia_asignacion_sin_punto_coma(self, p):
        'sentencia : IDENTIFICADOR IGUAL expresion error'
        var = p[1]
        linea = p.lineno(1)
        
        if linea not in self.lineas_con_error:
            self.agregar_error(linea, 
                f"¡Ey mi llave! Te faltó el punto y coma (;) después de '{var} = ...'")
        
        p[0] = None
    
    # ===================== MENSAJE.TEXTO() =====================
    
    def p_sentencia_mensaje(self, p):
        '''sentencia : MENSAJE PUNTO TEXTO PARENTESIS_IZQ CADENA_TEXTO PARENTESIS_DER PUNTO_Y_COMA
                     | MENSAJE PUNTO TEXTO PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_Y_COMA'''
        linea = p.lineno(1)
        valor_texto = p[5]
        
        self.semantico.validar_mensaje(valor_texto, linea)
        self.ultima_linea_completa = linea
        p[0] = ('mensaje_texto', valor_texto)
    
    def p_sentencia_mensaje_vacio(self, p):
        'sentencia : MENSAJE PUNTO TEXTO PARENTESIS_IZQ PARENTESIS_DER PUNTO_Y_COMA'
        linea = p.lineno(1)
        self.agregar_error(linea, "¡Joa! Mensaje.Texto está vacío, ponle algo pues.")
        p[0] = None
    
    def p_sentencia_mensaje_metodo_invalido(self, p):
        '''sentencia : MENSAJE PUNTO IDENTIFICADOR PARENTESIS_IZQ CADENA_TEXTO PARENTESIS_DER PUNTO_Y_COMA
                     | MENSAJE PUNTO IDENTIFICADOR PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_Y_COMA
                     | MENSAJE PUNTO IDENTIFICADOR PARENTESIS_IZQ PARENTESIS_DER PUNTO_Y_COMA'''
        linea = p.lineno(1)
        metodo = p[3]
        
        if metodo.lower() == 'texto':
            self.agregar_error(linea, 
                f"¡Eche! Es 'Mensaje.Texto', con mayúscula inicial, no '{metodo}'.")
        else:
            self.agregar_error(linea, 
                f"¡Qué vaina! 'Mensaje' no tiene un método llamado '{metodo}'.")
        
        p[0] = None
    
    def p_sentencia_mensaje_sin_paren_der(self, p):
        '''sentencia : MENSAJE PUNTO TEXTO PARENTESIS_IZQ CADENA_TEXTO PUNTO_Y_COMA
                     | MENSAJE PUNTO TEXTO PARENTESIS_IZQ expresion PUNTO_Y_COMA
                     | MENSAJE PUNTO TEXTO PARENTESIS_IZQ CADENA_TEXTO error
                     | MENSAJE PUNTO TEXTO PARENTESIS_IZQ expresion error'''
        linea = p.lineno(1)
        self.agregar_error(linea, 
            "¡Ombe! Te faltó cerrar el paréntesis ')' en Mensaje.Texto()")
        p[0] = None
    
    # ===================== EXPRESIONES =====================
    
    def p_expresion_binaria(self, p):
        '''expresion : expresion MAS expresion
                     | expresion MENOS expresion
                     | expresion POR expresion
                     | expresion DIVIDIDO expresion'''
        p[0] = ('operacion_binaria', p[2], p[1], p[3])
    
    def p_expresion_grupo(self, p):
        'expresion : PARENTESIS_IZQ expresion PARENTESIS_DER'
        p[0] = p[2]
    
    def p_expresion_valor(self, p):
        '''expresion : NUMERO_ENTERO
                     | NUMERO_REAL'''
        p[0] = ('numero', p[1])
    
    def p_expresion_identificador(self, p):
        'expresion : IDENTIFICADOR'
        var = p[1]
        
        if not self.semantico.variable_existe(var):
            p[0] = ('error', 'variable_no_definida', var)
        else:
            p[0] = ('variable', var)
    
    def p_expresion_cadena(self, p):
        'expresion : CADENA_TEXTO'
        p[0] = ('cadena', p[1])
    
    def p_expresion_captura_vacia(self, p):
        'expresion : CAPTURA PUNTO tipo_captura PARENTESIS_IZQ PARENTESIS_DER'
        if p[3] is not None:
            p[0] = ('capturar', p[3])
        else:
            p[0] = ('error', 'tipo_invalido')
    
    def p_expresion_captura_con_parametro(self, p):
        'expresion : CAPTURA PUNTO tipo_captura PARENTESIS_IZQ expresion PARENTESIS_DER'
        if p[3] is not None:
            p[0] = ('capturar', p[3])
        else:
            p[0] = ('error', 'tipo_invalido')
    
    def p_expresion_unaria(self, p):
        'expresion : MENOS expresion %prec UMINUS'
        p[0] = ('operacion_binaria', '-', ('numero', 0), p[2])
    
    # ===================== ERRORES DE CAPTURA =====================
    
    def p_expresion_captura_sin_parens(self, p):
        'expresion : CAPTURA PUNTO tipo_captura'
        linea = p.lineno(1)
        if p[3] is not None:
            self.agregar_error(linea, 
                f"¡Ombe! Te faltaron los paréntesis en Captura.{p[3]}()")
        p[0] = ('error', 'falta_parens')
    
    def p_expresion_captura_paren_izq_sin_cerrar(self, p):
        'expresion : CAPTURA PUNTO tipo_captura PARENTESIS_IZQ error'
        linea = p.lineno(1)
        if p[3] is not None:
            self.agregar_error(linea, 
                f"¡Ombe! Falta cerrar el paréntesis ')' en Captura.{p[3]}()")
        p[0] = ('error', 'captura_sin_cerrar')
    
    def p_expresion_identificador_parens(self, p):
        'expresion : IDENTIFICADOR PARENTESIS_IZQ PARENTESIS_DER'
        linea = p.lineno(1)
        nombre = p[1]
        
        if nombre.startswith('Captura'):
            self.agregar_error(linea, 
                f"¡Eche! Creo que querías decir 'Captura.{nombre[7:]}()'. Te faltó el punto.")
        else:
            self.agregar_error(linea, 
                f"¡Qué vaina! '{nombre}' no es una función, no le pongas paréntesis.")
        
        p[0] = ('error', 'funcion_invalida')
    
    def p_expresion_metodo_malformado(self, p):
        '''expresion : IDENTIFICADOR PUNTO IDENTIFICADOR PARENTESIS_IZQ PARENTESIS_DER
                     | IDENTIFICADOR PUNTO IDENTIFICADOR PARENTESIS_IZQ expresion PARENTESIS_DER
                     | IDENTIFICADOR PUNTO tipo_captura PARENTESIS_IZQ PARENTESIS_DER
                     | IDENTIFICADOR PUNTO tipo_captura PARENTESIS_IZQ expresion PARENTESIS_DER'''
        linea = p.lineno(1)
        obj = p[1]
        metodo = p[3]
        
        if obj.lower() == 'captura':
            self.agregar_error(linea, 
                f"¡Ombe! 'Captura' debe escribirse con mayúscula inicial: 'Captura.{metodo}()'")
        else:
            self.agregar_error(linea, 
                f"¡Qué vaina! La variable '{obj}' no tiene métodos, no inventes.")
        
        p[0] = ('error', 'metodo_invalido')
    
    # ===================== RECUPERACIÓN DE ERRORES =====================
    
    def p_expresion_error_parens(self, p):
        'expresion : PARENTESIS_IZQ error PARENTESIS_DER'
        p[0] = ('error', 'parens_malformados')
    
    def p_expresion_paren_sin_cerrar(self, p):
        'expresion : PARENTESIS_IZQ expresion error'
        linea = p.lineno(1)
        self.agregar_error(linea, "¡Ombe! Falta cerrar el paréntesis ')' en la expresión")
        p[0] = ('error', 'paren_sin_cerrar')
    
    def p_expresion_error(self, p):
        'expresion : error'
        p[0] = ('error', 'general')
    
    def p_sentencia_vacia(self, p):
        'sentencia : PUNTO_Y_COMA'
        linea = p.lineno(1)
        
        if hasattr(self, 'ultima_linea_completa') and self.ultima_linea_completa == linea:
            self.agregar_error(linea, 
                "¡Ey! Tienes doble punto y coma (;;) en la misma línea, borra uno pues.")
        
        p[0] = None
    
    def p_sentencia_error(self, p):
        'sentencia : error PUNTO_Y_COMA'
        p[0] = None
    
    # ===================== MANEJO GLOBAL DE ERRORES =====================
    
    def p_error(self, p):
        """Manejo inteligente de errores sintácticos"""
        if p:
            linea = p.lineno
            
            # Marcar errores léxicos primero
            for error in self.lexer_obj.errores:
                if 'linea' in error and isinstance(error['linea'], int):
                    self.lineas_con_error.add(error['linea'])
            
            # Evitar duplicados de la misma línea
            if linea == self.ultimo_error_linea:
                # Ya reportamos error en esta línea, solo recuperar
                while True:
                    tok = self.parser.token()
                    if not tok or tok.type == 'PUNTO_Y_COMA':
                        break
                if tok and tok.type == 'PUNTO_Y_COMA':
                    self.parser.errok()
                    return tok
                return
            
            self.ultimo_error_linea = linea
            
            # Mensajes específicos según el token
            if p.type in ['IDENTIFICADOR', 'MENSAJE', 'CAPTURA']:
                # Dejar que las reglas con 'error' manejen la recuperación
                return p
            
            elif p.type == 'PUNTO_Y_COMA':
                # Dejar que las reglas con 'error' lo consuman
                return p
            
            elif p.type in ['PARENTESIS_DER', 'PARENTESIS_IZQ']:
                # Solo reportar si no hay error previo en esta línea
                if linea not in self.lineas_con_error:
                    self.agregar_error(linea, 
                        "¡Ombe! Falta un paréntesis o está en el lugar equivocado")
                # Recuperación: buscar punto y coma
                while True:
                    tok = self.parser.token()
                    if not tok or tok.type == 'PUNTO_Y_COMA':
                        break
                if tok and tok.type == 'PUNTO_Y_COMA':
                    self.parser.errok()
                    return tok
            
            elif p.type in ['MAS', 'MENOS', 'POR', 'DIVIDIDO']:
                # Solo reportar si no hay error previo en esta línea
                if linea not in self.lineas_con_error:
                    self.agregar_error(linea, 
                        f"¡Qué vaina! El operador '{p.value}' no está bien colocado")
                # CRÍTICO: Recuperación más agresiva para continuar
                while True:
                    tok = self.parser.token()
                    if not tok or tok.type == 'PUNTO_Y_COMA':
                        break
                if tok and tok.type == 'PUNTO_Y_COMA':
                    self.parser.errok()
                    return tok
            
            else:
                # Solo reportar si no hay error previo en esta línea
                if linea not in self.lineas_con_error:
                    self.agregar_error(linea, 
                        f"¡Qué vaina! Error de sintaxis con '{p.value}' aquí")
                # Recuperación
                while True:
                    tok = self.parser.token()
                    if not tok or tok.type == 'PUNTO_Y_COMA':
                        break
                if tok and tok.type == 'PUNTO_Y_COMA':
                    self.parser.errok()
                    return tok
        
        else:
            # EOF inesperado
            if len(self.lineas_con_error) == 0:
                self.agregar_error('?', 
                    "¡Ombe! El archivo terminó de forma inesperada, seguro te faltó un punto y coma (;) al final.")


# ===================== CLASE COMPILADOR PRINCIPAL =====================

class Compilador:
    """Compilador completo - Orquesta todas las fases"""
    
    def __init__(self):
        # Crear analizadores
        self.lexer = AnalizadorLexico()
        self.lexer.construir()
        
        self.semantico = AnalizadorSemantico()
        
        self.parser = AnalizadorSintactico(self.lexer, self.semantico)
        self.parser.construir(debug=False)
    
    def reset(self):
        """Limpia el estado de todos los analizadores"""
        self.lexer.reset()
        self.parser.reset()
        self.semantico.reset()
    
    def analizar(self, codigo):
        """Ejecuta análisis completo del código"""
        self.reset()
        
        try:
            # Parse el código
            resultado = self.parser.parser.parse(
                codigo,
                lexer=self.lexer.lexer,
                tracking=True
            )
            
            # Recolectar todos los mensajes
            mensajes = []
            mensajes.extend(self.lexer.errores)
            mensajes.extend(self.parser.errores_sintacticos)
            mensajes.extend(self.semantico.mensajes)
            
            # Ordenar por línea
            mensajes.sort(key=lambda x: x['linea'] if isinstance(x['linea'], int) else 999999)
            
            # Calcular estadísticas
            aciertos = sum(1 for m in mensajes if m['tipo'] == 'exito')
            errores = sum(1 for m in mensajes if m['tipo'] == 'error')
            
            return {
                'exito': errores == 0,
                'resultado': resultado,
                'mensajes': mensajes,
                'estadisticas': {'aciertos': aciertos, 'errores': errores}
            }
        
        except Exception as e:
            # En caso de error fatal
            mensajes = []
            mensajes.extend(self.lexer.errores)
            mensajes.extend(self.parser.errores_sintacticos)
            mensajes.extend(self.semantico.mensajes)
            
            mensajes.sort(key=lambda x: x['linea'] if isinstance(x['linea'], int) else 999999)
            
            return {
                'exito': False,
                'resultado': None,
                'mensajes': mensajes,
                'estadisticas': {
                    'aciertos': sum(1 for m in mensajes if m['tipo'] == 'exito'),
                    'errores': sum(1 for m in mensajes if m['tipo'] == 'error')
                }
            }
    
    def obtener_estadisticas(self):
        """Retorna estadísticas de compilación"""
        mensajes = []
        mensajes.extend(self.lexer.errores)
        mensajes.extend(self.parser.errores_sintacticos)
        mensajes.extend(self.semantico.mensajes)
        
        return {
            'aciertos': sum(1 for m in mensajes if m['tipo'] == 'exito'),
            'errores': sum(1 for m in mensajes if m['tipo'] == 'error')
        }
    
    @property
    def tabla_simbolos(self):
        """Acceso a la tabla de símbolos"""
        return self.semantico.tabla_simbolos
    
    @property
    def mensajes_consola(self):
        """Acceso a los mensajes consolidados"""
        mensajes = []
        mensajes.extend(self.lexer.errores)
        mensajes.extend(self.parser.errores_sintacticos)
        mensajes.extend(self.semantico.mensajes)
        mensajes.sort(key=lambda x: x['linea'] if isinstance(x['linea'], int) else 999999)
        return mensajes