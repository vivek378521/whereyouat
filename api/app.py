from flask import Flask, render_template, request
from opencage.geocoder import OpenCageGeocode, RateLimitExceededError, InvalidInputError
from dotenv import load_dotenv
import os
import wikipedia


load_dotenv()  # Load environment variables from .env file


def is_dict(value):
    return isinstance(value, dict)


app = Flask(__name__)
app.jinja_env.filters["is_dict"] = is_dict

opencage_api_key = os.getenv("OPENCAGE_API_KEY")
geocoder = OpenCageGeocode(opencage_api_key)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_location", methods=["POST"])
def get_location():
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]

    try:
        results = geocoder.reverse_geocode(float(latitude), float(longitude))
        if results and len(results):
            location_info = results[0]

            # Display the formatted address
            formatted_address = location_info.get("formatted", "")

            # Extract city and state_district information from the components
            city = location_info.get("components", {}).get("city", "")
            state_district = location_info.get("components", {}).get(
                "state_district", ""
            )

            # Use Wikipedia API to get a summary
            if state_district:
                fact_summary = wikipedia.summary(state_district, sentences=1)
            elif city:
                fact_summary = wikipedia.summary(city, sentences=1)
            else:
                fact_summary = "No relevant information available."

            return render_template(
                "index.html",
                formatted_address=formatted_address,
                location_name=city,
                fact_summary=fact_summary,
                location_info=location_info,
            )
    except RateLimitExceededError as ex:
        error_message = f"Rate Limit Exceeded: {ex}"
        return render_template("index.html", error_message=error_message)
    except InvalidInputError as ex:
        error_message = f"Invalid Input: {ex}"
        return render_template("index.html", error_message=error_message)
    except Exception as ex:
        error_message = f"Error: {ex}"
        return render_template("index.html", error_message=error_message)

    # Default return statement in case none of the conditions are met
    return render_template("index.html", error_message="Unexpected error occurred.")


if __name__ == "__main__":
    app.run(debug=True)
