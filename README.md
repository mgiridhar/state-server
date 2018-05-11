# State Server!

This server tells us which state, if any, a point (or location) is in.
Some simplified geometries are included in states.json (so greatly simplified,
that some of the smaller ones disappear).

# Installation & Setup
This project uses python version 2.7
```
pip install shapely
./state-server &
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

## Notes

Given that file, it took one of us about an hour to implement something that
worked correctly. You're welcome to take it however far you want, but we're
expecting something along those lines.

And if there's anything special we have to do to run your program, just let us
know. A Makefile never hurt anyone.
