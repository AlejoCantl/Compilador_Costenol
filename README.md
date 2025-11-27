# Compilador Costeñol 🏖️

Un compilador educativo con sintaxis inspirada en el dialecto costeño colombiano, desarrollado con Python y PLY (Python Lex-Yacc). Este proyecto implementa un lenguaje de programación con mensajes de error y éxito en lenguaje coloquial costeño.

## 📋 Descripción General

**Costeñol** es un lenguaje de programación didáctico que utiliza palabras clave en español con sintaxis inspirada en lenguajes modernos. El compilador incluye:

- **Análisis léxico** (tokenización)
- **Análisis sintáctico** (parsing)
- **Análisis semántico** (validación de tipos)
- **Tabla de símbolos** para gestión de variables
- **Interfaz gráfica** con Tkinter para facilitar el uso

## ✨ Características Principales

### Tipos de Datos
- `Entero`: Números enteros
- `Real`: Números decimales (acepta tanto punto `.` como coma `,`)
- `Texto`: Cadenas de texto entre comillas dobles

### Operaciones Soportadas
- **Aritméticas**: `+`, `-`, `*`, `/`
- **Asignación**: `=`
- **Entrada/Salida**: 
  - `Captura.Entero()`, `Captura.Real()`, `Captura.Texto()`
  - `Mensaje.Texto()`

### Validaciones
- Declaración obligatoria de variables antes de su uso
- Verificación de tipos en asignaciones
- Detección de variables no inicializadas
- Mensajes de error contextuales y amigables en lenguaje costeño

## 🚀 Instalación

### Requisitos Previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el repositorio**
   ```bash
   cd "Compilador"
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   ```

3. **Activar el entorno virtual**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Uso

### Ejecutar la Interfaz Gráfica

```bash
python main.py
```

Esto abrirá la interfaz gráfica del compilador donde podrás:
- Escribir código en el editor
- Compilar y ver resultados en tiempo real
- Visualizar errores y aciertos con estadísticas

### Ejemplo de Código

```javascript
// Declaración de variables
nombre Texto;
edad Entero;
altura Real;

// Asignación de valores
nombre = "Carlos";
edad = 25;
altura = 1,75;  // También funciona con 1.75

// Operaciones aritméticas
resultado Real;
resultado = edad * altura;

// Mostrar mensajes
Mensaje.Texto("Hola mundo");
Mensaje.Texto(nombre);
Mensaje.Texto(resultado);

// Captura de datos del usuario
entrada Entero;
entrada = Captura.Entero();
```

## 📁 Estructura del Proyecto

```
Compilador_Costenol/
│
├── main.py           # Punto de entrada de la aplicación
├── gui.py            # Interfaz gráfica con Tkinter
├── lexer.py          # Analizador léxico
├── parser.py         # Analizador sintáctico
├── semantic.py       # Analizador semántico
├── requirements.txt  # Dependencias del proyecto
└── README.md         # Este archivo
```

### Descripción de Archivos

- **`main.py`**: Inicializa la aplicación y crea la ventana principal
- **`gui.py`**: Implementa la interfaz gráfica con editor de código, consola de resultados y estadísticas
- **`lexer.py`**: Define los tokens y reglas léxicas del lenguaje
- **`parser.py`**: Implementa la gramática, reglas sintácticas
- **`semantic.py`**: Implementa la validación semántica del código y la tabla de símbolos
- **`requirements.txt`**: Dependencias del proyecto

## 🎨 Características de la Interfaz

### Editor de Código
- Resaltado de sintaxis
- Área de texto con scroll
- Ejemplos de sintaxis integrados
- Botón de compilación destacado

### Consola de Resultados
- Mensajes de éxito en verde (✅)
- Mensajes de error en rojo (❌)
- Indicación de número de línea para cada mensaje
- Resumen final de compilación

### Estadísticas
- Contador de aciertos
- Contador de errores

## 🔧 Mensajes del Compilador

El compilador utiliza expresiones coloquiales costeñas para hacer la experiencia más amigable:

### Ejemplos de Mensajes de Éxito
- `¡Bien ahí! Variable 'nombre' quedó como Texto`
- `¡Tá bueno! Texto → nombre(Texto)`
- `Nojoda mostro está bueno el valor es "Carlos"`

### Ejemplos de Mensajes de Error
- `¡Ombe! La variable 'x' no existe, declárala primero apue.`
- `¡Eche! Es 'Mensaje.Texto', con mayúscula inicial, no 'texto'.`
- `¡Ey mi llave! Te faltó el punto y coma (;) después de...`
- `¡Esa vaina que cole! No puedes meter Real en 'edad' que es Entero`

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**: Lenguaje de programación principal
- **PLY (Python Lex-Yacc) 3.11**: Herramienta para análisis léxico y sintáctico
- **Tkinter**: Biblioteca para la interfaz gráfica

## 📚 Conceptos de Compiladores Implementados

1. **Análisis Léxico**: Tokenización del código fuente
2. **Análisis Sintáctico**: Verificación de la estructura gramatical
3. **Análisis Semántico**: Validación de tipos y contexto
4. **Tabla de Símbolos**: Gestión de variables y sus atributos
5. **Manejo de Errores**: Recuperación de errores y mensajes descriptivos
6. **Gramática LL**: Implementación con PLY (similar a YACC)

## 🎯 Objetivos Educativos

Este compilador fue diseñado con fines educativos para:
- Aprender los fundamentos de compiladores
- Entender el proceso de análisis léxico, sintáctico y semántico
- Practicar el diseño de lenguajes de programación
- Implementar validación de tipos
- Crear mensajes de error útiles y contextuales

## 🐛 Manejo de Errores

El compilador detecta y reporta múltiples tipos de errores:

- **Errores Léxicos**: Caracteres ilegales, variables que empiezan con números
- **Errores Sintácticos**: Falta de punto y coma, paréntesis sin cerrar, sintaxis incorrecta
- **Errores Semánticos**: Tipos incompatibles, variables no declaradas, variables sin inicializar
- **Errores de Mayúsculas**: Palabras clave escritas incorrectamente

## 📝 Notas Importantes

- Las palabras clave deben escribirse con **mayúscula inicial**: `Texto`, `Entero`, `Real`, `Captura`, `Mensaje`
- Todas las sentencias deben terminar con **punto y coma** (`;`)
- Las cadenas de texto deben estar entre **comillas dobles** (`"`)
- Los números reales aceptan tanto **punto** (`.`) como **coma** (`,`) como separador decimal
- Los comentarios se escriben con `//` para una línea o `/* */` para múltiples líneas

## 🤝 Contribuciones

Este es un proyecto educativo. Si encuentras errores o tienes sugerencias de mejora, siéntete libre de:
- Reportar issues
- Proponer mejoras
- Compartir feedback

## 📄 Licencia

Proyecto educativo de código abierto.

---

**¡Dale pues, a programar en Costeñol! 🏖️🚀**
