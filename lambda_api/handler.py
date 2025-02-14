import json
from recipe_extractor import RecipeExtractor

def lambda_handler(event, context):
    """
    Main Lambda handler function
    """
    try:
        print("Received event:", event)
        query_params = event.get("queryStringParameters", {})
        url = query_params.get("url", "")
        if not url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "URL is required"})
            }
        extractor = RecipeExtractor()
        recipe = extractor.extract_from_url(url)

        response = {
            "statusCode": 200,
            "body": json.dumps({
                "url": url,
                "recipe": recipe,
            })
        }
        print(response)
        return response

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }

if __name__ == "__main__":
    print("Running handler")
    event = {
        "queryStringParameters": {
            "url": "https://sugarspunrun.com/best-cheesecake-recipe/"
        }
    }
    context = {}
    print(lambda_handler(event, context))
