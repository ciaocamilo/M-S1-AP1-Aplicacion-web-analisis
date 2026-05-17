# Punto de inicio de la aplicación
from app import app
from gui import layout
import logica

# app es el objeto principal de Dash (creado en app.py), y su propiedad .layout define qué se renderiza en el navegador
# Al asignarle layout (importado desde gui.py), le estamos diciendo a Dash: "este es el árbol de componentes que debe mostrar como página web"
app.layout = layout

if __name__ == '__main__':
    app.run(debug=True)

