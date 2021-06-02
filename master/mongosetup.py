## Import dependencies
# Import external modules
import bson, pymongo
from .env import URI


## Setup MongoDB connection
CLIENT = pymongo.MongoClient(URI)
DATABASE_NAME = "studentsGateway"
DATABASE = CLIENT[DATABASE_NAME]
COLLECTION_NAMES = [
    # In decreasing levels of importance
    "students",
    "staff",
    "parents",
    "groups",  # Classes, Groups(Eg. Subjects) and Student-Parent
    "studentsGroup",
    "staffGroup",
    "forms",  # Announcements, forms, quizzes/polls
    "formsResponses",  # Responses to `forms`
    "grades",  # Grades to groups:students
    "appointments"  # Appointments (timer notifications, low priority)
]
COLLECTIONS = {k: DATABASE[k] for k in COLLECTION_NAMES}

'''
DATE_QUERY_KEYS = ["dubefore", "dubeforeincl", "duafter", "duafterincl", "duexact"]
DATE_MONGO_KEYS = ["$lt", "$lte", "$gt", "$gte", "$eq"]
DATE_KEYS_MAPPING = {DATE_QUERY_KEYS[i]: DATE_MONGO_KEYS[i] for i in range(5)}


def process_get_request(raw_query, hide_pass=True):
    # Turn the http request arguments into a dictionary
    query = dict(raw_query)
    # Make sure nobody can search by encryptedUserPass
    # by removing it entirely
    try:
        query.pop("encryptedUserPass")
    except:
        pass
    # Convert everything into int or float if possible
    for k, v in query.items():
        try:
            query[k] = int(v)
        except:
            pass
        try:
            query[k] = float(v)
        except:
            pass
    # Return query and whether to project encryptedUserPass
    # If hide_pass is true, encryptedUserPass will not be shown
    if hide_pass:
        return query, {"encryptedUserPass": 0}
    else:
        return query, {}


def process_use_regex(query, attributes):
    # Use regex for specified document attributes
    # Each query has {k: v}
    # Find all the `k` that have been specified to be used with regex
    # in the argument called `attributes`
    # and convert the corresponding `v` into a regex query
    # if k is found in the query dictionary
    #
    # normal searh returns exact
    # regex doesn't need to be exact
    for k in attributes:
        if k not in list(query.keys()):
            continue
        query[k] = {"$regex": query[k], "$options": "i"}
    return query


# Convert id to bson
def process_use_bson_objectid(query):
    # When someone uses `?id=<ObjectId>`
    # Convert argument to BSON.objectid.ObjectId
    # If `id` key not found then return original
    # Otherwise convert `id` to bson.objectid.ObjectId
    # and move to `_id`
    # and pop `id`
    try:
        query["_id"] = bson.objectid.ObjectId(query["id"])
        query.pop("id")
    except:
        pass
    finally:
        return query


def process_use_datetime(query, attributes=DATE_QUERY_KEYS):
    # Convert to datetime
    for k in attributes:
        if k not in list(query.keys()):
            continue
        # If cannot convert to datetime, remove query altogether
        try:
            query[k] = datetime.fromtimestamp(int(query[k]))
        except:
            query.pop(k)
    return query


def process_date_queries(querysets,
                         DATE_KEYS_MAPPING=DATE_KEYS_MAPPING,
                         DATE_QUERY_KEYS=DATE_QUERY_KEYS):
    # Package http date request args into dateUpdated key
    # with MongoDB`s comparison key words such as `$gte`
    query = {}
    for p in DATE_QUERY_KEYS:
        if p not in list(querysets.keys()):
            continue
        query[DATE_KEYS_MAPPING[p]] = querysets[p]
    return query


# Master query processor
def process_request(query, regex_attributes, DATE_QUERY_KEYS=DATE_QUERY_KEYS):
    # Convert the query with all the functions above
    query = process_use_datetime(query, attributes=DATE_QUERY_KEYS)
    query["dateUpdated"] = process_date_queries(query)
    if query["dateUpdated"] == {}:
        query.pop("dateUpdated")
    query = process_use_bson_objectid(query)
    query = process_use_regex(query, regex_attributes)
    query = process_get_request(query)
    return query
'''