"""
DynamoDB helper functions for thread metadata management.
"""

from datetime import datetime
from typing import List, Dict, Optional
import boto3
from boto3.dynamodb.conditions import Key
from common_assets.config import dynamodb_table_name


def get_dynamodb_table():
    """
    Get DynamoDB table resource.

    Returns:
        DynamoDB Table resource
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_table_name)
    return table


def save_thread_metadata(user_id: str, thread_id: str, chat_mode: str, new_thread : bool) -> bool:
    """
    Save or update thread metadata in DynamoDB.
    If thread exists, only updates update_date.
    If thread is new, creates with created_date and update_date.

    Args:
        user_id: User identifier
        thread_id: Thread identifier
        chat_mode: Chat mode (default: "QnA")

    Returns:
        True if successful, False otherwise
    """
    try:
        table = get_dynamodb_table()
        current_time = datetime.now().isoformat()

        # Check if thread exists
        response = table.get_item(
            Key={
                'user_id': user_id,
                'thread_id': thread_id
            }
        )

        if 'Item' in response:
            ### Ideally new-thread should not be False here
            if new_thread:
                print('New Thread = True sent by Front-end, but backend thread_id already existed')
            # Thread exists - only update update_date
            table.update_item(
                Key={
                    'user_id': user_id,
                    'thread_id': thread_id
                },
                UpdateExpression='SET update_date = :update_date',
                ExpressionAttributeValues={
                    ':update_date': current_time
                }
            )
        else:
            if not new_thread:
                print('New Thread = False sent by Front-end, but backend thread_id did not exis')

            # New thread - create with all fields
            table.put_item(
                Item={
                    'user_id': user_id,
                    'thread_id': thread_id,
                    'chat_mode': chat_mode,
                    'created_date': current_time,
                    'update_date': current_time
                }
            )
        return True
    except Exception as e:
        print(f"Error saving thread metadata: {e}")
        return False


def get_user_threads(user_id: str) -> List[str]:
    """
    Get all thread IDs for a specific user from DynamoDB.

    Args:
        user_id: User identifier

    Returns:
        List of thread IDs for the user
    """
    try:
        table = get_dynamodb_table()
        response = table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )

        thread_ids = [item['thread_id'] for item in response.get('Items', [])]
        return thread_ids
    except Exception as e:
        print(f"Error getting user threads: {e}")
        return []


def get_thread_details(user_id: str,thread_id:str):
    try:
        table = get_dynamodb_table()
        response = table.get_item(
            Key={
                'user_id':user_id,
                'thread_id': thread_id
            }
        )
        if (not 'Item' in response):
            return False
        else:
            return response['Item']
    except:
        return False



def delete_thread_metadata(user_id: str, thread_id: str) -> bool:
    """
    Delete a single thread's metadata from DynamoDB.

    Args:
        user_id: User identifier
        thread_id: Thread identifier

    Returns:
        True if successful, False otherwise
    """
    try:
        table = get_dynamodb_table()
        table.delete_item(
            Key={
                'user_id': user_id,
                'thread_id': thread_id
            }
        )
        return True
    except Exception as e:
        print(f"Error deleting thread metadata: {e}")
        return False


def delete_user_threads(user_id: str) -> bool:
    """
    Delete all threads for a specific user from DynamoDB.

    Args:
        user_id: User identifier

    Returns:
        True if all deletions successful, False otherwise
    """
    try:
        thread_ids = get_user_threads(user_id)

        for thread_id in thread_ids:
            delete_thread_metadata(user_id, thread_id)

        return True
    except Exception as e:
        print(f"Error deleting user threads: {e}")
        return False
