import json

from openai import OpenAI

from app.document_retriever import load_document



def generate_scenarios():

    documentation = load_document()

    prompt = f"""
You are a senior travel technology UAT analyst.

Generate executable UAT test scenarios for the API
described below.

API DOCUMENTATION:

{documentation}

IMPORTANT:

Every generated scenario must be executable directly
against the documented API.

Use concrete test values.

For this demo API, use these known test values where
appropriate:

- passenger_name: "Behram"
- valid fare: "ECONOMY"
- invalid fare: "INVALID"
- valid baggage: "20KG"
- invalid baggage: "INVALID"
- valid seat: "12A"
- invalid seat: "INVALID"
- valid search origin: "BOM"
- valid search destination: "DXB"
- no-flight destination: "XYZ"

Do NOT use placeholders such as:

<passenger name>
<available fare>
<generated PNR>
<origin airport code>

Do not invent values that are not supported by the
documentation or the known demo test values.

Generate positive and negative scenarios.

Cover:

- successful booking
- booking with baggage
- booking with seat
- missing passenger
- empty passenger
- invalid fare
- invalid baggage
- invalid seat
- successful flight search
- flight search with no results

Each scenario must contain:

id
scenario
category
priority
description
endpoint
method
request
expected

The request and expected fields must contain valid
JSON objects encoded as JSON strings.

IDs should start at AI-UAT-001.

--------------------------------------------------
EXPECTED RESPONSE RULES
--------------------------------------------------

IMPORTANT:

The "expected" value must be a FLAT JSON object.

IMPORTANT:
- Put documented response fields directly inside "expected".
- NEVER wrap expected response fields inside a "body" object.
- NEVER use "body" as a key inside "expected".
- Use documented fields such as "success", "booking_status",
  "pnr", "passenger_name", "fare", "error_code", and "message"
  directly at the top level.
- Keep "http_status" at the top level if it is specified.

Do not invent exact response values when the API
documentation does not define those values.

Use exact values only when the documentation or
known demo API behaviour explicitly defines them.

For dynamic response fields, use one of these
supported semantic assertions:

- "present"
- "array"
- "non-empty array"

These assertions mean:

"present"
The response field must exist and must not be null.

"array"
The response field must exist and must be a JSON array.

"non-empty array"
The response field must exist, must be a JSON array,
and must contain at least one item.

--------------------------------------------------
FLIGHT SEARCH RULES
--------------------------------------------------

For a successful flight search:

Request:

origin = "BOM"
destination = "DXB"

Expected response must include:

success = true
origin = "BOM"
destination = "DXB"

For the results field:

DO NOT use:

"results": []

DO NOT invent the exact flight list.

Use:

"results": "non-empty array"

The actual flight details are response data and should
not be hard-coded into the UAT expectation.

For a no-flight search:

Request:

origin = "BOM"
destination = "XYZ"

Expected response must include:

success = false
error_code = "NO_FLIGHTS"

The documentation requires a message field but does not
define a fixed message value.

Therefore use:

"message": "present"

Do NOT use:

"message": ""

Do NOT invent an exact message.

--------------------------------------------------
BOOKING RULES
--------------------------------------------------

For successful booking scenarios, validate the fields
whose values are directly determined by the request.

For example:

request:

{{
    "passenger_name": "Behram",
    "fare": "ECONOMY"
}}

expected:

{{
    "success": true,
    "booking_status": "CONFIRMED",
    "passenger_name": "Behram",
    "fare": "ECONOMY"
}}

Do not invent a PNR value.

If a response field is dynamic, use:

"present"

For example:

"pnr": "present"

For negative booking scenarios, validate the documented
error_code.

Do not require an exact error message unless the
documentation explicitly defines that exact message.

--------------------------------------------------
QUALITY RULE
--------------------------------------------------

Before producing each scenario, mentally verify:

1. Is the request supported by the API documentation?
2. Is the expected response supported by the documentation?
3. Am I inventing an exact response value?
4. If the value is dynamic, should I use a semantic assertion?
5. Could the expected response contradict the request?
6. Is this scenario actually testing the stated business
   condition?

The scenario must test the intended behaviour rather
than merely contain syntactically valid JSON.
"""

    client = OpenAI()

    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "uat_scenarios",
                "strict": True,
                "schema": {
                    "type": "object",

                    "properties": {

                        "scenarios": {
                            "type": "array",

                            "items": {
                                "type": "object",

                                "properties": {

                                    "id": {
                                        "type": "string"
                                    },

                                    "scenario": {
                                        "type": "string"
                                    },

                                    "category": {
                                        "type": "string"
                                    },

                                    "priority": {
                                        "type": "string",
                                        "enum": [
                                            "Critical",
                                            "High",
                                            "Medium",
                                            "Low"
                                        ]
                                    },

                                    "description": {
                                        "type": "string"
                                    },

                                    "endpoint": {
                                        "type": "string"
                                    },

                                    "method": {
                                        "type": "string",
                                        "enum": [
                                            "GET",
                                            "POST",
                                            "PUT",
                                            "DELETE"
                                        ]
                                    },

                                    "request": {
                                        "type": "string"
                                    },

                                    "expected": {
                                        "type": "string"
                                    }
                                },

                                "required": [
                                    "id",
                                    "scenario",
                                    "category",
                                    "priority",
                                    "description",
                                    "endpoint",
                                    "method",
                                    "request",
                                    "expected"
                                ],

                                "additionalProperties": False
                            }
                        }
                    },

                    "required": [
                        "scenarios"
                    ],

                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(
        response.output_text
    )

    for scenario in result["scenarios"]:

        scenario["request"] = json.loads(
            scenario["request"]
        )

        scenario["expected"] = json.loads(
            scenario["expected"]
        )

    return result