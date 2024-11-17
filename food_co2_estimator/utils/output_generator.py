from typing import List

from food_co2_estimator.language.detector import Languages
from food_co2_estimator.output_parsers.co2_estimator import CO2Emissions
from food_co2_estimator.output_parsers.search_co2_estimator import CO2SearchResult
from food_co2_estimator.output_parsers.weight_estimator import WeightEstimates

# Avg. dinner emission per person method:
# 1. Get Food emission per person per year here: https://concito.dk/udgivelser/danmarks-globale-forbrugsudledninger which is 1.97 ton / per capita
# 2. Estimate emission per day per capita: 1.97 / 365.25 * 1000 = 5.39 kg CO2 / per capita
# 3. Calculate ratio of dinenr calorie amount wrt. to daily calorie intake:
#     Minimum case; 600 calories / 2500 calories = 0.24. Maximum case: 0.4. Avg. case = 700 / 2250 = 0.31
# 4. Assume dinner emission is equivalent to amount of calories to estimate avg. dinner emission.
#    5.39 * 0.24 = 1.69 kg CO2 per capita

MIN_DINNER_EMISSION_PER_CAPITA = 1.3
MAX_DINNER_EMISSION_PER_CAPITA = 2.2


def generate_output(
    weight_estimates: WeightEstimates,
    co2_emissions: CO2Emissions,
    search_results: List[CO2SearchResult],
    negligeble_threshold: float,
    number_of_persons: int | None,
    language: Languages = Languages.English,
) -> str:
    translations = {
        Languages.English: {
            "unable": "unable to estimate weight",
            "negligible": "weight on {} kg is negligible",
            "not_found": "CO2e per kg not found",
            "total": "Total CO2 emission",
            "persons": "Estimated number of persons",
            "emission_pr_person": "Emission pr. person",
            "avg_meal_emission_pr_person": "Avg. Danish dinner emission pr person",
            "method": "The calculation method per ingredient is",
            "legends": "Legends",
            "db": "(DB) - Data from SQL Database (https://denstoreklimadatabase.dk)",
            "search": "(Search) - Data obtained from search",
            "comments": "Comments",
            "for": "For",
        },
        Languages.Danish: {
            "unable": "kan ikke skønne vægt",
            "negligible": "vægt på {} kg er negligerbar",
            "not_found": "CO2e per kg ikke fundet",
            "total": "Samlet CO2-udslip",
            "persons": "Estimeret antal personer",
            "emission_pr_person": "Emission pr. person",
            "avg_meal_emission_pr_person": "Gennemsnitligt aftensmad udledning pr. person",
            "method": "Beregningsmetoden pr. ingrediens er",
            "legends": "Forklaring",
            "db": "(DB) - Data fra SQL Database (https://denstoreklimadatabase.dk)",
            "search": "(Søgning) - Data opnået fra søgning",
            "comments": "Kommentarer",
            "for": "For",
        },
    }

    trans = translations.get(language, translations[Languages.English])

    ingredients_output = []
    total_co2 = 0
    all_comments = []

    for weight_estimate in weight_estimates.weight_estimates:
        co2_data = next(
            (
                item
                for item in co2_emissions.emissions
                if item.ingredient == weight_estimate.ingredient
            ),
            None,
        )
        search_result = next(
            (
                item
                for item in search_results
                if item.ingredient == weight_estimate.ingredient
            ),
            None,
        )

        comments = {
            "Weight": weight_estimate.weight_calculation,
            "DB": co2_data.comment if co2_data else None,
            "Search": search_result.explanation if search_result else None,
        }

        all_comments.append(
            {"ingredient": weight_estimate.ingredient, "comments": comments}
        )

        if weight_estimate.weight_in_kg is None:
            ingredients_output.append(
                f"{weight_estimate.ingredient}: {trans['unable']}"
            )
            continue

        if weight_estimate.weight_in_kg <= negligeble_threshold:
            ingredients_output.append(
                f"{weight_estimate.ingredient}: {trans['negligible'].format(round(weight_estimate.weight_in_kg,3))}"
            )
            continue

        if co2_data and co2_data.co2_per_kg:
            co2_value = round(co2_data.co2_per_kg * weight_estimate.weight_in_kg, 2)
            ingredients_output.append(
                f"{weight_estimate.ingredient}: {round(weight_estimate.weight_in_kg, 2)} kg * {round(co2_data.co2_per_kg, 2)} kg CO2e / kg (DB) = {co2_value} kg CO2e"
            )
            total_co2 += co2_value

        elif search_result and search_result.result:
            co2_value = round(search_result.result * weight_estimate.weight_in_kg, 2)
            ingredients_output.append(
                f"{weight_estimate.ingredient}: {round(weight_estimate.weight_in_kg, 2)} kg * {round(search_result.result, 2)} kg CO2e / kg (Search) = {co2_value} kg CO2e"
            )
            total_co2 += co2_value

        else:
            ingredients_output.append(
                f"{weight_estimate.ingredient}: {trans['not_found']}"
            )
    if number_of_persons is not None:
        number_of_persons_text = f"\n{trans['persons']}: {number_of_persons}"
        emission_per_person_text = f"\n{trans['emission_pr_person']}: {round(total_co2/number_of_persons,1)} kg CO2e / pr. person"
    else:
        number_of_persons_text = ""
        emission_per_person_text = ""

    output = (
        "----------------------------------------"
        f"\n{trans['total']}: {round(total_co2,1)} kg CO2e"
        f"{number_of_persons_text}"
        f"{emission_per_person_text}"
        f"\n{trans['avg_meal_emission_pr_person']}: {MIN_DINNER_EMISSION_PER_CAPITA} - {MAX_DINNER_EMISSION_PER_CAPITA} kg CO2e / pr. person"
        "\n----------------------------------------"
        f"\n{trans['method']}: X kg * Y kg CO2e / kg = Z kg CO2e"
    )
    output += "\n" + "\n".join(ingredients_output)
    output += "\n----------------------------------------"

    # Legends
    output += f"\n\n{trans['legends']}:"
    output += f"\n{trans['db']}"
    output += f"\n{trans['search']}"

    # Append comments
    output += f"\n\n{trans['comments']}:"
    for comment in all_comments:
        ingredient = comment["ingredient"]
        output += f"\n{trans['for']} {ingredient}:"
        for key, value in comment["comments"].items():
            if value:
                output += f"\n- {key}: {value}"

    return output
