class AnalizadorSemantico:
    """Analizador semántico - Gestión de tabla de símbolos y tipos"""
    
    def __init__(self):
        self.tabla_simbolos = {}
        self.mensajes = []
        self.lineas_procesadas = set()
    
    def reset(self):
        """Limpia el estado del analizador"""
        self.tabla_simbolos.clear()
        self.mensajes.clear()
        self.lineas_procesadas.clear()
    
    # ==================== GESTIÓN DE VARIABLES ====================
    
    def declarar_variable(self, nombre, tipo, linea):
        """Declara una variable en la tabla de símbolos"""
        if nombre in self.tabla_simbolos:
            self.agregar_mensaje('error', linea, 
                f"¡Epa! La variable '{nombre}' ya la declaraste mano, no la repitas.")
            return False
        
        self.tabla_simbolos[nombre] = {
            'tipo': tipo,
            'valor': None,
            'linea': linea
        }
        
        self.agregar_mensaje('exito', linea, 
            f"¡Bien ahí! Variable '{nombre}' quedó como {tipo}")
        return True
    
    def asignar_variable(self, nombre, expresion, linea):
        """Asigna un valor a una variable existente"""
        if nombre not in self.tabla_simbolos:
            self.agregar_mensaje('error', linea, 
                f"¡Ombe hey! La variable '{nombre}' no existe, declárala primero apue.")
            return False
        
        tipo_declarado = self.tabla_simbolos[nombre]['tipo']
        
        # PRIMERO: Verificar si hay errores sintácticos en la expresión
        if isinstance(expresion, tuple) and expresion[0] == 'error':
            # Hay un error sintáctico - NO asignar
            if expresion[1] == 'variable_no_definida':
                var_error = expresion[2]
                if tipo_declarado == 'Texto':
                    self.agregar_mensaje('error', linea, 
                        f"¡Eche! Si '{var_error}' es texto, ponle comillas ombe: \"{var_error}\"")
                else:
                    self.agregar_mensaje('error', linea, 
                        f"¡Ombe! La variable '{var_error}' no existe, no inventes.")
            elif expresion[1] not in ['tipo_invalido', 'falta_parens', 'captura_sin_cerrar', 
                                       'funcion_invalida', 'metodo_invalido', 'parens_malformados', 
                                       'paren_sin_cerrar']:
                # Para errores generales que aún no se reportaron
                pass
            # Para otros tipos de errores, el parser ya los reportó
            return False
        
        tipo_expresion = self.obtener_tipo_expresion(expresion)
        
        # Validar tipo de Captura
        if isinstance(expresion, tuple) and expresion[0] == 'capturar':
            tipo_captura = expresion[1]
            if tipo_declarado != tipo_captura:
                self.agregar_mensaje('error', linea,
                    f"¡Ey vale! No puedes usar Captura.{tipo_captura}() para '{nombre}' que es {tipo_declarado}")
                return False
            else:
                self.tabla_simbolos[nombre]['valor'] = expresion
                self.agregar_mensaje('exito', linea, 
                    f"¡Tá bueno! Captura.{tipo_captura}() → {nombre}({tipo_declarado})")
                return True
        
        # Validar mensajes de error de tipos
        if str(tipo_expresion).startswith('!Eche tú que!') or \
           str(tipo_expresion).startswith('¡Ombe!') or \
           str(tipo_expresion).startswith('¡Nojoda que!'):
            self.agregar_mensaje('error', linea, tipo_expresion)
            return False
        
        # Si el tipo es 'Error' (propagado de sintaxis), no hacer nada más
        if tipo_expresion == 'Error':
            return False
        
        # Validar compatibilidad de tipos
        if not self.tipos_compatibles(tipo_declarado, tipo_expresion):
            self.agregar_mensaje('error', linea,
                f"¡Esa vaina que cole! No puedes meter {tipo_expresion} en '{nombre}' que es {tipo_declarado}")
            return False
        
        # Asignación exitosa
        self.tabla_simbolos[nombre]['valor'] = expresion
        self.agregar_mensaje('exito', linea, 
            f"¡Tá bueno! {tipo_expresion} → {nombre}({tipo_declarado})")
        return True
    
    def variable_existe(self, nombre):
        """Verifica si una variable existe"""
        return nombre in self.tabla_simbolos
    def variable_tiene_valor(self, nombre):
        """Verifica si una variable tiene valor asignado"""
        if nombre not in self.tabla_simbolos:
            return False
        return self.tabla_simbolos[nombre]['valor'] is not None
    
    # ==================== VALIDACIÓN DE TIPOS ====================
    
    def obtener_tipo_expresion(self, expresion):
        """Determina el tipo de una expresión"""
        if not isinstance(expresion, tuple):
            return 'Desconocido'
        
        if expresion[0] == 'error':
            return 'Error'
        
        if expresion[0] == 'numero':
            valor = expresion[1]
            return 'Entero' if isinstance(valor, int) else 'Real'
        
        elif expresion[0] == 'cadena':
            return 'Texto'
        
        elif expresion[0] == 'variable':
            variable = expresion[1]
            if not self.variable_existe(variable):
                return 'Desconocido'
            
            if not self.variable_tiene_valor(variable):
                return f'!Eche tú que! La variable "{variable}" no tiene valor todavía, ponle algo primero eche nojoda care mondá'
            
            return self.tabla_simbolos[variable]['tipo']
        
        elif expresion[0] == 'capturar':
            return expresion[1]
        
        elif expresion[0] == 'operacion_binaria':
            op, izq, der = expresion[1], expresion[2], expresion[3]
            
            # Verificar si hay errores en los operandos PRIMERO
            if isinstance(izq, tuple) and izq[0] == 'error':
                return 'Error'
            if isinstance(der, tuple) and der[0] == 'error':
                return 'Error'
            
            tipo_izq = self.obtener_tipo_expresion(izq)
            tipo_der = self.obtener_tipo_expresion(der)
            
            # Propagar errores
            if tipo_izq == 'Error' or tipo_der == 'Error':
                return 'Error'
            
            if 'Error:' in str(tipo_izq) or 'Error:' in str(tipo_der):
                return tipo_izq if 'Error:' in str(tipo_izq) else tipo_der
            
            # Operador suma (especial para texto)
            if op == '+':
                if tipo_izq == 'Texto' or tipo_der == 'Texto':
                    if tipo_izq == 'Texto' and tipo_der == 'Texto':
                        return 'Texto'
                    else:
                        return f'¡Nojoda que! no puedes sumar Texto con {tipo_izq if tipo_izq != "Texto" else tipo_der}'
                else:
                    if tipo_izq == 'Entero' and tipo_der == 'Entero':
                        return 'Entero'
                    else:
                        return 'Real'
            
            # Otros operadores (solo numéricos)
            else:
                if tipo_izq not in ['Entero', 'Real'] or tipo_der not in ['Entero', 'Real']:
                    return f'¡Ombe! La operación "{op}" solo funciona con números, no con {tipo_izq} y {tipo_der} eche'
                
                if tipo_izq == 'Entero' and tipo_der == 'Entero':
                    return 'Entero'
                else:
                    return 'Real'
        
        return 'Desconocido'
    
    def tipos_compatibles(self, tipo_declarado, tipo_expresion):
        """Verifica si dos tipos son compatibles"""
        if 'Error:' in str(tipo_expresion):
            return False
        
        compatibilidad = {
            'Entero': ['Entero'],
            'Real': ['Entero', 'Real'],
            'Texto': ['Texto']
        }
        
        return tipo_expresion in compatibilidad.get(tipo_declarado, [])
    
    # ==================== EVALUACIÓN DE EXPRESIONES ====================
    
    def obtener_valor_expresion(self, expresion, visitados=None):
        """Obtiene el valor real de una expresión para mostrar"""
        if visitados is None:
            visitados = set()
        
        if not isinstance(expresion, tuple):
            return str(expresion)
        
        if expresion[0] == 'error':
            return None
        
        if expresion[0] == 'numero':
            valor = expresion[1]
            if isinstance(valor, float) and valor == int(valor):
                return str(int(valor))
            return str(valor)
        
        elif expresion[0] == 'cadena':
            return expresion[1]
        
        elif expresion[0] == 'variable':
            variable = expresion[1]
            
            if variable in visitados:
                return f"[{variable}]"
            
            if self.variable_tiene_valor(variable):
                valor_almacenado = self.tabla_simbolos[variable]['valor']
                visitados.add(variable)
                return self.obtener_valor_expresion(valor_almacenado, visitados)
            
            return f"[{variable}]"
        
        elif expresion[0] == 'capturar':
            tipo_captura = expresion[1]
            return f"[Captura.{tipo_captura}()]"
        
        elif expresion[0] == 'operacion_binaria':
            resultado = self.evaluar_operacion(expresion, visitados)
            if resultado is not None:
                if isinstance(resultado, float) and resultado == int(resultado):
                    return str(int(resultado))
                return str(resultado)
            return "[operación no evaluable]"
        
        return str(expresion)
    
    def evaluar_operacion(self, expresion, visitados=None):
        """Evalúa una operación binaria y retorna el resultado numérico"""
        if visitados is None:
            visitados = set()
        
        if not isinstance(expresion, tuple):
            return None
        
        if expresion[0] == 'operacion_binaria':
            op, izq, der = expresion[1], expresion[2], expresion[3]
            
            val_izq = self.evaluar_operacion(izq, visitados)
            val_der = self.evaluar_operacion(der, visitados)
            
            if val_izq is None or val_der is None:
                return None
            
            try:
                if op == '+':
                    return val_izq + val_der
                elif op == '-':
                    return val_izq - val_der
                elif op == '*':
                    return val_izq * val_der
                elif op == '/':
                    if val_der == 0:
                        return None
                    return val_izq / val_der
            except:
                return None
        
        elif expresion[0] == 'numero':
            return expresion[1]
        
        elif expresion[0] == 'variable':
            var = expresion[1]
            
            if var in visitados:
                return None
            
            if self.variable_tiene_valor(var):
                visitados.add(var)
                return self.evaluar_operacion(self.tabla_simbolos[var]['valor'], visitados)
            
            return None
        
        return None
    
    # ==================== GESTIÓN DE MENSAJES ====================
    
    def agregar_mensaje(self, tipo, linea, mensaje):
        """Agrega un mensaje evitando duplicados por línea"""
        # Evitar duplicados en la misma línea
        clave = (tipo, linea, mensaje)
        
        # Verificar si ya existe este mensaje exacto
        if any(m['tipo'] == tipo and m['linea'] == linea and m['mensaje'] == mensaje 
               for m in self.mensajes):
            return
        
        self.mensajes.append({
            'tipo': tipo,
            'linea': linea,
            'mensaje': mensaje
        })
    
    def validar_mensaje(self, expresion, linea):
        """Valida la expresión de un Mensaje.Texto()"""
        if isinstance(expresion, tuple) and expresion[0] == 'error':
            if len(expresion) > 1:
                var_nombre = expresion[1]
                if var_nombre == 'variable_no_definida':
                    var_nombre = expresion[2]
                    self.agregar_mensaje('error', linea, 
                        f"¡Ombe! La variable '{var_nombre}' no existe, no puedo mostrar un fantasma.")
            # Para otros errores, ya fueron reportados por el parser
            return None
        
        if isinstance(expresion, tuple) and expresion[0] == 'capturar':
            tipo_captura = expresion[1]
            self.agregar_mensaje('error', linea, 
                f"¡Ombe! No puedes usar Captura.{tipo_captura}() dentro de Mensaje.Texto()")
            return None
        
        if isinstance(expresion, tuple) and expresion[0] == 'variable':
            var_nombre = expresion[1]
            if not self.variable_existe(var_nombre):
                self.agregar_mensaje('error', linea, 
                    f"¡Ombe! La variable '{var_nombre}' no existe, no puedo mostrar un fantasma.")
                return None
            elif not self.variable_tiene_valor(var_nombre):
                self.agregar_mensaje('error', linea, 
                    f"¡Ombe! La variable '{var_nombre}' no tiene valor, asígnale algo primero.")
                return None
        
        if isinstance(expresion, tuple) and expresion[0] == 'operacion_binaria':
            tipo_expresion = self.obtener_tipo_expresion(expresion)
            # Si el tipo es Error (por operadores mal colocados), no mostrar mensaje
            if tipo_expresion == 'Error':
                return None
            if 'Error:' in str(tipo_expresion) or str(tipo_expresion).startswith('¡'):
                self.agregar_mensaje('error', linea, tipo_expresion)
                return None
        
        valor = self.obtener_valor_expresion(expresion)
        if valor is not None:
            self.agregar_mensaje('exito', linea, 
                f"Nojoda mostro está bueno el valor es \"{valor}\"")
            return valor
        
        return None