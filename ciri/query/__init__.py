prompt = \
"""
Question: Are there any mistakes in the above configuration file? Respond in a json format similar to the following:
{
    "error": true, // true or false
    "error_property": [], // list of property(ies) that has/have the error, or empty array if there's no error
    "reason": [] // list of strings explaining the error reason(s), or empty array if there's no error
}

Answer:
```json
"""