import json

from openai import OpenAI

from app.document_retriever import (
    retrieve_relevant_documentation
)


def diagnose_failure(failure):

    query = " ".join(
        [
            failure.get("endpoint", ""),
            failure.get("method", ""),
            str(failure.get("request", "")),
            str(failure.get("expected", "")),
            str(failure.get("actual", "")),
            str(failure.get("failure", ""))
        ]
    )

    relevant_documentation = (
        retrieve_relevant_documentation(
            query
        )
    )


    prompt = f"""
You are a senior travel technology UAT
and API integration analyst.

Analyze this UAT failure.

Rules:

- Do not invent facts.
- If the root cause is uncertain,
  say so.
- Clearly distinguish facts from hypotheses.
- Confidence must be exactly High,
  Medium, or Low.
- Evidence must only use information
  contained in the UAT failure or the
  supplied API documentation.
- Keep every field concise.
- Consider the context of travel API
  integration.
- API documentation is supporting
  evidence, not proof that a particular
  implementation is defective.
- Do not override the deterministic
  UAT result.

RELEVANT API DOCUMENTATION:

{relevant_documentation}

UAT FAILURE:

{json.dumps(failure, indent=2)}
"""


    client = OpenAI()

    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "uat_diagnosis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {

                        "root_cause": {
                            "type": "string"
                        },

                        "impact": {
                            "type": "string"
                        },

                        "recommendation": {
                            "type": "string"
                        },

                        "confidence": {
                            "type": "string",
                            "enum": [
                                "High",
                                "Medium",
                                "Low"
                            ]
                        },

                        "evidence": {
                            "type": "string"
                        }
                    },

                    "required": [
                        "root_cause",
                        "impact",
                        "recommendation",
                        "confidence",
                        "evidence"
                    ],

                    "additionalProperties": False
                }
            }
        }
    )


    return json.loads(
        response.output_text
    )

