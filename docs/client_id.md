## get\_user\_id

A GET request is invoked by the client to the server. This will return a JSON object with information containing a `user_id` number that the client will use to identify itself for every job it completes. 

As new clients connect to the server, each client will get a user_id in the form of `user#` with `#` being an incrementing integer for how many new clients have been assigned jobs by the server. 

Starting with `User1`, the user ids will be saved in a redis database for data permanence so the data is not lost if the server discontinues for any reason.

## JSON definition
A simple JSON object will be returned with only one field:

* `user_id`: A unique identifier of the client returning the result.

## Example return value:
```
{'user_id' = 'User123'}
```
