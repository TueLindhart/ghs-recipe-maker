EN_CO2_SQL_PROMPT_WITH_EXAMPLES = """Given a list of ingredients,
            extract the main ingredients from the list and create a syntactically correct {dialect} query to run,
            then look at the results of the query and return the answer.

Solve the task using the following steps:
- Query all ingredients in a single query.
  Example query: 'SELECT Name, Total_kg_CO2_eq_kg FROM dk_co2_emission
  WHERE Name LIKE '%tomato%' OR NAME LIKE '%bouillon%'
- In the query, remove all non-ingredient words.
  Example of removing: '%chopped tomatoes%' to '%tomato%' or '%minced beef%' to '%beef%'
- Match the SQLResult to the list of ingredients based on preparation and type.
  Example match: '1 can of chopped tomatoes' best matches results from 'Tomato, peeled, canned'.
- Return the Answer in the following format: ''ingredient': X kg CO2e / kg'.
  Example Answer: 'Chopped tomatoes: X kg CO2e/ kg \n'.
- If the ingredient is not found in the database, return '?'.
  Example Answer: 'Chopped tomatoes: ? \n'

Use the following format:
Ingredients: "Ingredients here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:
{table_info}

Begin!

Ingredients:
150 g red lentils
1 can of chopped tomatoes
2 cubes of vegetable bouillon
1 tin of tomato concentrate (140 g)
1 tbsp. lemon juice
1. tbsp. chili powder
1 starfruit

SQLQuery: SELECT Name, Total_kg_CO2_eq_kg FROM dk_co2_emission WHERE
          Name LIKE '%tomato%' OR
          Name LIKE '%lentil%' OR
          Name LIKE '%bouillon%' OR
          Name LIKE '%juice%' OR
          Name LIKE '%lemon%' OR
          Name LIKE '%chili%' OR
          Name LIKE '%starfruit%'

SQLResult: [('Tomato, ripe, raw, origin unknown', 0.7), ('Green lentils, dried', 1.78)
            ('Tomatojuice, canned', 1.26), ('Tomato, peeled, canned', 1.26)
            ('Tomato paste, concentrated', 2.48), ('Red lentils, dried', 1.78
            ('Ice, popsickle, lemonade', 1.15), ('Lemon, raw', 0.94
            ('Apple juice', 1.64),('Bouillon, chicken, prepared', 0.38)
            ('Bouillon, beef, prepared', 0.52), ('Pepper, hot chili, raw', 1.02)
            ('Pepper, hot chili, canned', 1.54),
            ]

Answer:
Red lentils: 1.78 kg CO2e / kg
Chopped tomatoes: 1.26 kg CO2e / kg
Vegetable bouillon: 0.38 kg CO2e / kg (closest was chicken bouillon)
Tomato concentrate (140 g): 2.48 kg CO2e / kg (closest was tomato paste)
Lemon juice: 0.94 kg CO2e / kg (Closest was Lemon, raw)
Starfruit: ? (Not found in database)

Ingredients: {input}"""

