import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import re

ruta_archivo_actual = ""
cambios_realizados = False



def cargar_archivo():
    global ruta_archivo_actual, cambios_realizados
    if cambios_realizados:
        respuesta = messagebox.askyesno("Guardar cambios", "Desea guardar el archivo S/N")
        if respuesta == tk.YES:
            guardar_archivo()
    ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.vb")])
    if ruta_archivo:
        with open(ruta_archivo, "r") as archivo:
            contenido = archivo.read()
            cuadro_codigo.delete("1.0", tk.END)
            cuadro_codigo.insert(tk.END, contenido)
            ruta_archivo_actual = ruta_archivo
            cambios_realizados = False

def obtener_tokens():
    contenido_codigo = cuadro_codigo.get("1.0", tk.END)
    cuadro_resultados.delete("1.0", tk.END)
    cuadro_errores.delete("1.0", tk.END)

    lineas = contenido_codigo.splitlines()
    tokens = []

    for linea in lineas:
        # Utilizar una expresión regular para encontrar cadenas de texto entre comillas dobles
        cadenas = re.findall(r'"[^"]*"', linea)
        if cadenas:
            for cadena in cadenas:
                tokens.append(f"[CADENA: {cadena}]")
        else:
            palabras = linea.split()
            tokens_linea = ""

            for i, palabra in enumerate(palabras):
                if i > 0:
                    tokens_linea += ", "
                tokens_linea += palabra

            tokens.append(tokens_linea)

    for token_linea in tokens:
        cuadro_resultados.insert(tk.END, token_linea + "\n")



def clasificar_palabra(palabra, linea_numero):
    palabra_minuscula = palabra.lower()

    if palabra_minuscula in ["andalso", "orelse", "and", "or", "not"]:
        return f"[OL:{palabra}]"
    elif palabra in ["<", "<=", "==", "!=", ">=", ">", "+", "-", "*", "/", "="]:
        return f"[Op:{palabra}]"
    elif re.match(r'^"([^"]*)"$', palabra):
        return f"[CAD: {palabra}]"
    elif palabra_minuscula in [ "AddHandler", "AddressOf", "Alias",  "As", "Boolean", "ByRef", "Byte",
            "ByVal", "Call", "Case", "Catch", "CBool", "CByte", "CChar", "CDate", "CDbl", "CDec",
            "Char", "CInt", "Class", "CLng", "CObj", "Const", "Continue", "CSByte", "CShort",
            "CSng", "CStr", "CType", "CUInt", "CULng", "CUShort", "Date", "Decimal", "Declare",
            "Default", "Delegate", "Dim", "DirectCast", "Do", "Double", "Each",
            "End", "Enum", "Erase", "Error", "Event", "Exit", "False", "Finally", "For",
            "Friend", "Function", "Get", "GetType", "GoSub", "GoTo", "Handles", "Implements",
            "Imports", "In", "Inherits", "Integer", "Interface",  "Let", "Lib",
            "Long", "Loop", "Me", "Mod", "Module", "MustInherit", "MustOverride", "MyBase", "MyClass",
            "Namespace", "Narrowing", "New", "Next", "Nothing", "NotInheritable", "NotOverridable",
            "Object", "Of", "On", "Operator", "Option", "Optional", "Overloads", "Overridable",
            "Overrides", "ParamArray", "Partial", "Private", "Property", "Protected", "Public", "RaiseEvent",
            "ReadOnly", "ReDim", "REM", "RemoveHandler", "Resume", "Return", "SByte", "Select", "Set",
            "Shadows", "Shared", "Short", "Single", "Static", "Step", "Stop", "String", "Structure",
            "Sub", "SyncLock", "Throw", "To", "True", "Try", "TryCast", "TypeOf", "UInteger",
            "ULong", "UShort", "Using", "Variant", "Wend", "When", "While", "Widening", "With", "WithEvents",
            "WriteOnly"]:
        
        return f"[PR:{palabra}]"
    elif re.match(r'^[0-9\+\-E\.]+$', palabra): #expresion proporcionada
        errores = validar_automata(palabra, linea_numero)
        if errores:
            cuadro_errores.insert(tk.END, "\n".join(errores) + "\n")
        return f"[NUM:{palabra}]"
    else:
        return f"[ID:{palabra}]"

