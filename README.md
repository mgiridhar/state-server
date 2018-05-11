# State Server!

This server tells us which state, if any, a point (or location) is in The United States.
Some simplified geometries are included in states.json (so greatly simplified,
that some of the smaller ones disappear).

# Installation & Setup
This project uses python version 2.7

Clone the repository as below, and enter the 'state-server' directory,
```
git clone https://github.com/mgiridhar/state-server.git

cd state-server
```

Install shapely package using `pip`. Use `sudo` permission if needed.
```
pip install shapely
```

Start the server in the backgroud.
```
./state-server &
```

Do a POST request to the localhost with the required longitude and latitude arguments as content.
```
curl  -d "longitude=-77.036133&latitude=40.513799" http://localhost:8080/
```


## Behavior

```
  $ ./state-server &
  [1] 21507
  $ curl  -d "longitude=-77.036133&latitude=40.513799" http://localhost:8080/
  {"states": ["Pennsylvania"]}
  $
```