DK_CO2_SQL_PROMPT_WITH_EXAMPLES = """
Given a list of ingredients in Danish, extract the main ingredients from the list
and create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.

Solve the task using the following steps:
- Query all ingredients in a single query.
  Example query: 'SELECT Navn, Total_kg_CO2_eq_kg FROM dk_co2_emission
  WHERE Navn LIKE '%tomato%' OR Navn LIKE '%bouillion%'
- In the query, remove all non-ingredient words.
  Example of removing: '%hakkede tomater%' to '%tomat%' or '%hakket oksekød%' to '%oksekød%'
- Match the SQLResult to the list of ingredients based on preparation and type.
  Example match: '1 dåse hakkede tomater' best matches results from 'Tomat, flået, konserves'.
- Return the Answer in the following format: ''ingredient': X kg CO2e / kg'.
  Example Answer: 'Hakkede tomater: X kg CO2e/ kg \n'.
- If the ingredient is not found in the database, return '?'.
  Example Answer: 'Chopped tomatoes: ? \n'

Use the following format:
Ingredients: "Ingredients here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:
{table_info}

Begin!

Ingredients:
150 g røde linser
1 dåse hakkede tomater
2 terninger grøntsagsbouillon
1 dåse tomatkoncentrat (140 g)
1 spsk. citronsaft
1. spsk. chilipulver
10 majstortillas
1 stjernefrugt

SQLQuery: SELECT Navn, Total_kg_CO2_eq_kg FROM dk_co2_emission WHERE
          Navn LIKE '%tomat%' OR
          Navn LIKE '%linse%' OR
          Navn LIKE '%bouillon%' OR
          Navn LIKE '%saft%' OR
          Navn LIKE '%citron%' OR
          Navn LIKE '%chili%' OR
          Navn LIKE '%tortilla%' OR
          Navn LIKE '%stjernefrugt%'

SQLResult: [('Tomat, uspec., rå', 0.7), ('Grønne linser, tørrede', 1.78)
            ('Tomatjuice, konserves', 1.26), ('Tomat, flået, konserves', 1.26)
            ('Tomatpure, koncentreret', 2.48), ('Røde linser, tørrede', 1.78
            ('Ispind, limonade', 1.15), ('Citron, rå', 0.94
            ('Æblejuice', 1.64),('Bouillon, hønsekød, spiseklar', 0.38)
            ('Bouillon, oksekød, spiseklar', 0.52), ('Peber, chili, rå', 1.02)
            ('Tortillabrød, hvede',0.74), ('Peber, chili, konserves', 1.54),
            ]

Answer:
Røde linser: 1.78 kg CO2e / kg
Hakkede tomater: 1.26 kg CO2e / kg
Grøntsagsbouillon: 0.38 kg CO2e / kg (closest was chicken bouillon)
Tomatkoncentrat: 2.48 kg CO2e / kg (closest was tomato paste)
Citronsaft: 0.94 kg CO2e / kg (Closest was Lemon, raw)
Majstortillas: 0.74 kg CO2e / kg (Closest was Tortillabrød, hvede)
Stjernefrugt: ? (Not found in database)

Ingredients: {input}"""

EN_CO2_SQL_PROMPT = """Given a list of ingredients,
            extract the main ingredients from the list and create a syntactically correct {dialect} query to run,
            then look at the results of the query and return the answer.

Solve the task using the following steps:
- Query all ingredients in a single query.
- In the query, remove all non-ingredient words.
- Match the SQLResult to the list of ingredients based on preparation and type.
- Return the Answer in the following format: ''ingredient': X kg CO2e / kg'.
- If the ingredient is not found in the database, return '?'.

Use the following format:
Ingredients: "Ingredients here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:
{table_info}

Begin!

Ingredients:
150 g red lentils
1 can of chopped tomatoes
2 cubes of vegetable bouillon
1 tin of tomato concentrate (140 g)
1 tbsp. lemon juice
1. tbsp. chili powder
10 corn tortillas
1 starfruit

SQLQuery: SELECT Name, Total_kg_CO2_eq_kg FROM dk_co2_emission WHERE
          Name LIKE '%tomato%' OR
          Name LIKE '%lentil%' OR
          Name LIKE '%bouillion%' OR
          Name LIKE '%juice%' OR
          Name LIKE '%lemon%' OR
          Name LIKE '%chili%' OR
          Name LIKE '%tortilla%' OR
          Name LIKE '%starfruit%'

SQLResult: [('Tomato, ripe, raw, origin unknown', 0.7), ('Green lentils, dried', 1.78)
            ('Tomatojuice, canned', 1.26), ('Tomato, peeled, canned', 1.26)
            ('Tomato paste, concentrated', 2.48), ('Red lentils, dried', 1.78
            ('Ice, popsickle, lemonade', 1.15), ('Lemon, raw', 0.94
            ('Apple juice', 1.64),('Bouillon, chicken, prepared', 0.38)
            ('Bouillon, beef, prepared', 0.52), ('Pepper, hot chili, raw', 1.02)
            ('Tortilla bread, wheat',0.74),('Pepper, hot chili, canned', 1.54),
            ]

Answer:
Red lentils: 1.78 kg CO2e / kg
Chopped tomatoes: 1.26 kg CO2e / kg
Vegetable bouillon: 0.38 kg CO2e / kg (closest was chicken bouillon)
Tomato concentrate (140 g): 2.48 kg CO2e / kg (closest was tomato paste)
Lemon juice: 0.94 kg CO2e / kg (Closest was Lemon, raw)
Corn tortillas: 0.74 kg CO2e / kg (Closest was Tortilla bread, wheat)
Starfruit: ? (Not found in database)

Ingredients: {input}"""
