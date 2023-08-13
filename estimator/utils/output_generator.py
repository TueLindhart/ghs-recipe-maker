from typing import List

from prompt_templates.co2_search_prompts import CO2SearchResult
from prompt_templates.co2_sql_prompts import CO2Emissions
from prompt_templates.weight_est_prompts import WeightEstimates


def generate_output(
    weight_estimates: WeightEstimates,
    co2_emissions: CO2Emissions,
    search_results: List[CO2SearchResult],
    negligeble_threshold: float,
) -> str:
    ingredients_output = []
    total_co2 = 0
    all_comments = []

    for weight_estimate in weight_estimates.weight_estimates:
        # Find corresponding co2 emission data and search result
        co2_data = next((item for item in co2_emissions.emissions if item.ingredient == weight_estimate.ingredient), None)
        search_result = next((item for item in search_results if item.ingredient == weight_estimate.ingredient), None)

        # Separate comments for clarity
        comments = {"Weight": weight_estimate.weight_calculation, "DB": co2_data.comment if co2_data else None, "Search": search_result.explanation if search_result else None}

        all_comments.append({"ingredient": weight_estimate.ingredient, "comments": comments})

        if weight_estimate.weight_in_kg is None:
            ingredients_output.append(f"{weight_estimate.ingredient}: unable to estimate weight")
            continue

        if weight_estimate.weight_in_kg <= negligeble_threshold:
            ingredients_output.append(f"{weight_estimate.ingredient}: weight on {round(weight_estimate.weight_in_kg,3)} kg is negligible")
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
            ingredients_output.append(f"{weight_estimate.ingredient}: CO2e per kg ikke fundet")

    output = (
        "----------------------------------------"
        f"\nTotal CO2 emission: {round(total_co2,2)} kg CO2e"
        "\n----------------------------------------"
        "\nThe calculation method per ingredient is: X kg * Y kg CO2e / kg = Z kg CO2e"
    )
    output += "\n" + "\n".join(ingredients_output)
    output += "\n----------------------------------------"

    # Legends
    output += "\n\nLegends:"
    output += "\n(DB) - Data from SQL Database (https://denstoreklimadatabase.dk)"
    output += "\n(Search) - Data obtained from search"

    # Append comments
    output += "\n\nComments:"
    for comment in all_comments:
        ingredient = comment["ingredient"]
        output += f"\nFor {ingredient}:"
        for key, value in comment["comments"].items():
            if value:
                output += f"\n- {key}: {value}"

    return output
