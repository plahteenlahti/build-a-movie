# API

## Address

The address for the APIs is `http://167.172.109.147/`

## Endpoints

- `http://167.172.109.147/predict-rating` : for IMDb rating prediction
- `http://167.172.109.147/predict-wlg` : for worldwide lifetime gross prediction

## Usage

Example:

`curl -X POST -H "Content-type: application/json" -d '{"genres":["News"],"people":["Tom Cruise"],"budget":20000}' http://167.172.109.147/predict-wlg`

## Returns

Both the endpoints return a JSON file formatted like this:
```
{
    "result": value
}
```
where `value` is the float result of the prediction.

## Code

The server is a Flask server with uWSGI and NGINX as http server. The code is in the `ids_server` folder; obv it doesn't work outside the environment, but if you want to get a look it's there (it's not such a complicated code tho).