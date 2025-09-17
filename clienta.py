class Clienta:
    def __init__(self, nombre, apellido, email, telefono):
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.telefono = telefono

    def mostrar_datos(self):
        return f"{self.nombre} {self.apellido} - Email: {self.email} - Tel: {self.telefono}"
