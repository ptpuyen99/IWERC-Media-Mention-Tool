import os
import json
import requests
import boto3
import pandas as pd
from datetime import datetime

# AWS DynamoDB Details
DYNAMODB_TABLE_NAME = "MediaMentions"

# Initialize AWS Clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def lambda_handler(event, context):
    try:
        print("Fetching data from Google Search API...")

        # Google Search API request
        url = "https://customsearch.googleapis.com/customsearch/v1"
        params = {
            'key': "API KEY",
            'cx': "CX",
            'q': "Illinois Workforce and Education Research Collaborative (IWERC)",
            'num': 10,
            'excludeTerms': 'pdf'
        }

        response = requests.get(url, params=params)
        results = response.json()

        print("Processing search results...")

        # Prepare data for DynamoDB
        now = datetime.now()
        current_time = now.strftime('%Y-%m-%d')

        records = []
        for item in results.get('items', []):
            date = item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time', current_time)
            try:
                parsed_datetime = datetime.fromisoformat(date)
                formatted_date = parsed_datetime.strftime("%Y-%m-%d")
            except ValueError:
                formatted_date = current_time  # Default to today if no valid date

            record = {
                "Date": formatted_date,
                "Title": item.get('title', 'No title'),
                "Link": item.get('link', 'No link'),  # Primary Key
                "Snippet": item.get('snippet', 'No snippet')
            }

            records.append(record)

            # Insert into DynamoDB
            table.put_item(Item=record)

        print("Successfully stored in DynamoDB")
        
        return {"status": "success", "message": f"{len(records)} records uploaded to DynamoDB"}

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}
