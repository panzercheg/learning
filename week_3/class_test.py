class Planet:
    pass

solar_system = []

planet_names =[
    "Mercury", "Venus", "Earth", "Mars",
    "Jupiter", "Saturn"
]
for i in range(8):
    planet = Planet()
    solar_system.append(planet)

print(solar_system)