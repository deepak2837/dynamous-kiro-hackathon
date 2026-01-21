"""
Database utilities for handling MongoDB ObjectId serialization
"""
from typing import Dict, List, Any, Union


def remove_object_id(document: Dict[str, Any]) -> Dict[str, Any]:
    """Remove MongoDB ObjectId from a single document"""
    if "_id" in document:
        del document["_id"]
    return document


def remove_object_ids(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove MongoDB ObjectId from a list of documents"""
    return [remove_object_id(doc) for doc in documents]


def clean_mongo_document(document: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Clean MongoDB document(s) by removing ObjectId fields"""
    if isinstance(document, list):
        return remove_object_ids(document)
    elif isinstance(document, dict):
        return remove_object_id(document)
    else:
        return document
