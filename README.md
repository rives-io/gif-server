# GIF-SERVER
An Flask server + redis that keeps GIFs generated from gameplays.

## RUN
``` shell
docker-compose up
```

## STOP
``` shell
docker-compose down
```

## ENDPOINTS

### POST /insert-gif
Receives a JSON payload containing the gameplay ID and the GIF to be stored.

Payload Format

``` json
{
    "gameplay_id": "0x...",
    "gif": "..."
}
```

### POST /gifs
Receives a JSON payload containing a list of gameplay ID and returns their GIFs.

Payload Format

``` json
[
    "1",
    "2",
    "3",
]
```