def validar_automata(token, linea):
        estado = 1 
        for char in token:
            if estado == 1:
                if '0' <= char <= '9' or char in ['+', '-']:
                    estado = 2
                else:
                    return [f"Error {linea}: Token'{token}'"]
                
            elif estado == 2:
                if '0' <= char <= '9':
                    estado = 2
                elif char == '.':
                    estado = 3
                elif char.lower() == 'e':
                    estado = 5
                else:
                    return [f"Error {linea}: Token'{token}'"]
                
            elif estado == 3:
                if '0' <= char <= '9':
                    estado = 4
                else:
                    return [f"Error {linea}: Token'{token}'"]
                
            elif estado == 4:
                if '0' <= char <= '9':
                    estado = 4
                elif char.lower() == 'e':
                    estado = 5
                else:
                    return [f"Error {linea}: Token'{token}'"]
                
            elif estado == 5:
                if '0' <= char <= '9':
                    estado = 7
                elif char in ['+', '-']:
                    estado = 6
                else:
                    return [f"Error {linea}: Token'{token}'"]
                
            elif estado == 6:
                if '0' <= char <= '9':
                    estado = 7
                else:
                    return [f"Error {linea}: Token'{token}'"]
                
            elif estado == 7:
                if '0' <= char <= '9':
                    estado = 7
                else:
                    return [f"Error {linea}: Token'{token}"]
                
        if estado not in (2, 4, 7):
            return [f"Error {linea}: Token'{token}'"]

        return[]

def clasificar():
    contenido_codigo = cuadro_codigo.get("1.0", tk.END)
    cuadro_resultados.delete("1.0", tk.END)
    cuadro_errores.delete("1.0", tk.END)

    lineas = contenido_codigo.splitlines()
    tokens = []

    contenido_linea = ""

    for linea_numero, linea in enumerate(lineas, start=1):
        palabras = re.findall(r'\b(?:\w+\.)?\w+\b|[.,<>=!+\-*/]', linea)
        tokens_linea = []

        for palabra in palabras:
            tokens_linea.append(clasificar_palabra(palabra, linea_numero))

        contenido_linea += ", ".join(tokens_linea) + "\n"

    cuadro_resultados.insert(tk.END, contenido_linea)

def guardar_archivo():
    global ruta_archivo_actual
    if ruta_archivo_actual:
        contenido_codigo = cuadro_codigo.get("1.0", tk.END)
        with open(ruta_archivo_actual, "w") as archivo:
            archivo.write(contenido_codigo)

def guardar_como():
    global ruta_archivo_actual
    ruta_archivo = filedialog.asksaveasfilename(filetypes=[("Archivos de texto", "*.vb")])
    if ruta_archivo:
        contenido_codigo = cuadro_codigo.get("1.0", tk.END)
        with open(ruta_archivo, "w") as archivo:
            archivo.write(contenido_codigo)
            ruta_archivo_actual = ruta_archivo

def cerrar():
    global cambios_realizados
    contenido_izquierda = cuadro_codigo.get("1.0", tk.END)
    if cambios_realizados or contenido_izquierda.strip() != ruta_archivo_actual.strip():
        respuesta = messagebox.askyesno("Guardar cambios", "Desea guardar el archivo S/N")
        if respuesta == tk.YES:
            guardar_archivo()
    ventana.quit()

ventana = tk.Tk()
ventana.title("LECTOR TEXTO VISUAL BASIC")

frame = ttk.Frame(ventana)
frame.pack(fill=tk.BOTH, expand=True)

# Cuadro de texto para mostrar el código
cuadro_codigo = tk.Text(frame, wrap=tk.NONE, font=("Arial", 12))
cuadro_codigo.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
cuadro_codigo.config(height=20, width=60)

# Cuadro de texto para mostrar los resultados (tokens)
cuadro_resultados = tk.Text(frame, wrap=tk.NONE, font=("Arial", 12))
cuadro_resultados.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
cuadro_resultados.config(height=20, width=60)

# Cuadro de texto para mostrar los errores
cuadro_errores = tk.Text(ventana, wrap=tk.NONE, font=("Arial", 12))
cuadro_errores.pack(side=tk.BOTTOM, padx=10, pady=10, fill=tk.BOTH, expand=True)
cuadro_errores.config(height=5, width=60)

# Resto del código

# Configuración de la barra de menú
ventana.protocol("WM_DELETE_WINDOW", cerrar)

barra_menu = tk.Menu(ventana)
ventana.config(menu=barra_menu)

archivo_menu = tk.Menu(barra_menu, tearoff=0)
barra_menu.add_cascade(label="Archivo", menu=archivo_menu)
archivo_menu.add_command(label="Abrir", command=cargar_archivo)
archivo_menu.add_command(label="Guardar", command=guardar_archivo)
archivo_menu.add_command(label="Guardar como", command=guardar_como)
archivo_menu.add_separator()
archivo_menu.add_command(label="Cerrar", command=cerrar)

tokens_menu = tk.Menu(barra_menu, tearoff=0)
barra_menu.add_cascade(label="Tokens", menu=tokens_menu)
tokens_menu.add_command(label="Obtener", command=obtener_tokens)
tokens_menu.add_command(label="Clasificar", command=clasificar)

ventana.mainloop()
