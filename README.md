https://binance-docs.github.io/apidocs/futures/en/

## Architecture v2

<img src="./rig-arch.png"
     alt="rig architecture v2"
     style="height: 600px" />

## To Do
* offline protection for account admin - if failed orchestration retry until successful
* append buy, sell lines of df to csv 

## Notes
* python version 3.11
* python.analysis.typeCheckingMode basic - strict was painful
* pip install -r requirements.txt
* some patterns, techniques & adapted modules where extracted from https://github.com/freqtrade/freqtrade
* use to bypass seemly unsolvable typing issues: # type: ignore

