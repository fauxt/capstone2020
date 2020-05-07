# Client Environment
* Each user is responsible to have a `.env` file in the root directory
* The `.env` file must contain the api key under the key `API_KEY`
    * `API_KEY=enter_your_api_key`
* The `.env` will also contain the client id under the key `CLIENT_ID`
    * If the client id is not in the `.env` file, the Client Manager will retrieve one from the server endpoint `/get_user_id` as a json response. The response will contain the id under the key `user_id`. See `Client Manager` documentation for more information of what it does.
    * `CLIENT_ID=client_id_goes_here`

# Client Manager
* Loads `.env` file into environment variables on instance creation.
* Calls `check_for_id` function on creation to set `client_id` if it was None.
* Contains the variables `api_key` and `client_id`.
* Class contains four functions:
    * `set_keys` sets the `api_key` and `client_id` variables from the environment variables without doing a load. This function is mainly for testing purposes. It is not practical to call this function without doing a load first to get the most up to date variables from the `.env` file.
    * `client_has_id` checks the `client_id` variable for a value. Returns True if the variable is not None (an id exists) or False if the variable is None (an id does not exist).
    * `request_id` makes the call to the server endpoint for a client id and stores it in the `client_id` variable. Returns the new `client_id` variable.
        * Can throw a `NoConnectionError` exception is the function is unable to make contact with the server.
    * `check_for_id` will check for a client id and set one. Makes a call to `check_has_id`.
        * If the `check_has_id` function returns True, it does nothing.
        * If the `check_has_id` function returns False, it calls the `request_id` function to get and save a client id to the `client_id` variable. The function will then proceed to append the new client id to the `.env` file in the correct format depicted above in Client Environment.