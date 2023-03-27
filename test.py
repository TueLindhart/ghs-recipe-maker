from langchain.utilities import GoogleSearchAPIWrapper

search = GoogleSearchAPIWrapper(k=5, search_engine="google")

ingredient = "Bacon"

# print(search.run(f"{ingredient} carbon footprint in kg CO2e per kg"))
print(search.run(f"Average {ingredient} carbon footprint in kg CO₂e/kg, kg CO2e/kg"))
