# Declaración de variables
numero = 10
texto = "Hola, mundo"
lista = [1, 2, 3, 4, 5]
myName = input("")

def suma(a, b):
    """Función que suma dos números"""
    return a + b

def saludar(nombre):
    """Función que saluda a una persona"""
    print(f"Hola, {nombre}!")

# Uso de las funciones
resultado = suma(5, 7)
print("La suma es:", str(resultado) + " " + myName)


saludar("Juan")