import matplotlib.pyplot as plt

try:
    radius = float(input("Ingrese el radio del círculo: "))
except ValueError:
    print("Por favor ingrese un número válido.")
    exit(1)

fig, ax = plt.subplots()

circle = plt.Circle((0, 0), radius, fill=False)
ax.add_patch(circle)

# Ajuste de la escala para que el círculo no se deforme
ax.set_aspect('equal', adjustable='box')

# Límites para que el círculo aparezca centrado y completo
padding = radius * 0.1 + 1
ax.set_xlim(-radius - padding, radius + padding)
ax.set_ylim(-radius - padding, radius + padding)

ax.set_title(f"Círculo con radio {radius}")

plt.show()
