from time import time

from estimator import estimator

start_time = time()
url = "https://www.foodfanatic.dk/tacos-med-lynchili-og-salsa"
print(estimator(url, verbose=True))
end_time = time()

print(f"Time elapsed: {end_time - start_time}s")
