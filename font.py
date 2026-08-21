import tkinter as tk
from tkinter import font

def changeFont(dummy):
    #print(fd3[listbox.curselection()[0]])
    #fuente_seleccionada = fuente_var.get()
    etiqueta.config(font=(fd3[listbox.curselection()[0]], 12))  # Cambia el tamaño según tus necesidades

root = tk.Tk()
root.title("Selector de Fuente")

#fuentes_disponibles = font.families()
fd3=sorted(list(font.families()))
#print(fd3)


# Crear el Listbox
listbox = tk.Listbox(
    root,
    selectmode=tk.BROWSE,
    height=6
    )
listbox.insert(0, *fd3)
listbox.bind('<<ListboxSelect>>', changeFont)

listbox.pack()

# Etiqueta de ejemplo con la fuente seleccionada
etiqueta = tk.Label(root, text="Texto de ejemplo")
etiqueta.pack()

# Botón para aplicar cambios
boton_aplicar = tk.Button(root, text="Aplicar", command=changeFont)
boton_aplicar.pack()

root.mainloop()
